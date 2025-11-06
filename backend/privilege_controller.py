#!/usr/bin/env python3

# =========================
# Simple auth and role logic
# =========================
# Note: "root" role is for testing purposes only - provides full access to all tables
VALID_ROLES = {"aro", "student", "guardian", "dro", "root"}

# Mock role-table visibility (adjust to your schema)
# Note: "root" role has access to all tables for testing purposes
ROLE_TABLES = {
    "student": ["students", "grades", "disciplinary_records"],
    "guardian": ["guardians", "grades", "disciplinary_records"],
    "aro": ["grades"],
    "dro": ["disciplinary_records"],
    "root": ["students", "guardians", "grades", "disciplinary_records", "courses", "staffs", "dataUpdateLog"],  # Testing role: full access
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
    # Testing role: root has full access to all tables and operations
    "root": {
        "students": {
            "read": True, 
            "range": "All",  # Can access all records
            "insert": ['StuID', 'last_name', 'first_name', 'gender', 'Id_No', 'address', 'phone', 'email', 'guardian_relation'],
            "update": ['last_name', 'first_name', 'gender', 'Id_No', 'address', 'phone', 'email', 'guardian_relation'],
            "delete": True  # Full delete permission
        },
        "guardians": {
            "read": True, 
            "range": "All",
            "insert": ['GuaID', 'last_name', 'first_name', 'email', 'phone'],
            "update": ['last_name', 'first_name', 'email', 'phone'],
            "delete": True
        },
        "grades": {
            "read": True, 
            "range": "All",
            "insert": ['GradeID', 'StuID', 'CID', 'term', 'grade', 'comments'],
            "update": ['grade', 'term', 'comments'],
            "delete": True
        },
        "disciplinary_records": {
            "read": True, 
            "range": "All",
            "insert": ['DrID', 'StuID', 'date', 'StfID', 'descriptions'],
            "update": ['date', 'descriptions'],
            "delete": True
        },
        "courses": {
            "read": True, 
            "range": "All",
            "insert": ['CID', 'course_name', 'description'],
            "update": ['course_name', 'description'],
            "delete": True
        },
        "staffs": {
            "read": True, 
            "range": "All",
            "insert": ['StfID', 'last_name', 'first_name', 'email', 'phone'],
            "update": ['last_name', 'first_name', 'email', 'phone'],
            "delete": True
        },
        "dataUpdateLog": {
            "read": True, 
            "range": "All",
            "insert": ['LogID', 'user_id', 'user_role', 'sql_text'],
            "update": ['sql_text'],
            "delete": True
        }
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
    """Parse user role and ID from HTTP headers"""
    role_header = headers.get("X-User-Role")
    if not role_header:
        return None
    role = role_header.lower()
    personId = headers.get("X-User-ID")
    if role in VALID_ROLES:
        return {"role": role, "personId": personId}
    return None

def buildRangeFilter(auth, table_name, currentTableName="target"):
    """Build data range filter conditions based on role privileges
    
    Note: "root" role always returns empty filter (full access) since range is "All"
    """
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

    # "All" range means no filtering (full access) - used by root role and admin roles
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
