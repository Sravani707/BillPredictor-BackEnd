from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from datetime import datetime
import numpy as np

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE CONNECTION ---------------- #

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="monthly_bill_db"
    )

# ---------------- ROOT TEST ---------------- #

@app.route('/')
def home():
    return "Monthly Bill Predictor Backend Running"

# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({"message": "User already exists"})

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        db.commit()
        user_id = cursor.lastrowid

        cursor.close()
        db.close()

        return jsonify({"message": "Registration Successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:
            return jsonify({
                "message": "Login Successful",
                "name": user['name'],
                "user_id": user['id']
            })
        else:
            return jsonify({"message": "Invalid Credentials"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- ADD EXPENSE ---------------- #

@app.route('/add_expense', methods=['POST'])
def add_expense():
    try:
        data = request.json
        user_id = data.get('user_id')
        category_id = data.get('category_id')
        amount = float(data.get('amount'))

        expense_date = datetime.now().strftime('%Y-%m-%d')

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO expenses (user_id, category_id, amount, expense_date)
            VALUES (%s, %s, %s, %s)
        """, (user_id, category_id, amount, expense_date))

        db.commit()
        cursor.close()
        db.close()

        return jsonify({"message": "Expense added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- HISTORY ---------------- #

@app.route('/history/<int:user_id>', methods=['GET'])
def get_history(user_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                e.id AS expense_id,
                e.amount,
                e.expense_date,
                e.category_id,
                IFNULL(c.category_name, 'Uncategorized') AS category_name
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = %s
            ORDER BY e.id DESC
        """, (user_id,))

        expenses = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify({"expenses": expenses})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- MONTHLY SUMMARY ---------------- #

@app.route('/monthly_summary/<int:user_id>', methods=['GET'])
def monthly_summary(user_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                IFNULL(c.category_name, 'Others') AS category_name,
                SUM(e.amount) AS total_amount
            FROM expenses e
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = %s
              AND MONTH(e.expense_date) = MONTH(CURRENT_DATE())
              AND YEAR(e.expense_date) = YEAR(CURRENT_DATE())
            GROUP BY c.category_name
        """, (user_id,))

        categories = cursor.fetchall()

        cursor.execute("""
            SELECT SUM(amount) AS total
            FROM expenses
            WHERE user_id = %s
              AND MONTH(expense_date) = MONTH(CURRENT_DATE())
              AND YEAR(expense_date) = YEAR(CURRENT_DATE())
        """, (user_id,))

        total = cursor.fetchone()['total'] or 0

        cursor.close()
        db.close()

        daily_average = round(total / datetime.now().day, 2) if total else 0

        return jsonify({
            "total_month_expense": float(total),
            "daily_average": daily_average,
            "categories": categories
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- NORMAL PREDICT ---------------- #

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        user_id = data.get('user_id')

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=%s", (user_id,))
        expense_total = cursor.fetchone()[0] or 0

        cursor.close()
        db.close()

        return jsonify({
            "predicted_next_month_expense": float(expense_total)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- AI PREDICT (WITH EVENTS) ---------------- #

@app.route('/ai_predict', methods=['POST'])
def ai_predict():
    try:
        data = request.json
        user_id = data.get('user_id')

        db = get_db()
        cursor = db.cursor()

        # ---------------------------------------------------
        # STEP 1: Get last 3 months expense totals
        # ---------------------------------------------------
        cursor.execute("""
            SELECT DATE_FORMAT(expense_date, '%Y-%m') AS month,
                   SUM(amount) as total
            FROM expenses
            WHERE user_id = %s
            GROUP BY month
            ORDER BY month DESC
            LIMIT 3
        """, (user_id,))

        rows = cursor.fetchall()

        # Need minimum data
        if len(rows) < 2:
            cursor.close()
            db.close()
            return jsonify({
                "message": "Not enough data for prediction"
            })

        # Oldest → newest order
        rows = rows[::-1]

        months = np.arange(len(rows))
        totals = np.array([float(r[1]) for r in rows])

        # ---------------------------------------------------
        # STEP 2: AI Learning (Linear Regression)
        # y = mx + c
        # ---------------------------------------------------
        m, c = np.polyfit(months, totals, 1)

        next_month_index = len(rows)
        expense_prediction = float(m * next_month_index + c)

        if expense_prediction < 0:
            expense_prediction = 0

        # ---------------------------------------------------
        # STEP 3: Get NEXT MONTH dates
        # ---------------------------------------------------
        today = datetime.now()

        if today.month == 12:
            next_month = 1
            next_year = today.year + 1
        else:
            next_month = today.month + 1
            next_year = today.year

        # ---------------------------------------------------
        # STEP 4: Fetch events for NEXT month
        # ---------------------------------------------------
        cursor.execute("""
            SELECT event_name, estimated_cost
            FROM events
            WHERE user_id = %s
              AND MONTH(event_date) = %s
              AND YEAR(event_date) = %s
        """, (user_id, next_month, next_year))

        events = cursor.fetchall()

        event_total = sum(float(e[1]) for e in events) if events else 0

        # ---------------------------------------------------
        # STEP 5: Final AI Prediction
        # ---------------------------------------------------
        final_prediction = expense_prediction + event_total

        cursor.close()
        db.close()

        return jsonify({
            "expense_prediction": round(expense_prediction, 2),
            "event_added_amount": round(event_total, 2),
            "ai_predicted_next_month_expense": round(final_prediction, 2),
            "events_count": len(events),
            "based_on_months": [r[0] for r in rows]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
# ---------------- GET CATEGORIES ---------------- #

@app.route('/categories', methods=['GET'])
def get_categories():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, category_name AS name
            FROM categories
        """)

        result = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- DELETE EXPENSE ---------------- #

@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        db.commit()

        if cursor.rowcount == 0:
            cursor.close()
            db.close()
            return jsonify({"message": "Expense not found"}), 404

        cursor.close()
        db.close()

        return jsonify({"message": "Expense deleted successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- ADD EVENT ---------------- #

@app.route('/add_event', methods=['POST'])
def add_event():
    try:
        data = request.json

        user_id = data.get('user_id')
        event_name = data.get('event_name')
        event_date = data.get('event_date')
        estimated_cost = data.get('estimated_cost')

        # Validate inputs
        if not user_id or not event_name or not event_date or not estimated_cost:
            return jsonify({"message": "Missing required fields"}), 400

        # Ensure date format is correct
        try:
            formatted_date = datetime.strptime(event_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except:
            return jsonify({"message": "Date must be in YYYY-MM-DD format"}), 400

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO events (user_id, event_name, event_date, estimated_cost)
            VALUES (%s, %s, %s, %s)
        """, (user_id, event_name, formatted_date, estimated_cost))

        db.commit()

        cursor.close()
        db.close()

        return jsonify({"message": "Event added successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- GET EVENTS ---------------- #

@app.route('/events/<int:user_id>', methods=['GET'])
def get_events(user_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, event_name, event_date, estimated_cost
            FROM events
            WHERE user_id = %s
            ORDER BY event_date ASC
        """, (user_id,))

        events = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify(events)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

        # ---------------- DELETE EVENT ---------------- #

@app.route('/delete_event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
        db.commit()

        if cursor.rowcount == 0:
            cursor.close()
            db.close()
            return jsonify({"message": "Event not found"}), 404

        cursor.close()
        db.close()

        return jsonify({"message": "Event deleted successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

        # ---------------- UPDATE EXPENSE ---------------- #

@app.route('/update_expense/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    try:
        data = request.json
        category_id = data.get('category_id')
        amount = data.get('amount')

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE expenses
            SET category_id = %s,
                amount = %s
            WHERE id = %s
        """, (category_id, amount, expense_id))

        db.commit()

        if cursor.rowcount == 0:
            cursor.close()
            db.close()
            return jsonify({"message": "Expense not found"}), 404

        cursor.close()
        db.close()

        return jsonify({"message": "Expense updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- MAIN ---------------- #


# ---------------- TRENDS ---------------- #
@app.route('/trends/<int:user_id>', methods=['GET'])
def get_trends(user_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT
                c.category_name,
                DATE_FORMAT(e.expense_date,'%%Y-%%m') AS month,
                SUM(e.amount) AS total
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = %s
            GROUP BY c.category_name, month
        """

        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()

        from collections import defaultdict

        data = defaultdict(dict)

        for r in rows:
            data[r["category_name"]][r["month"]] = float(r["total"])

        months = sorted({m for v in data.values() for m in v.keys()})

        if len(months) < 2:
            cursor.close()
            db.close()
            return jsonify({"trending_up": [], "trending_down": []})

        prev_month = months[-2]
        curr_month = months[-1]

        trending_up = []
        trending_down = []

        for category, values in data.items():
            prev = values.get(prev_month, 0)
            curr = values.get(curr_month, 0)

            if prev == 0 and curr > 0:
                percent = 100
                trending_up.append({
                    "category": category,
                    "percent": percent,
                    "change": curr
                })

            elif curr > prev and prev > 0:
                percent = round(((curr-prev)/prev)*100)
                trending_up.append({
                    "category": category,
                    "percent": percent,
                    "change": curr-prev
                })

            elif curr < prev and prev > 0:
                percent = round(((prev-curr)/prev)*100)
                trending_down.append({
                    "category": category,
                    "percent": percent,
                    "change": prev-curr
                })

        cursor.close()
        db.close()

        return jsonify({
            "trending_up": trending_up,
            "trending_down": trending_down
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)