from db_connection import get_connection

db = get_connection()
cursor = db.cursor()

# Insert expenses for different months
expenses = [
    (1, 1, 8000, "2025-01-10"),
    (1, 1, 9000, "2025-02-10"),
    (1, 1, 10000, "2025-03-10")
]

for expense in expenses:
    cursor.execute("""
        INSERT INTO expenses (user_id, category_id, amount, expense_date)
        VALUES (%s, %s, %s, %s)
    """, expense)

db.commit()
cursor.close()
db.close()

print("Multiple expenses inserted successfully!")