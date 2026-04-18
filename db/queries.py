import sqlite3


DB_NAME = "db.sqlite"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    try:
        cursor = conn.cursor()

        with open("db/schema.sql", "r") as f:
            cursor.executescript(f.read())

        conn.commit()
    finally:
        conn.close()

# create
# create user
def create_user(payload):
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")
    
    required_fields = ["user_name", "user_email", "user_status"]

    field_parts = []
    value_parts = []
    values = []

    for field in required_fields:
        if field in payload:
            field_parts.append(field)
            value_parts.append("?")
            values.append(payload[field])

    if not field_parts:
        raise ValueError("payload is empty")

    query = f"""
        INSERT INTO users ({', '.join(field_parts)})
        VALUES ({', '.join(value_parts)})
    """

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, values)
        user_id = cursor.lastrowid
        conn.commit()
    finally:
        conn.close()

    return user_id

# create token
def create_token(user_id, payload):
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")
    
    required_fields = ["token_value", "token_expires_at"]

    field_parts = ["user_id"]
    value_parts = ["?"]
    values = [user_id]

    for field in required_fields:
        if field in payload:
            field_parts.append(field)
            value_parts.append("?")
            values.append(payload[field])

    if not any(field in payload for field in required_fields):
        raise ValueError("payload is empty or missing required fields")

    query = f"""
        INSERT INTO tokens ({', '.join(field_parts)})
        VALUES ({', '.join(value_parts)})
    """

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, values)
        token_id = cursor.lastrowid
        conn.commit()
    finally:
        conn.close()
    return token_id

# create task
def create_task(payload):

    if not isinstance(payload, dict):
        raise ValueError("task's payload must be a dict")

    required_fields = ["user_id", "task_title", "task_description", "task_status"]

    field_parts = []
    value_parts = []
    values = []

    for field in required_fields:
        if field in payload:
            field_parts.append(field)
            value_parts.append("?")
            values.append(payload[field])

    if not field_parts:
        raise ValueError("task's payload is empty")

    query = f"""
        INSERT INTO tasks ({', '.join(field_parts)})
        VALUES ({', '.join(value_parts)})
    """

    conn = get_connection()
    try:    
        cursor = conn.cursor()
        cursor.execute(query, values)
        task_id = cursor.lastrowid
        conn.commit()
    finally:
        conn.close()

    return task_id

# get tokens
def get_token_by_user(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, token_value, token_expires_at
            FROM tokens
            WHERE user_id = ?
            LIMIT 1
        """, (user_id,)
        )
        row = cursor.fetchone()
    finally:
        conn.close()
    return row

# get users
def get_users():
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * 
            FROM users
            ORDER BY user_id DESC
        """)
        rows = cursor.fetchall()
    finally:
        conn.close()

    return rows

def get_user_by_username(user_name):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * 
            FROM users 
            WHERE user_name = ? 
            LIMIT 1
        """, (user_name,)
        )
        row = cursor.fetchone()
    finally:
        conn.close()
    return row

def get_user_by_id(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * 
            FROM users
            WHERE user_id = ?
            LIMIT 1
        """, (user_id,)
        )
        row = cursor.fetchone()
    finally:
        conn.close()
    return row
    
def get_user_by_email(user_email):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * 
            FROM users 
            WHERE user_email = ? 
            LIMIT 1
        """, (user_email,)
        )
        row = cursor.fetchone()
    finally:
        conn.close()
    return row

# get tasks
def get_task_by_id(task_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM tasks
            WHERE tasks.task_id = ?
            LIMIT 1
        """, (task_id,)
        )
        row = cursor.fetchone()
    finally:
        conn.close()
    return row

def get_tasks_by_user(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT users.user_name, tasks.*
            FROM tasks
            JOIN users ON users.user_id = tasks.user_id 
            WHERE tasks.user_id = ?
            ORDER BY tasks.task_status DESC, tasks.task_id DESC
        """, (user_id,)
        )
        rows = cursor.fetchall()
    finally:
        conn.close()
    return rows

def get_active_tasks_by_user(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT users.user_name, tasks.*
            FROM tasks
            JOIN users ON users.user_id = tasks.user_id 
            WHERE tasks.user_id = ? AND tasks.task_status = 'active'
            ORDER BY tasks.task_id DESC
        """, (user_id,)
        )
        rows = cursor.fetchall()
    finally:
        conn.close()
    return rows

# update user
def update_user_by_id(user_id, payload):
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    allowed_fields = ["user_name", "user_email", "user_status"]

    set_parts = []
    values = []

    for field in allowed_fields:
        if field in payload:
            set_parts.append(f"{field} = ?")
            values.append(payload[field])

    if not set_parts:
        raise ValueError("payload is empty")
    
    values.append(user_id)

    query = f"""
        UPDATE users
        SET {', '.join(set_parts)}
        WHERE user_id = ?
        RETURNING *
    """

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, values)
        row = cursor.fetchone()
        conn.commit()
    finally:
        conn.close()

    return row

# update task
def update_task_by_id(task_id, payload):
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    allowed_fields = ["task_title", "task_description", "task_status"]

    set_parts = []
    values = []

    for field in allowed_fields:
        if field in payload:
            set_parts.append(f"{field} = ?")
            values.append(payload[field])

    if not set_parts:
        raise ValueError("payload is empty")
    
    values.append(task_id)

    query = f"""
        UPDATE tasks
        SET {', '.join(set_parts)}
        WHERE task_id = ?
        RETURNING *
    """

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, values)
        row = cursor.fetchone()
        conn.commit()
    finally:
        conn.close()

    return row

# delete user
def delete_user_by_id(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE 
            FROM users
            WHERE user_id = ?
        """, (user_id,)
        )
        conn.commit()
    finally:
        conn.close()

    return cursor.rowcount