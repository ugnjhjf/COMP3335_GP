#!/usr/bin/env python3
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import traceback
import pymysql

# =========================
# Database configuration
# =========================
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'supersecurepassword',
    'database': 'ComputingU',
    'charset': 'utf8mb4'
}

def get_db_connection():
    return pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

# =========================
# Simple auth and role logic
# =========================
VALID_ROLES = {"aro", "student", "guardian", "dro"}

# Mock role-table visibility (adjust to your schema)
ROLE_TABLES = {
    "student": ["students", "grades", "disciplinary_records"],
    "guardian": ["guardians", "grades", "disciplinary_records"],
    "aro": ["grades"],
    "dro": ["disciplinary_records"],
}

RolePrivileges = {
    "student": {
        "students": {
            "read": True, 
            "range": "self",
            "insert": [], # no insert allowed
            "update": ["last_name", "first_name", "gender", "Id_No", "address", "phone", "email", "guardian_relation"],
            "delete": False
        },
        "grades": {
            "read": True, 
            "range": "self",
            "insert": [], # no insert allowed
            "update": [], # no update allowed
            "delete": False
        },
        "disciplinary_records": {
            "read": True, 
            "range": "self",
            "insert": [], # no insert allowed
            "update": [], # no update allowed
            "delete": False
        }
    },
    "guardian": {
        "guardians": {
            "read": True, 
            "range": "self",
            "insert": [], # no insert allowed
            "update": ["last_name","first_name","email","phone"],
            "delete": False
        },
        "grades": {
            "read": True, 
            "range": "self",
            "insert": False,
            "update": [], # no update allowed
            "delete": False
        },
        "disciplinary_records": {
            "read": True, 
            "range": "self",
            "insert": [], # no insert allowed
            "update": [], # no update allowed
            "delete": False
        }
    },
    "aro": {
        "grades": {
            "read": True, 
            "range": "All",
            "insert": ['StuID', 'CID', 'term', 'grade', 'comments'],
            "update": ["grade", "term", "comments"],
            "delete": True
        },
    },
    "dro": {
        "disciplinary_records": {
            "read": True, 
            "range": "All",
            "insert": ['StuID', 'date', 'StfID', 'descriptions'],
            "update": ["date", "description"],
            "delete": True
        },
    },
}

FKLink = {
    "students": {
        "GuaID": {
            "table": "guardians",
            "pk": "GuaID",
            "corrNameSql": "CONCAT(j.`first_name`, ' ', j.`last_name`)",
            "corrName": "Guardian name"
        }
    },
    "grades": {
        "StuID": {
            "table": "students",
            "pk": "StuID",
            "corrNameSql": "CONCAT(j.`first_name`, ' ', j.`last_name`)",
            "corrName": "Student name"
        },
        "CID": {
            "table": "courses",
            "pk": "CID",
            "corrNameSql": "j.`course_name`",
            "corrName": "Course Name"
        }
    },
    "disciplinary_records": {
        "StuID": {
            "table": "students",
            "pk": "StuID",
            "corrNameSql": "CONCAT(j.`first_name`, ' ', j.`last_name`)",
            "corrName": "Student Name"
        },
        "StfID": {
            "table": "staffs",
            "pk": "StfID",
            "corrNameSql": "CONCAT(j.`first_name`, ' ', j.`last_name`)",
            "corrName": "Staff Name"
        }
    }
}

def parse_bearer_role(headers):
    role_header = headers.get("X-User-Role")
    if not role_header:
        return None
    role = role_header.lower()
    personId = headers.get("X-User-ID")
    if role in VALID_ROLES:
        return {"role": role, "personId": personId}
    return None

def json_response(handler, status, data, headers=None):
    body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    # CORS for testing
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-User-Role, X-User-ID")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    if headers:
        for k, v in headers.items():
            handler.send_header(k, v)
    handler.end_headers()
    handler.wfile.write(body)

def text_response(handler, status, text, content_type="text/plain; charset=utf-8"):
    body = text.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-User-Role, X-User-ID")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.end_headers()
    handler.wfile.write(body)

def read_json(handler):
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length == 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return {}

def db_query(sql, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
    finally:
        conn.close()

def db_execute(sql, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.rowcount
    finally:
        conn.close()

def getTableColumns(table_name):
    # Returns a list of column dicts for the given table
    rows = db_query(f"SHOW COLUMNS FROM `{table_name}`")
    return rows

def checkPrimaryKey(columnData, keyPair):
    if not keyPair or not columnData:
        return False
    for col in columnData:
        if col.get("Key") == "PRI":
            keyName = col.get("Field")
            if keyName not in keyPair.keys():
                return False
    return True

def checkUpdatableColumns(updatableColumnList, updateValues):
    if not updateValues or not updatableColumnList:
        return False
    for colName in list(updateValues.keys()):
        if colName not in updatableColumnList:
            return False
    return True

def buildRangeFilter(auth, table_name, currentTableName="target"):
    role = auth["role"]
    personId = auth.get("personId")
    joinSql = []
    whereSql = ""
    params = []

    role_priv = RolePrivileges.get(role, {})
    table_priv = role_priv.get(table_name)
    if table_priv is None:
        return [], "", []

    rng = (table_priv.get("range") or "").lower()

    if rng == "all":
        return [], "", []

    def restrict_eq(col, val):
        return f"{currentTableName}.`{col}` = %s", [val]

    def join_and_restrict_student_guardian(stuId_col="StuID", guaId_col="GuaID"):
        j = "s_guard"
        joinSql.append(
            f"INNER JOIN `students` {j} ON {currentTableName}.`{stuId_col}` = {j}.`StuID`"
        )
        return f"{j}.`{guaId_col}` = %s", [personId]

    if role == "student":
        if rng == "self":
            # Student can only see their own rows
            if table_name in ("students", "grades", "disciplinary_records"):
                whereSql, params = restrict_eq("StuID", personId)
    elif role == "guardian":
        if rng == "self" and table_name == "guardians":
            whereSql, params = restrict_eq("GuaID", personId)
        elif rng == "children" and table_name in ("grades", "disciplinary_records"):
            whereSql, params = join_and_restrict_student_guardian()

    return joinSql, whereSql, params

def logDataUpdate(user_id, role, sql_text):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO sql_change_log (user_id, user_role, sql_text)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, role, sql_text)
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

def test_db_connection():
    """测试数据库连接是否成功"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        conn.close()
        return True, "数据库连接成功"
    except Exception as e:
        return False, f"数据库连接失败: {str(e)}"

def run(host="127.0.0.1", port=8000):
    # 测试数据库连接
    print("正在测试数据库连接...")
    success, message = test_db_connection()
    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
        print("警告: 服务器将继续启动，但数据库操作可能会失败")
    
    httpd = HTTPServer((host, port), SimpleAPIServer)
    print(f"Serving on http://{host}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()