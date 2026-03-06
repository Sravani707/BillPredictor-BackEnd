import mysql.connector

db = None
cursor = None

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )

    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS monthly_bill_db")
    print("Database created successfully!")

except Exception as e:
    print("Error:", e)

finally:
    if cursor is not None:
        cursor.close()
    if db is not None and db.is_connected():
        db.close()
