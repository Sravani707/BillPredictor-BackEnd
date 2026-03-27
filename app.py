from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from prophet import Prophet
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

# ---------------- EMAIL CONFIG ---------------- #

SENDER_EMAIL = "sravani.ch2004@gmail.com"
APP_PASSWORD = "pgvqvskdkgrhviwr"

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE CONNECTION ---------------- #

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="monthly_bill_db",
        port=3307
    )

def generate_event_savings(event_id, user_id, event_date, total_cost):

    db = get_db()
    cursor = db.cursor()

    today = datetime.today()
    event_dt = datetime.strptime(event_date, "%Y-%m-%d")

    # calculate months left
    months = (
        (event_dt.year - today.year) * 12 +
        (event_dt.month - today.month)
    )

    if months <= 0:
        months = 1

    monthly_amount = round(float(total_cost) / months, 2)

    current = today.replace(day=1)

    for i in range(months):

        month_year = current.strftime("%B %Y")

        cursor.execute("""
            INSERT INTO event_savings
            (event_id, user_id, month_year, required_amount, saved)
            VALUES (%s,%s,%s,%s,%s)
        """, (event_id, user_id, month_year, monthly_amount, 0))

        current += relativedelta(months=1)

    db.commit()
    cursor.close()
    db.close()

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
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        email = data.get('email')
        password = data.get('password')

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and user['password'] == password:
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "name": user['name'],
                "user_id": user['id']
            })

        return jsonify({"message": "Invalid Credentials"})

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ---------------- UPDATE PROFILE ---------------- #

@app.route('/update_profile', methods=['POST'])
def update_profile():
    try:
        data = request.json

        user_id = data.get("user_id")
        name = data.get("name")
        email = data.get("email")

        if not user_id:
            return jsonify({"message": "User ID missing"}), 400

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE users
            SET name=%s, email=%s
            WHERE id=%s
        """, (name, email, user_id))

        db.commit()

        cursor.close()
        db.close()

        return jsonify({
            "status": "success",
            "message": "Profile updated successfully"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
#----------------------forget password-------------------#

import random

def send_otp_email(receiver_email, otp):

    subject = "ExpenseAI Password Reset OTP"
    body = f"Your OTP for resetting password is: {otp}"

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()

        print("OTP email sent successfully")

    except Exception as e:
        print("Email sending failed:", e)


@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    try:
        data = request.json
        email = data.get("email")

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            db.close()
            return jsonify({"message": "Email not found"})

        otp = random.randint(100000, 999999)

        cursor.execute(
            "UPDATE users SET otp=%s WHERE email=%s",
            (otp, email)
        )
        db.commit()

        cursor.close()
        db.close()

        # Send OTP to email
        send_otp_email(email, otp)

        return jsonify({
            "message": "OTP sent successfully"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#--------------------------verify OTP----------------#
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json
        email = data.get("email")
        otp = data.get("otp")

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND otp=%s",
            (email, otp)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:
            return jsonify({"message": "OTP verified"})
        else:
            return jsonify({"message": "Invalid OTP"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#----------------reset password---------------#
@app.route('/reset_password', methods=['POST'])
def reset_password():
    try:
        data = request.json
        email = data.get("email")
        new_password = data.get("password")

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "UPDATE users SET password=%s, otp=NULL WHERE email=%s",
            (new_password, email)
        )

        db.commit()

        cursor.close()
        db.close()

        return jsonify({"message": "Password updated successfully"})

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

# ---------------- ADD INCOME ---------------- #

@app.route('/add_income', methods=['POST'])
def add_income():
    try:
        data = request.json

        user_id = data.get("user_id")
        amount = data.get("amount")

        conn = get_db()
        cursor = conn.cursor()

        query = """
            INSERT INTO income (user_id, amount, date)
            VALUES (%s, %s, CURDATE())
        """

        cursor.execute(query, (user_id, amount))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Income added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- GET INCOME ---------------- #

@app.route('/get_income/<int:user_id>', methods=['GET'])
def get_income(user_id):

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT IFNULL(SUM(amount),0) AS total_income
        FROM income
        WHERE user_id = %s
        AND MONTH(date)=MONTH(CURDATE())
        AND YEAR(date)=YEAR(CURDATE())
    """

    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    # ⭐ IMPORTANT FIX
    result["total_income"] = float(result["total_income"])

    return jsonify(result)


#-------------------RECALCULATE_EVENT_SAVINGS-----------#

@app.route("/recalculate_event_savings", methods=["POST"])
def recalculate_event_savings():

    data = request.json
    event_id = data["event_id"]
    new_amount = data["new_amount"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE event_savings
        SET required_amount = %s
        WHERE event_id = %s
        AND saved = 0
    """, (new_amount, event_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Updated successfully"})


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

# ---------------- AI PREDICT (WITH EVENTS) ---------------- #

@app.route('/ai_predict', methods=['POST'])
def ai_predict():
    try:
        data = request.json
        user_id = data.get('user_id')

        db = get_db()
        cursor = db.cursor(dictionary=True)   # ✅ dictionary cursor

        # ---------------------------------------------------
        # STEP 1: Collect training data
        # ---------------------------------------------------
        cursor.execute("""
            SELECT DATE_FORMAT(expense_date, '%Y-%m') AS month,
                   SUM(amount) AS total
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

        # Oldest → newest
        rows = rows[::-1]

        # ---------------------------------------------------
        # STEP 2: Prophet ML Model
        # ---------------------------------------------------

        df = pd.DataFrame({
            "ds": pd.to_datetime(
                [r["month"] + "-01" for r in rows],
                format="%Y-%m-%d"
            ),
            "y": [float(r["total"]) for r in rows]
        })

        df = df.sort_values("ds")

        # Train model
        model = Prophet()
        model.fit(df)

        # Predict next month
        future = model.make_future_dataframe(periods=1, freq='MS')
        forecast = model.predict(future)

        expense_prediction = float(forecast["yhat"].iloc[-1])

        if expense_prediction < 0:
            expense_prediction = 0

        # ---------------------------------------------------
        # STEP 3: Next month calculation
        # ---------------------------------------------------
        today = datetime.now()

        if today.month == 12:
            next_month = 1
            next_year = today.year + 1
        else:
            next_month = today.month + 1
            next_year = today.year

        # ---------------------------------------------------
        # STEP 4: Fetch events
        # ---------------------------------------------------
        cursor.execute("""
            SELECT event_name, estimated_cost
            FROM events
            WHERE user_id = %s
              AND MONTH(event_date) = %s
              AND YEAR(event_date) = %s
        """, (user_id, next_month, next_year))

        events = cursor.fetchall()

        event_total = sum(float(e["estimated_cost"]) for e in events) if events else 0

        # ---------------------------------------------------
        # STEP 5: Final Prediction
        # ---------------------------------------------------
        final_prediction = expense_prediction + event_total

        cursor.close()
        db.close()

        return jsonify({
            "expense_prediction": round(expense_prediction, 2),
            "event_added_amount": round(event_total, 2),
            "ai_predicted_next_month_expense": round(final_prediction, 2),
            "events_count": len(events),
            "based_on_months": [r["month"] for r in rows]
        })

    except Exception as e:
        print("AI Predict Error:", e)   # ✅ shows error in terminal
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

        event_id = cursor.lastrowid

        generate_event_savings(
            event_id,
            user_id,
            formatted_date,
            estimated_cost
        )

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

# ---------------- GET EVENT SAVINGS ---------------- #

@app.route('/event_savings/<int:user_id>/<int:event_id>', methods=['GET'])
def get_event_savings(user_id, event_id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, month_year, required_amount, saved
        FROM event_savings
        WHERE user_id=%s AND event_id=%s
        ORDER BY id ASC
    """, (user_id, event_id))

    rows = cursor.fetchall()

    # ✅ FIX: convert 0/1 → True/False
    for row in rows:
        row["saved"] = bool(row["saved"])

    cursor.close()
    db.close()

    return jsonify({
        "savings_plan": rows
    })

@app.route('/update_saving_status', methods=['POST'])
def update_saving_status():
    data = request.get_json()
    print("Received:", data)  # DEBUG

    saving_id = data.get('savingId')
    saved = data.get('saved')

    if saving_id is None or saved is None:
        return jsonify({"error": "missing savingId or saved"}), 400

    db = get_db()          # ✅ get database connection
    cursor = db.cursor()
    try:
        cursor.execute(
            "UPDATE event_savings SET saved=%s WHERE id=%s",
            (saved, saving_id)
        )
        db.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()


# ---------------- EVENT PLANNER (MAIN SCREEN) ---------------- #

@app.route('/event_planner/<int:user_id>', methods=['GET'])
def event_planner(user_id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            e.id,
            e.event_name,
            e.event_date,
            e.estimated_cost,

            IFNULL(SUM(
                CASE
                    WHEN es.saved = 1
                    THEN es.required_amount
                    ELSE 0
                END
            ),0) AS total_saved

        FROM events e

        LEFT JOIN event_savings es
            ON e.id = es.event_id

        WHERE e.user_id = %s
        GROUP BY e.id
        ORDER BY e.event_date ASC
    """, (user_id,))

    result = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(result)


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