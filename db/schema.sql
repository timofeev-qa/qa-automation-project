CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL UNIQUE,
    user_email TEXT NOT NULL UNIQUE,
    user_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tokens (
    token_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    token_value TEXT NOT NULL UNIQUE,
    token_expires_at TEXT NOT NULL,
    FOREIGN KEY (user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_title TEXT NOT NULL,
    task_description TEXT,
    task_status TEXT NOT NULL,
    FOREIGN KEY (user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE
)