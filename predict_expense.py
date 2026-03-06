from db_connection import get_connection
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

user_id = 1

db = get_connection()
cursor = db.cursor(dictionary=True)

cursor.execute("""
SELECT MONTH(expense_date) as month,
       SUM(amount) as total
FROM expenses
WHERE user_id=%s
GROUP BY MONTH(expense_date)
ORDER BY month
""", (user_id,))

data = cursor.fetchall()
cursor.close()
db.close()

if len(data) < 2:
    print("Not enough data for prediction")
else:
    df = pd.DataFrame(data)

    X = np.array(df["month"]).reshape(-1,1)
    y = np.array(df["total"])

    model = LinearRegression()
    model.fit(X,y)

    next_month = max(df["month"]) + 1
    prediction = model.predict([[next_month]])

    # ensure we don't return a negative value
    expense_prediction = prediction[0]
    if expense_prediction < 0:
        expense_prediction = 0

    print("Predicted Next Month Expense:", expense_prediction)
