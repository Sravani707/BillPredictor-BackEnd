import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="monthly_bill_db"
)

cursor = conn.cursor()

user_id = 1
event_name = "Festival"
event_date = "2026-04-15"
estimated_cost = 3000.00

query = """
INSERT INTO events (user_id, event_name, event_date, estimated_cost)
VALUES (%s, %s, %s, %s)
"""

values = (user_id, event_name, event_date, estimated_cost)

cursor.execute(query, values)
conn.commit()

print("Event inserted successfully!")

cursor.close()
conn.close()
