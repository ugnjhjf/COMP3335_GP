#!/usr/bin/env python3

# =========================
# Simple auth and role logic
# =========================
VALID_ROLES = {"aro", "student", "guardian", "dro"}

# Role-table visibility mapping
ROLE_TABLES = {
    "student": ["students", "grades", "disciplinary_records"],
    "guardian": ["guardians", "grades", "disciplinary_records"],
    "aro": ["grades"],
    "dro": ["disciplinary_records"],
}

RolePrivileges = {
    "student": {
        "students": {
            "read": ["StuID", "last_name", "first_name", "gender", "Id_No",
                "address", "phone", "email", "guardian_relation"],
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
            "read": ["GuaID", "last_name", "first_name", "phone", "email"],
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
            "read": ["StfID", "last_name", "first_name", "gender", "Id_No",
                "address", "phone", "email", "guardian_relation"], 
            "range": "All",
            "insert": ['StuID', 'date', 'StfID', 'descriptions'],
            "update": ["date", "description"],
            "delete": True
        },
    }
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
    """
    Parse user role and ID from HTTP headers
    Supports both token-based auth and direct header auth (for backward compatibility)
    Note: Invalid token attempts are logged in api_handler.py when this returns None
    """
    # Try token-based authentication first
    auth_header = headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        from auth import validate_session
        token = auth_header.replace("Bearer ", "")
        session_info = validate_session(token)
        if session_info:
            return {
                "role": session_info["role"],
                "personId": session_info["user_id"]
            }
        # Invalid token - will be logged by caller (api_handler.py)
    
    # Fallback to direct header authentication (for backward compatibility)
    role_header = headers.get("X-User-Role")
    if not role_header:
        return None
    role = role_header.lower()
    personId = headers.get("X-User-ID")
    if role in VALID_ROLES:
        return {"role": role, "personId": personId}
    return None

def buildRangeFilter(auth, table_name, currentTableName="target"):
    """Build data range filter conditions based on role privileges"""
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

    # "All" range means no filtering (full access) - used by admin roles
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

def retrieveReadableColumns(table_priv, available_columns):
    read_perm = table_priv.get("read")
    if read_perm is True:
        return set(available_columns)
    if isinstance(read_perm, (list, tuple, set)):
        lowermap = {col.lower(): col for col in available_columns}
        allowed = set()
        for col_name in read_perm:
            key = str(col_name).lower()
            if key in lowermap:
                allowed.add(lowermap[key])
        return allowed
    return set()