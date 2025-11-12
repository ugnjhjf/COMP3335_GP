import json
import urllib.parse
import traceback
from http.server import BaseHTTPRequestHandler

from communicator import json_response, read_json
from privilege_controller import (
    parse_bearer_role,
    ROLE_TABLES,
    RolePrivileges,
    FKLink,
    buildRangeFilter,
    retrieveReadableColumns,
)
from db_query import db_query, db_execute, getTableColumns, checkPrimaryKey, checkUpdatableColumns
from logger import logDataUpdate
from auth import authenticate_user, create_session, validate_session, logout
from encryption import (
    getEncryptedColumns,
    buildSelectDecryptExpr,
    getEncryptionKey,
)


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

                role_privs = RolePrivileges.get(auth["role"], {})
                tables = ROLE_TABLES.get(auth["role"], [])

                tableColumns = {}
                for table in tables:
                    columns_info = getTableColumns(table)
                    table_priv = role_privs.get(table, {})
                    allowed_columns = retrieveReadableColumns(
                        table_priv, [col["Field"] for col in columns_info]
                    )

                    # keep original structure but drop disallowed columns
                    filtered = [col for col in columns_info if col["Field"] in allowed_columns]
                    tableColumns[table] = filtered

                rolePrivileges = role_privs  # keep original structure for client if needed
                return json_response(
                    self,
                    200,
                    {"tables": tables, "tableColumns": tableColumns, "rolePrivileges": rolePrivileges},
                )

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
                data = read_json(self) or {}
                email = data.get("email", "").strip()
                password = data.get("password", "")

                if not email or not password:
                    return json_response(self, 400, {"ok": False, "error": "Email and password required"})

                # Authenticate user
                user_info = authenticate_user(email, password)

                if user_info:
                    # Create session
                    token = create_session(user_info)
                    return json_response(self, 200, {
                        "ok": True,
                        "token": token,
                        "user": {
                            "id": user_info["user_id"],
                            "role": user_info["role"],
                            "name": user_info["name"],
                            "user_type": user_info.get("user_type", "")
                        }
                    })
                else:
                    return json_response(self, 401, {"ok": False, "error": "Invalid email or password"})

            elif path == "/auth/logout":
                auth_header = self.headers.get("Authorization", "")
                token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
                if logout(token):
                    return json_response(self, 200, {"ok": True, "message": "Logged out successfully"})
                else:
                    return json_response(self, 400, {"ok": False, "error": "Invalid token"})
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
                limit = max(1, min(limit, 500))
                offset = max(0, offset)

                if table not in ROLE_TABLES.get(auth["role"], []):
                    return json_response(self, 403, {"error": "Forbidden"})

                columnData = getTableColumns(table)
                table_priv = RolePrivileges.get(auth["role"], {}).get(table, {})
                allowed_columns = retrieveReadableColumns(table_priv, [col["Field"] for col in columnData])
                if not allowed_columns:
                    return json_response(self, 403, {"error": "Forbidden"})

                table_encrypted_columns = getEncryptedColumns(table)

                tableCols = []
                tableColsMap = {}
                for c in columnData:
                    colName = c.get("Field")
                    if colName in allowed_columns:
                        tableCols.append(colName)
                        tableColsMap[colName.lower()] = colName

                if not tableCols:
                    return json_response(
                        self,
                        403,
                        {"error": "No readable columns configured for this table"},
                    )

                def checkColumn(name):
                    actual = tableColsMap.get(str(name).lower())
                    if actual:
                        return f"{currentTableName}.`{actual}`", actual
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
                joins = []
                joinIdx = 1
                whereClauses = []
                select_params = []
                where_params = []

                tableFks = FKLink.get(table, {})
                encryption_key_value = None

                for col in tableCols:
                    if col in table_encrypted_columns:
                        if encryption_key_value is None:
                            encryption_key_value = getEncryptionKey()
                        decrypt_expr = buildSelectDecryptExpr(table, col, currentTableName)
                        queryingColumns.append(f"{decrypt_expr} AS `{col}`")
                        select_params.append(encryption_key_value)
                    elif col in tableFks.keys():
                        queryingColumns.append(f"{currentTableName}.`{col}` AS `{col}`")

                        joinTableName = f"j{joinIdx}"
                        joins.append(
                            f"LEFT JOIN `{tableFks[col].get('table')}` {joinTableName} "
                            f"ON {currentTableName}.`{col}` = {joinTableName}.`{tableFks[col].get('pk')}`"
                        )
                        joinIdx += 1

                        corr_sql = tableFks[col].get("corrNameSql")
                        corr_alias = tableFks[col].get("corrName")
                        if corr_sql and corr_alias:
                            queryingColumns.append(
                                f"{corr_sql.replace('j.', f'{joinTableName}.')} AS `{corr_alias}`"
                            )
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
                    where_params.extend(rangeParams or [])

                for f in (filters or []):
                    targetColumn = f.get("column")
                    operator = str(f.get("operator") or f.get("op") or "").lower()
                    val = f.get("value", None)
                    if not targetColumn or operator not in OP:
                        continue
                    try:
                        col, actual_col = checkColumn(targetColumn)
                    except ValueError:
                        continue

                    if actual_col in table_encrypted_columns:
                        return json_response(
                            self,
                            400,
                            {"error": f"Filtering on encrypted column '{actual_col}' is not supported"},
                        )

                    tok = OP[operator]
                    if operator in {"eq", "ne", "gt", "lt", "gte", "lte", "like"}:
                        if val is None:
                            continue
                        whereClauses.append(f"{col} {tok} %s")
                        where_params.append(val)
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
                        where_params.extend(valInstance)
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
                        where_params.extend(valInstance)
                    elif operator == "is_null":
                        whereClauses.append(f"{col} IS NULL")
                    elif operator == "is_not_null":
                        whereClauses.append(f"{col} IS NOT NULL")

                if whereClauses:
                    sqlComponents.append("WHERE " + " AND ".join(whereClauses))

                orderClauses = []
                for o in (orders or []):
                    targetColumn = o.get("column")
                    if not targetColumn:
                        continue
                    try:
                        col, actual_col = checkColumn(targetColumn)
                    except ValueError:
                        continue

                    if actual_col in table_encrypted_columns:
                        return json_response(
                            self,
                            400,
                            {"error": f"Ordering on encrypted column '{actual_col}' is not supported"},
                        )

                    direction = (o.get("direction") or "").upper()
                    if direction not in ("ASC", "DESC"):
                        continue
                    orderClauses.append(f"{col} {direction}")
                if orderClauses:
                    sqlComponents.append("ORDER BY " + ", ".join(orderClauses))

                sqlComponents.append(f"LIMIT {limit} OFFSET {offset}")

                sql = " ".join(sqlComponents)

                final_params = select_params + where_params
                results = db_query(sql, final_params)
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

                # check if the table is allowed for the role
                if table not in ROLE_TABLES.get(auth["role"], []):
                    return json_response(self, 403, {"error": "Forbidden"})

                columnData = getTableColumns(table)
                if not checkPrimaryKey(columnData, key):
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})

                if not checkUpdatableColumns(rolePrivileges.get(table, {}).get("update", []), updateValues):
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})

                table_encrypted_columns = getEncryptedColumns(table)
                currentTableName = "target"
                rangeJoins, rangeWhere, rangeParams = buildRangeFilter(auth, table, currentTableName)

                setColumnSql = []
                params = []
                encryption_key_value = None

                for colName, colVal in updateValues.items():
                    if colName in table_encrypted_columns:
                        if encryption_key_value is None:
                            encryption_key_value = getEncryptionKey()
                        setColumnSql.append(f"{currentTableName}.`{colName}` = AES_ENCRYPT(%s, %s)")
                        params.append(colVal)
                        params.append(encryption_key_value)
                    else:
                        setColumnSql.append(f"{currentTableName}.`{colName}` = %s")
                        params.append(colVal)

                if not setColumnSql:
                    return json_response(self, 400, {"ok": False, "error": "No columns to update"})

                primaryKey = next(iter(key))

                parts = [f"UPDATE `{table}` {currentTableName}"]
                if rangeJoins:
                    parts.append(" ".join(rangeJoins))

                parts.append(f"SET {', '.join(setColumnSql)}")

                where_parts = [f"{currentTableName}.`{primaryKey}` = %s"]
                params.append(key[primaryKey])

                if rangeWhere:
                    where_parts.append(rangeWhere)
                    params.extend(rangeParams or [])

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
                    params.extend(rangeParams or [])

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
                insertValues = data.get("insertValues", {})

                # check if the table is allowed for the role
                if table not in ROLE_TABLES.get(auth["role"], []):
                    return json_response(self, 403, {"error": "Forbidden"})

                allowed_insert_columns = rolePrivileges.get(table, {}).get("insert", [])
                if set(insertValues.keys()) != set(allowed_insert_columns):
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})

                ordered_columns = allowed_insert_columns
                table_encrypted_columns = getEncryptedColumns(table)

                columns_clause = []
                value_fragments = []
                params = []
                encryption_key_value = None

                for col in ordered_columns:
                    columns_clause.append(f"`{col}`")
                    val = insertValues[col]
                    if col in table_encrypted_columns:
                        if encryption_key_value is None:
                            encryption_key_value = getEncryptionKey()
                        value_fragments.append("AES_ENCRYPT(%s, %s)")
                        params.append(val)
                        params.append(encryption_key_value)
                    else:
                        value_fragments.append("%s")
                        params.append(val)

                columns_str = ', '.join(columns_clause)
                placeholders = ', '.join(value_fragments)

                sql = f"INSERT INTO `{table}` ({columns_str}) VALUES ({placeholders})"

                logDataUpdate(auth["personId"], auth["role"], sql)

                try:
                    db_execute(sql, params)
                    return json_response(self, 200, {"ok": True, "insert": ordered_columns})
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