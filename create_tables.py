from db_connection import get_connection

db = get_connection()
cursor = db.cursor()

# USERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    password VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# CATEGORIES
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories(
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100)
)
""")

# EXPENSES
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    category_id INT,
    amount DECIMAL(10,2),
    expense_date DATE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# EVENTS
cursor.execute("""
CREATE TABLE IF NOT EXISTS events(
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    event_name VARCHAR(150),
    expected_extra_amount DECIMAL(10,2),
    event_month INT,
    event_year INT
)
""")

db.commit()
print("Tables created successfully!")

cursor.close()
db.close()
