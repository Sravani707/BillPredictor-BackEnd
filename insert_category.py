from db_connection import get_connection

categories = ["Rent", "Food", "Travel", "Shopping", "Bills"]

db = get_connection()
cursor = db.cursor()

for cat in categories:
    cursor.execute(
        "INSERT INTO categories (category_name) VALUES (%s)",
        (cat,)
    )

db.commit()
print("Categories inserted!")

cursor.close()
db.close()
