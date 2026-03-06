from db_connection import get_connection

name = "Sravani"
email = "sravani@gmail.com"
password = "1234"

db = get_connection()
cursor = db.cursor()

cursor.execute(
    "INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",
    (name, email, password)
)

db.commit()
print("User inserted successfully!")

cursor.close()
db.close()
