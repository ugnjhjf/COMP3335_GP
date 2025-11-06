#!/usr/bin/env python3
import json
import urllib.parse
import traceback
from http.server import BaseHTTPRequestHandler

from communicator import json_response, read_json
from privilege_controller import (
    parse_bearer_role, ROLE_TABLES, RolePrivileges, FKLink, buildRangeFilter
)
from db_query import db_query, db_execute, getTableColumns, checkPrimaryKey, checkUpdatableColumns
from logger import logDataUpdate

class SimpleAPIServer(BaseHTTPRequestHandler):
    server_version = "SimpleAPIServer/0.1"

    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-User-Role, X-User-ID")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        try:
            url = urllib.parse.urlparse(self.path)
            path = url.path
            self.log_message(f"GET {path}")
            
            if path == "/" or path == "":
                return json_response(self, 200, {
                    "message": "University Data API Server",
                    "version": "1.0",
                    "endpoints": {
                        "GET": ["/retrieveTablesColumns"],
                        "POST": ["/auth/login", "/performQuery", "/data/update", "/data/delete", "/data/insert"]
                    }
                })
            
            if path == "/retrieveTablesColumns":
                auth = parse_bearer_role(self.headers)
                if not auth:
                    return json_response(self, 401, {"error": "Unauthorized"})
                
                tables = ROLE_TABLES.get(auth["role"], [])
                
                tableColumns = {}
                for table in tables:
                    tableColumns[table] = getTableColumns(table)

                roleRrivileges = RolePrivileges.get(auth["role"], {})
                return json_response(self, 200, {"tables": tables, "tableColumns": tableColumns, "rolePrivileges": roleRrivileges})

            return json_response(self, 404, {"error": "Not found"})
        except Exception as e:
            traceback.print_exc()
            return json_response(self, 500, {"error": "Server error", "detail": str(e)})

    def do_POST(self):
        try:
            url = urllib.parse.urlparse(self.path)
            path = url.path
            self.log_message(f"POST {path}")

            if path == "/auth/login":
                # implement later
                pass
            elif path == "/performQuery":
                auth = parse_bearer_role(self.headers)
                if not auth:
                    return json_response(self, 401, {"error": "Unauthorized"})

                data = read_json(self) or {}
                table = str(data.get("currentTable") or "")
                filters = data.get("filters", [])
                orders = data.get("orders", [])
                limit = int(data.get("limit", 100))
                offset = int(data.get("offset", 0))
                limit = max(1, min(limit, 500))   # cap
                offset = max(0, offset)

                # check if the table is allowed for the role
                if table not in ROLE_TABLES.get(auth["role"], []):
                    return json_response(self, 403, {"error": "Forbidden"})

                # check if the table contain the columns
                columnData = getTableColumns(table)
                tableCols = []
                for c in columnData:
                    tableCols.append(c.get("Field"))

                def checkColumn(name):
                    if name in tableCols:
                        return f"{currentTableName}.`{name}`"
                    raise ValueError("Invalid column")

                OP = {
                    "eq": "=",
                    "ne": "!=",
                    "gt": ">",
                    "lt": "<",
                    "gte": ">=",
                    "lte": "<=",
                    "like": "LIKE",
                    "in": "IN",
                    "between": "BETWEEN",
                    "is_null": "IS NULL",
                    "is_not_null": "IS NOT NULL",
                }

                currentTableName = "target"
                queryingColumns = []
                queryingColumnsStr = ""
                joins = []
                joinIdx = 1
                whereClauses = []
                setColumnSql = []
                params = []

                tableFks = FKLink.get(table, {})

                for col in tableCols:
                    if col in tableFks.keys():
                        queryingColumns.append(f"{currentTableName}.`{col}` AS `{col}`")
                        
                        joinTableName = f"j{joinIdx}"
                        joins.append(f"LEFT JOIN `{tableFks[col].get('table')}` {joinTableName} ON {currentTableName}.`{col}` = {joinTableName}.`{tableFks[col].get('pk')}`")
                        joinIdx += 1

                        queryingColumns.append(f"{tableFks[col].get('corrNameSql').replace('j.', f'{joinTableName}.')} AS `{tableFks[col].get('corrName')}`")
                    else:
                        queryingColumns.append(f"{currentTableName}.`{col}` AS `{col}`")

                rangeJoins, rangeWhere, rangeParams = buildRangeFilter(auth, table, currentTableName)

                queryingColumnsStr = ', '.join(queryingColumns)
                sqlComponents = [f"SELECT {queryingColumnsStr} FROM `{table}` {currentTableName}"]

                if rangeJoins:
                    sqlComponents.extend(rangeJoins)

                if joins:
                    sqlComponents.extend(joins)

                def verifyList(valInstance):
                    if isinstance(valInstance, list):
                        if all(isinstance(i, (str, int, float)) for i in valInstance):
                            return True
                        else:
                            return False
                    else:
                        return False

                if rangeWhere:
                    whereClauses.append(rangeWhere)
                    params.extend(rangeParams)

                for f in (filters or []):
                    targetColumn = f.get("column")
                    operator = str(f.get("operator") or f.get("op") or "").lower()
                    val = f.get("value", None)
                    if not targetColumn or operator not in OP:
                        continue
                    try:
                        col = checkColumn(targetColumn)
                    except ValueError:
                        continue

                    tok = OP[operator]
                    if operator in {"eq", "ne", "gt", "lt", "gte", "lte", "like"}:
                        if val is None:
                            continue
                        whereClauses.append(f"{col} {tok} %s")
                        params.append(val)
                    elif operator == "in":
                        if isinstance(val, str):
                            try:
                                valInstance = json.loads(val)
                            except Exception:
                                continue
                        else:
                            valInstance = val
                        if not verifyList(valInstance) or len(valInstance) != 2:
                            continue
                        placeholders = ", ".join(["%s"] * len(valInstance))
                        whereClauses.append(f"{col} IN ({placeholders})")
                        params.extend(valInstance)
                    elif operator == "between":
                        if isinstance(val, str):
                            try:
                                valInstance = json.loads(val)
                            except Exception:
                                continue
                        else:
                            valInstance = val
                        if not verifyList(valInstance) or len(valInstance) != 2:
                            continue
                        whereClauses.append(f"{col} BETWEEN %s AND %s")
                        params.extend(valInstance)
                    elif operator == "is_null":
                        whereClauses.append(f"{col} IS NULL")
                    elif operator == "is_not_null":
                        whereClauses.append(f"{col} IS NOT NULL")

                if whereClauses:
                    sqlComponents.append("WHERE " + " AND ".join(whereClauses))

                orderClauses = []
                for o in (orders or {}):
                    targetColumn = o.get("column")
                    if not targetColumn:
                        continue
                    try:
                        col = checkColumn(targetColumn)
                    except ValueError:
                        continue
                    direction = (o.get("direction")).upper()
                    if direction not in ("ASC", "DESC"):
                        continue
                    orderClauses.append(f"{col} {direction}")
                if orderClauses:
                    sqlComponents.append("ORDER BY " + ", ".join(orderClauses))

                sql = " ".join(sqlComponents)

                results = db_query(sql, params)
                return json_response(self, 200, {"results": results})
            elif path == "/data/update":
                auth = parse_bearer_role(self.headers)
                if not auth:
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})
                
                rolePrivileges = RolePrivileges.get(auth["role"], {})
                data = read_json(self) or {}
                table = str(data.get("table") or "")
                key = data.get("key", {})
                updateValues = data.get("updateValues", {})

                setColumnSql = []
                params = []

                 # check if the table is allowed for the role
                if table not in ROLE_TABLES.get(auth["role"], []):
                    return json_response(self, 403, {"error": "Forbidden"})
                
                columnData = getTableColumns(table)
                if not checkPrimaryKey(columnData, key):
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})
                
                if not checkUpdatableColumns(rolePrivileges.get(table, {}).get("update", []), updateValues):
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})
                
                currentTableName = "target"
                rangeJoins, rangeWhere, rangeParams = buildRangeFilter(auth, table, currentTableName)

                for colName, colVal in updateValues.items():
                    setColumnSql.append(f"{currentTableName}.`{colName}` = %s")
                    params.append(colVal)

                primaryKey = next(iter(key))

                parts = [f"UPDATE `{table}` {currentTableName}"]
                if rangeJoins:
                    parts.append(" ".join(rangeJoins))

                parts.append(f"SET {', '.join(setColumnSql)}")

                where_parts = [f"{currentTableName}.`{primaryKey}` = %s"]
                params.append(key[primaryKey])

                if rangeWhere:
                    where_parts.append(rangeWhere)
                    params.extend(rangeParams)

                sql = " ".join(parts) + " WHERE " + " AND ".join(where_parts)

                logDataUpdate(auth["personId"], auth["role"], sql)

                try:
                    db_execute(sql, params)
                    return json_response(self, 200, {"ok": True, "updated": updateValues})
                except Exception as e:
                    traceback.print_exc()
                    return json_response(self, 500, {"ok": False, "error": "Server error", "detail": str(e)})
            elif path == "/data/delete":
                auth = parse_bearer_role(self.headers)
                if not auth:
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})
                
                rolePrivileges = RolePrivileges.get(auth["role"], {})
                data = read_json(self) or {}
                table = str(data.get("table") or "")
                key = data.get("key", {})

                 # check if the table is allowed for the role
                if table not in ROLE_TABLES.get(auth["role"], []):
                    return json_response(self, 403, {"error": "Forbidden"})
                
                columnData = getTableColumns(table)
                if not checkPrimaryKey(columnData, key):
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})
                
                currentTableName = "target"
                rangeJoins, rangeWhere, rangeParams = buildRangeFilter(auth, table, currentTableName)
                
                params = []
                primaryKey = next(iter(key))

                parts = [f"DELETE {currentTableName} FROM `{table}` {currentTableName}"]
                if rangeJoins:
                    parts.append(" ".join(rangeJoins))

                where_parts = [f"{currentTableName}.`{primaryKey}` = %s"]
                params.append(key[primaryKey])

                if rangeWhere:
                    where_parts.append(rangeWhere)
                    params.extend(rangeParams)

                sql = " ".join(parts) + " WHERE " + " AND ".join(where_parts)

                logDataUpdate(auth["personId"], auth["role"], sql)

                try:
                    db_execute(sql, params)
                    return json_response(self, 200, {"ok": True, "deleted": key})
                except Exception as e:
                    traceback.print_exc()
                    return json_response(self, 500, {"ok": False, "error": "Server error", "detail": str(e)})
            elif path == "/data/insert":
                auth = parse_bearer_role(self.headers)
                if not auth:
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})
                
                rolePrivileges = RolePrivileges.get(auth["role"], {})
                data = read_json(self) or {}
                table = str(data.get("table") or "")
                updateValues = data.get("insertValues", {})
                params = []

                 # check if the table is allowed for the role
                if table not in ROLE_TABLES.get(auth["role"], []):
                    return json_response(self, 403, {"error": "Forbidden"})
                
                columnData = getTableColumns(table)
                print(set(updateValues.keys()))
                print(set(RolePrivileges.get(auth["role"], {}).get(table, {}).get("insert", [])))
                if (set(updateValues.keys()) != set(RolePrivileges.get(auth["role"], {}).get(table, {}).get("insert", []))):
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})
                
                updateValueColumns = list(updateValues.keys())
                placeholders = ', '.join(['%s'] * len(updateValueColumns))
                ColumnsStr = ', '.join(f"`{c}`" for c in updateValueColumns)

                sql = f"INSERT INTO `{table}` ({ColumnsStr}) VALUES ({placeholders})"
                params = [updateValues[c] for c in updateValueColumns]

                logDataUpdate(auth["personId"], auth["role"], sql)

                try:
                    db_execute(sql, params)
                    return json_response(self, 200, {"ok": True, "insert": updateValueColumns})
                except Exception as e:
                    traceback.print_exc()
                    return json_response(self, 500, {"ok": False, "error": "Server error", "detail": str(e)})
                
            return json_response(self, 404, {"error": "Not found"})
        except Exception as e:
            traceback.print_exc()
            return json_response(self, 500, {"error": "Server error", "detail": str(e)})

    def log_message(self, format, *args):
        print("%s - - [%s] %s" % (self.address_string(),
            self.log_date_time_string(),
            format % args))

