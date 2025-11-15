import json
import urllib.parse
import traceback
from http.server import BaseHTTPRequestHandler

import os
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
from logger import logDataUpdate, logAccountOperation
from auth import authenticate_user, create_session, validate_session, logout
from logger_config import app_logger, log_security_event
from audit_logger import log_audit_event, log_sql_execution, log_unauthorized_access
from security_monitor import detect_sql_injection, log_sql_injection_attempt, detect_policy_violation, log_policy_violation
# Security enhancements - 安全增强模块
from security import (
    decrypt_password, validate_email, validate_password, 
    sanitize_input, validate_table_name, validate_column_name,
    validate_table_name_whitelist, escape_identifier
)
from encryption import (
    getEncryptedColumns,
    buildSelectDecryptExpr,
    getEncryptionKey,
)


class SimpleAPIServer(BaseHTTPRequestHandler):
    server_version = "SimpleAPIServer/0.1"

    def do_OPTIONS(self):
        # CORS preflight - CORS预检请求
        from security import get_allowed_origins, is_origin_allowed
        origin = self.headers.get("Origin", "")
        allowed_origins = get_allowed_origins()
        self.send_response(204)
        if '*' in allowed_origins or is_origin_allowed(origin):
            self.send_header("Access-Control-Allow-Origin", origin if origin else "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-User-Role, X-User-ID, X-Key-Id")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Credentials", "true")
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
                    columns_info = getTableColumns(table, role=auth["role"])
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
            
            # Public key endpoint for frontend encryption - 前端加密用的公钥端点
            if path == "/auth/public-key":
                from security import get_public_key_pem
                public_key = get_public_key_pem()
                if public_key:
                    return json_response(self, 200, {
                        "publicKey": public_key,
                        "keyId": os.getenv("RSA_KEY_ID", "default")
                    })
                else:
                    return json_response(self, 503, {"error": "Public key not available"})

            return json_response(self, 404, {"error": "Not found"})
        except Exception as e:
            # Log error details but don't expose to client - 记录错误详情但不暴露给客户端
            import logging
            logging.error(f"GET request error: {str(e)}", exc_info=True)
            traceback.print_exc()  # Keep for development - 开发环境保留
            # Return generic error message - 返回通用错误信息
            return json_response(self, 500, {"error": "Server error occurred"})

    def do_POST(self):
        try:
            url = urllib.parse.urlparse(self.path)
            path = url.path
            self.log_message(f"POST {path}")

            if path == "/auth/login":
                # Get client IP address
                client_ip = self.client_address[0] if hasattr(self, 'client_address') else self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or 'unknown'
                
                data = read_json(self) or {}
                email = data.get("email", "").strip()
                password = data.get("password", "")
                encrypted_password = data.get("encryptedPassword", "")  # Support encrypted password - 支持加密密码
                
                # Log login request
                app_logger.info(f"Login request received: email={email}, ip={client_ip}")
                logAccountOperation(client_ip, None, None, f"Login request sent: email={email}")
                
                # Input validation - 输入验证
                if not email:
                    app_logger.warning(f"Login rejected: email missing, ip={client_ip}")
                    log_security_event('login_rejected', {'reason': 'email_missing'}, None, client_ip)
                    logAccountOperation(client_ip, None, None, f"Login rejected: reason=Email missing")
                    return json_response(self, 400, {"ok": False, "error": "Email is required"})
                if not password and not encrypted_password:
                    app_logger.warning(f"Login rejected: password missing, email={email}, ip={client_ip}")
                    log_security_event('login_rejected', {'email': email, 'reason': 'password_missing'}, None, client_ip)
                    logAccountOperation(client_ip, None, None, f"Login rejected: email={email}, reason=Password missing")
                    return json_response(self, 400, {"ok": False, "error": "Password is required"})
                
                # Validate email format - 验证邮箱格式
                if not validate_email(email):
                    app_logger.warning(f"Login rejected: invalid email format, email={email}, ip={client_ip}")
                    log_security_event('login_rejected', {'email': email, 'reason': 'invalid_email_format'}, None, client_ip)
                    logAccountOperation(client_ip, None, None, f"Login rejected: email={email}, reason=Invalid email format")
                    return json_response(self, 400, {"ok": False, "error": "Invalid email format"})
                
                # Decrypt password if encrypted - 如果密码已加密则解密
                if encrypted_password:
                    decrypted = decrypt_password(encrypted_password)
                    if decrypted:
                        password = decrypted
                    # If decryption fails, fall back to plain password (backward compatibility)
                    # 如果解密失败，回退到明文密码（向后兼容）
                
                # Check for SQL injection attempts in email
                if detect_sql_injection(email):
                    app_logger.warning(f"SQL injection attempt detected in login: email={email}, ip={client_ip}")
                    log_sql_injection_attempt(email, None, client_ip)
                    log_security_event('sql_injection_attempt', {'email': email, 'location': 'login_email'}, None, client_ip)
                    logAccountOperation(client_ip, None, None, f"SQL injection attempt: email={email}, location=login_email")
                    return json_response(self, 400, {"ok": False, "error": "Invalid input"})
                
                # Check for SQL injection attempts in password
                if password and detect_sql_injection(password):
                    app_logger.warning(f"SQL injection attempt detected in login: password field, email={email}, ip={client_ip}")
                    log_sql_injection_attempt(password, None, client_ip)
                    log_security_event('sql_injection_attempt', {'email': email, 'location': 'login_password'}, None, client_ip)
                    logAccountOperation(client_ip, None, None, f"SQL injection attempt: email={email}, location=login_password")
                    return json_response(self, 400, {"ok": False, "error": "Invalid input"})
                
                # Validate password - 验证密码
                if password:
                    is_valid, error_msg = validate_password(password)
                    if not is_valid:
                        app_logger.warning(f"Login rejected: invalid password format, email={email}, ip={client_ip}")
                        log_security_event('login_rejected', {'email': email, 'reason': 'invalid_password_format'}, None, client_ip)
                        logAccountOperation(client_ip, None, None, f"Login rejected: email={email}, reason=Invalid password format")
                        return json_response(self, 400, {"ok": False, "error": error_msg})
                
                # Sanitize inputs - 清理输入
                email = sanitize_input(email, max_length=255)
                password = sanitize_input(password, max_length=128)
                
                if not email or not password:
                    app_logger.warning(f"Login rejected: sanitization failed, email={email}, ip={client_ip}")
                    log_security_event('login_rejected', {'email': email, 'reason': 'sanitization_failed'}, None, client_ip)
                    logAccountOperation(client_ip, None, None, f"Login rejected: email={email}, reason=Input sanitization failed")
                    return json_response(self, 400, {"ok": False, "error": "Invalid input"})
                
                # Authenticate user
                user_info = authenticate_user(email, password, client_ip)
                
                if user_info:
                    # Create session
                    token = create_session(user_info)
                    app_logger.info(f"Session created for login: user_id={user_info['user_id']}, role={user_info['role']}, ip={client_ip}")
                    logAccountOperation(client_ip, user_info['user_id'], user_info['role'], f"Session created successfully: user_id={user_info['user_id']}, role={user_info['role']}")
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
                    # Login failed - ensure it's logged (brute force attack indicator)
                    # Note: authenticate_user already logs this, but we ensure it's recorded here too
                    app_logger.warning(f"Login failed: email={email}, reason=invalid_credentials, ip={client_ip}")
                    log_security_event('login_failed', {'email': email, 'reason': 'invalid_credentials'}, None, client_ip)
                    logAccountOperation(client_ip, None, None, f"Login failed: email={email}, reason=Invalid email or password")
                    return json_response(self, 401, {"ok": False, "error": "Invalid email or password"})

            elif path == "/auth/logout":
                auth_header = self.headers.get("Authorization", "")
                token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
                if logout(token):
                    return json_response(self, 200, {"ok": True, "message": "Logged out successfully"})
                else:
                    return json_response(self, 400, {"ok": False, "error": "Invalid token"})
            elif path == "/performQuery":
                # Get client IP address
                client_ip = self.client_address[0] if hasattr(self, 'client_address') else self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or 'unknown'
                
                auth = parse_bearer_role(self.headers)
                if not auth:
                    # Log unauthorized access attempt (session attack indicator)
                    auth_header = self.headers.get("Authorization", "")
                    token_info = "missing"
                    if auth_header.startswith("Bearer "):
                        token = auth_header.replace("Bearer ", "")
                        token_info = f"invalid_token: {token[:20]}..." if len(token) > 20 else f"invalid_token: {token}"
                    app_logger.warning(f"Unauthorized query attempt: ip={client_ip}, token={token_info}")
                    log_security_event('unauthorized_access', {'action': 'query', 'reason': 'invalid_token', 'token_info': token_info}, None, client_ip)
                    logAccountOperation(client_ip, None, None, f"Unauthorized access: action=query, reason=Invalid or missing token (session attack attempt)")
                    return json_response(self, 401, {"error": "Unauthorized"})

                data = read_json(self) or {}
                table = str(data.get("currentTable") or "")
                filters = data.get("filters", [])
                orders = data.get("orders", [])
                limit = int(data.get("limit", 100))
                offset = int(data.get("offset", 0))
                limit = max(1, min(limit, 500))
                offset = max(0, offset)

                # Log query request
                app_logger.info(f"Query request: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, ip={client_ip}")
                logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Database query request: table={table}")

                # Validate table name with whitelist - 使用白名单验证表名（更安全）
                allowed_tables = ROLE_TABLES.get(auth["role"], [])
                if not validate_table_name_whitelist(table, allowed_tables):
                    app_logger.warning(f"Invalid table name in query: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, ip={client_ip}")
                    log_security_event('policy_violation', {'action': 'query', 'resource': table, 'reason': 'invalid_table_name'}, auth.get('personId'), client_ip)
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Policy violation: action=query, table={table}, reason=Invalid table name")
                    return json_response(self, 400, {"error": "Invalid table name"})

                # check if the table is allowed for the role
                if table not in allowed_tables:
                    app_logger.warning(f"Access denied to table: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, ip={client_ip}")
                    log_policy_violation('read', auth.get('role'), table, auth.get('personId'), client_ip)
                    log_unauthorized_access('query', auth.get('personId'), auth.get('role'), client_ip, table)
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Inappropriate access: action=query, table={table}, reason=Access denied")
                    return json_response(self, 403, {"error": "Forbidden"})

                columnData = getTableColumns(table, role=auth.get('role'))
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
                    # Validate column name - 验证列名
                    if not validate_column_name(targetColumn):
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
                    # Validate column name - 验证列名
                    if not validate_column_name(targetColumn):
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

                # Log database query access
                log_sql_execution('SELECT', table, auth.get('personId'), auth.get('role'), sql, client_ip, True)
                log_audit_event('query', {'table': table, 'filters': len(filters), 'limit': limit}, auth.get('personId'), auth.get('role'), client_ip, sql)

                final_params = select_params + where_params
                results = db_query(sql, final_params, role=auth.get('role'))
                app_logger.info(f"Query executed successfully: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, rows={len(results)}, ip={client_ip}")
                logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Database query successful: table={table}, rows_returned={len(results)}")
                return json_response(self, 200, {"results": results})
            elif path == "/data/update":
                # Get client IP address
                client_ip = self.client_address[0] if hasattr(self, 'client_address') else self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or 'unknown'
                
                auth = parse_bearer_role(self.headers)
                if not auth:
                    app_logger.warning(f"Unauthorized update attempt: ip={client_ip}")
                    log_security_event('unauthorized_access', {'action': 'update', 'reason': 'no_auth'}, None, client_ip)
                    logAccountOperation(client_ip, None, None, f"Unauthorized access: action=update, reason=Token error or missing")
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})

                rolePrivileges = RolePrivileges.get(auth["role"], {})
                data = read_json(self) or {}
                table = str(data.get("table") or "")
                key = data.get("key", {})
                updateValues = data.get("updateValues", {})
                
                # Log update request
                app_logger.info(f"Update request: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, ip={client_ip}")
                logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Data update request: table={table}")
                
                # Validate table name - 验证表名
                if not validate_table_name(table):
                    app_logger.warning(f"Invalid table name in update: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, ip={client_ip}")
                    log_security_event('policy_violation', {'action': 'update', 'resource': table, 'reason': 'invalid_table_name'}, auth.get('personId'), client_ip)
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Policy violation: action=update, table={table}, reason=Invalid table name")
                    return json_response(self, 400, {"ok": False, "error": "Invalid table name"})

                setColumnSql = []
                params = []

                # check if the table is allowed for the role
                if table not in ROLE_TABLES.get(auth["role"], []):
                    app_logger.warning(f"Access denied to table for update: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, ip={client_ip}")
                    log_policy_violation('write', auth.get('role'), table, auth.get('personId'), client_ip)
                    log_unauthorized_access('update', auth.get('personId'), auth.get('role'), client_ip, table)
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Inappropriate access: action=update, table={table}, reason=Access denied")
                    return json_response(self, 403, {"error": "Forbidden"})

                columnData = getTableColumns(table, role=auth.get('role'))
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

                # Log data modification
                logDataUpdate(auth["personId"], auth["role"], sql)
                log_sql_execution('UPDATE', table, auth.get('personId'), auth.get('role'), sql, client_ip, True)
                log_audit_event('update', {'table': table, 'key': key, 'updateValues': list(updateValues.keys())}, auth.get('personId'), auth.get('role'), client_ip, sql)

                try:
                    rows_affected = db_execute(sql, params, role=auth.get('role'))
                    app_logger.info(f"Update executed successfully: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, rows_affected={rows_affected}, ip={client_ip}")
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Data update successful: table={table}, rows_affected={rows_affected}")
                    return json_response(self, 200, {"ok": True, "updated": updateValues})
                except Exception as e:
                    # Log error details but don't expose to client - 记录错误详情但不暴露给客户端
                    app_logger.error(f"Update error: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, error={e}, ip={client_ip}")
                    log_sql_execution('UPDATE', table, auth.get('personId'), auth.get('role'), sql, client_ip, False)
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Data update failed: table={table}, error={str(e)}")
                    import logging
                    logging.error(f"Update error: {str(e)}", exc_info=True)
                    traceback.print_exc()  # Keep for development - 开发环境保留
                    # Return generic error message - 返回通用错误信息
                    return json_response(self, 500, {"ok": False, "error": "Server error occurred"})
            elif path == "/data/delete":
                # Get client IP address
                client_ip = self.client_address[0] if hasattr(self, 'client_address') else self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or 'unknown'
                
                auth = parse_bearer_role(self.headers)
                if not auth:
                    app_logger.warning(f"Unauthorized delete attempt: ip={client_ip}")
                    log_security_event('unauthorized_access', {'action': 'delete', 'reason': 'no_auth'}, None, client_ip)
                    logAccountOperation(client_ip, None, None, f"Unauthorized access: action=delete, reason=Token error or missing")
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})

                rolePrivileges = RolePrivileges.get(auth["role"], {})
                data = read_json(self) or {}
                table = str(data.get("table") or "")
                key = data.get("key", {})
                
                # Log delete request
                app_logger.info(f"Delete request: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, ip={client_ip}")
                logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Data delete request: table={table}")
                
                # Validate table name with whitelist - 使用白名单验证表名（更安全）
                allowed_tables = ROLE_TABLES.get(auth["role"], [])
                if not validate_table_name_whitelist(table, allowed_tables):
                    app_logger.warning(f"Invalid table name in delete: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, ip={client_ip}")
                    log_security_event('policy_violation', {'action': 'delete', 'resource': table, 'reason': 'invalid_table_name'}, auth.get('personId'), client_ip)
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Policy violation: action=delete, table={table}, reason=Invalid table name")
                    return json_response(self, 400, {"ok": False, "error": "Invalid table name"})

                 # check if the table is allowed for the role
                if table not in allowed_tables:
                    app_logger.warning(f"Access denied to table for delete: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, ip={client_ip}")
                    log_policy_violation('delete', auth.get('role'), table, auth.get('personId'), client_ip)
                    log_unauthorized_access('delete', auth.get('personId'), auth.get('role'), client_ip, table)
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Inappropriate access: action=delete, table={table}, reason=Access denied")
                    return json_response(self, 403, {"error": "Forbidden"})

                columnData = getTableColumns(table, role=auth.get('role'))
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

                # Log data modification
                logDataUpdate(auth["personId"], auth["role"], sql)
                log_sql_execution('DELETE', table, auth.get('personId'), auth.get('role'), sql, client_ip, True)
                log_audit_event('delete', {'table': table, 'key': key}, auth.get('personId'), auth.get('role'), client_ip, sql)

                try:
                    rows_affected = db_execute(sql, params, role=auth.get('role'))
                    app_logger.info(f"Delete executed successfully: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, rows_affected={rows_affected}, ip={client_ip}")
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Data delete successful: table={table}, rows_affected={rows_affected}")
                    return json_response(self, 200, {"ok": True, "deleted": key})
                except Exception as e:
                    # Log error details but don't expose to client - 记录错误详情但不暴露给客户端
                    app_logger.error(f"Delete error: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, error={e}, ip={client_ip}")
                    log_sql_execution('DELETE', table, auth.get('personId'), auth.get('role'), sql, client_ip, False)
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Data delete failed: table={table}, error={str(e)}")
                    import logging
                    logging.error(f"Delete error: {str(e)}", exc_info=True)
                    traceback.print_exc()  # Keep for development - 开发环境保留
                    # Return generic error message - 返回通用错误信息
                    return json_response(self, 500, {"ok": False, "error": "Server error occurred"})
            elif path == "/data/insert":
                # Get client IP address
                client_ip = self.client_address[0] if hasattr(self, 'client_address') else self.headers.get('X-Forwarded-For', '').split(',')[0].strip() or 'unknown'
                
                auth = parse_bearer_role(self.headers)
                if not auth:
                    app_logger.warning(f"Unauthorized insert attempt: ip={client_ip}")
                    log_security_event('unauthorized_access', {'action': 'insert', 'reason': 'no_auth'}, None, client_ip)
                    logAccountOperation(client_ip, None, None, f"Unauthorized access: action=insert, reason=Token error or missing")
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})

                rolePrivileges = RolePrivileges.get(auth["role"], {})
                data = read_json(self) or {}
                table = str(data.get("table") or "")
                updateValues = data.get("insertValues", {})
                params = []
                
                # Log insert request
                app_logger.info(f"Insert request: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, ip={client_ip}")
                logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Data insert request: table={table}")
                
                # Validate table name with whitelist - 使用白名单验证表名（更安全）
                allowed_tables = ROLE_TABLES.get(auth["role"], [])
                if not validate_table_name_whitelist(table, allowed_tables):
                    app_logger.warning(f"Invalid table name in insert: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, ip={client_ip}")
                    log_security_event('policy_violation', {'action': 'insert', 'resource': table, 'reason': 'invalid_table_name'}, auth.get('personId'), client_ip)
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Policy violation: action=insert, table={table}, reason=Invalid table name")
                    return json_response(self, 400, {"ok": False, "error": "Invalid table name"})

                # check if the table is allowed for the role
                if table not in allowed_tables:
                    app_logger.warning(f"Access denied to table for insert: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, ip={client_ip}")
                    log_policy_violation('write', auth.get('role'), table, auth.get('personId'), client_ip)
                    log_unauthorized_access('insert', auth.get('personId'), auth.get('role'), client_ip, table)
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Inappropriate access: action=insert, table={table}, reason=Access denied")
                    return json_response(self, 403, {"error": "Forbidden"})
                
                columnData = getTableColumns(table, role=auth.get('role'))
                
                # Check if insert columns match allowed columns
                allowed_insert_columns = rolePrivileges.get(table, {}).get("insert", [])
                if set(updateValues.keys()) != set(allowed_insert_columns):
                    return json_response(self, 401, {"ok": False, "error": "Unauthorized"})
                
                # Validate and escape column names - 验证并转义列名
                updateValueColumns = list(updateValues.keys())
                for col in updateValueColumns:
                    if not validate_column_name(col):
                        return json_response(self, 400, {"ok": False, "error": f"Invalid column name: {col}"})
                    escaped_col = escape_identifier(col)
                    if not escaped_col:
                        return json_response(self, 400, {"ok": False, "error": f"Invalid column name: {col}"})

                # Build INSERT SQL with encryption support
                ordered_columns = allowed_insert_columns
                table_encrypted_columns = getEncryptedColumns(table)

                columns_clause = []
                value_fragments = []
                params = []
                encryption_key_value = None

                for col in ordered_columns:
                    columns_clause.append(f"`{col}`")
                    val = updateValues[col]
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

                # Log data modification
                logDataUpdate(auth["personId"], auth["role"], sql)
                log_sql_execution('INSERT', table, auth.get('personId'), auth.get('role'), sql, client_ip, True)
                log_audit_event('insert', {'table': table, 'columns': updateValueColumns}, auth.get('personId'), auth.get('role'), client_ip, sql)

                try:
                    rows_affected = db_execute(sql, params, role=auth.get('role'))
                    app_logger.info(f"Insert executed successfully: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, rows_affected={rows_affected}, ip={client_ip}")
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Data insert successful: table={table}, rows_affected={rows_affected}")
                    return json_response(self, 200, {"ok": True, "insert": updateValueColumns})
                except Exception as e:
                    # Log error details but don't expose to client - 记录错误详情但不暴露给客户端
                    app_logger.error(f"Insert error: user_id={auth.get('personId')}, role={auth.get('role')}, table={table}, error={e}, ip={client_ip}")
                    log_sql_execution('INSERT', table, auth.get('personId'), auth.get('role'), sql, client_ip, False)
                    logAccountOperation(client_ip, auth.get('personId'), auth.get('role'), f"Data insert failed: table={table}, error={str(e)}")
                    import logging
                    logging.error(f"Insert error: {str(e)}", exc_info=True)
                    traceback.print_exc()  # Keep for development - 开发环境保留
                    # Return generic error message - 返回通用错误信息
                    return json_response(self, 500, {"ok": False, "error": "Server error occurred"})

            return json_response(self, 404, {"error": "Not found"})
        except Exception as e:
            # Log error details but don't expose to client - 记录错误详情但不暴露给客户端
            import logging
            logging.error(f"POST request error: {str(e)}", exc_info=True)
            traceback.print_exc()  # Keep for development - 开发环境保留
            # Return generic error message - 返回通用错误信息
            return json_response(self, 500, {"error": "Server error occurred"})

    def log_message(self, format, *args):
        print("%s - - [%s] %s" % (self.address_string(),
            self.log_date_time_string(),
            format % args))