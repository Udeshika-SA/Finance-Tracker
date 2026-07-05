from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from src.database.db import get_db
from src.services.recommendations import get_recommendations

finance_bp = Blueprint("finance", __name__)


# =========================
# DASHBOARD Page
# =========================
@finance_bp.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)


    # ----------------- TOTAL INCOME -----------------
    cursor.execute("""
        SELECT SUM(t.amount) AS total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id=%s AND c.type='Income'
    """, (current_user.id,))
    total_income = float(cursor.fetchone()["total"] or 0)


    # ----------------- TOTAL EXPENSE -----------------
    cursor.execute("""
        SELECT SUM(t.amount) AS total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id=%s AND c.type='Expense'
    """, (current_user.id,))
    total_expense = float(cursor.fetchone()["total"] or 0)


    # ----------------- SAVINGS -----------------
    cursor.execute("""
        SELECT SUM(amount) AS total
        FROM savings
        WHERE user_id=%s
    """, (current_user.id,))
    savings = float(cursor.fetchone()["total"] or 0)


    # ----------------- BALANCE -----------------
    balance = total_income - (total_expense + savings)


    # ----------------- RECOMMENDATIONS -----------------
    cursor.execute("""
    SELECT
    c.name AS category,
    t.amount
    FROM transactions t
    JOIN categories c
    ON t.category_id=c.id
    WHERE t.user_id=%s
    AND c.type='Expense'
    """,(current_user.id,))

    expense_data = cursor.fetchall()

    recommendation = get_recommendations(expense_data,  total_income, total_expense, savings)
    

    # ----------------- PIE CHART -----------------
    cursor.execute("""
        SELECT c.name AS category, SUM(tr.amount) AS total
        FROM transactions tr
        JOIN categories c ON tr.category_id = c.id
        WHERE tr.user_id=%s AND c.type='Expense'
        GROUP BY c.name
    """, (current_user.id,))

    expense_data = cursor.fetchall()

    # ---------- Totals
    expense_total = sum([float(x["total"]) for x in expense_data])
    savings_total = float(savings or 0)

    # ---------- Pie data
    pie_data = []

    # Expense categories
    for e in expense_data:
        pie_data.append({
            "category": e["category"],
            "total": float(e["total"])
        })

    # Savings
    pie_data.append({
        "category": "Savings",
        "total": savings_total
    })

    # Balance (remaining income)
    balance_value = total_income - (expense_total + savings_total)

    if balance_value > 0:
        pie_data.append({
            "category": "Balance",
            "total": balance_value
        })

    # Final Arrays
    labels = [x["category"] for x in pie_data]
    values = [x["total"] for x in pie_data]


    # ----------------- Monthly Chart (Line) -----------------
    cursor.execute("""
        SELECT MONTH(created_at) AS month, SUM(amount) AS total
        FROM transactions
        WHERE user_id=%s
        GROUP BY MONTH(created_at)
        ORDER BY month
    """, (current_user.id,))
    monthly = cursor.fetchall()

    months = [str(m["month"]) for m in monthly]
    monthly_values = [float(m["total"]) for m in monthly]

    return render_template(
        "dashboard.html",
        show_nav=True,
        total_income=total_income,
        total_expense=total_expense,
        savings=savings,
        balance=balance,
        labels=labels,
        values=values,
        months=months,
        monthly_values=monthly_values,
        recommendation=recommendation
    )



# =========================
# ADD TRANSACTION + SAVINGS Page
# =========================
@finance_bp.route("/add-transaction", methods=["GET", "POST"])
@login_required
def add_transaction():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        # ----------------- TRANSACTION -----------------
        if action == "transaction":
            category_id = request.form.get("category_id")
            amount = request.form.get("amount")

            if category_id and amount:
                cursor.execute("""
                    INSERT INTO transactions (user_id, category_id, amount)
                    VALUES (%s, %s, %s)
                """, (current_user.id, category_id, amount))
                db.commit()


        # ----------------- SAVINGS -----------------
        elif action == "savings":
            title = request.form.get("title")
            amount = request.form.get("amount")

            if title and amount:
                cursor.execute("""
                    INSERT INTO savings (user_id, title, amount)
                    VALUES (%s, %s, %s)
                """, (current_user.id, title, amount))
                db.commit()

        return redirect(url_for("finance.add_transaction"))

    #  -----------------TYPES (STATIC) -----------------
    types = [
        {"name": "Income"},
        {"name": "Expense"}
    ]

    # ----------------- CATEGORIES -----------------
    cursor.execute("""
        SELECT id, name, type
        FROM categories
        WHERE user_id=%s
    """, (current_user.id,))
    categories = cursor.fetchall()

    return render_template(
        "add_transaction.html",
        show_nav=True,
        types=types,
        categories=categories
    )



# =========================
# TRANSACTION HISTORY Page
# =========================
@finance_bp.route("/transaction-history")
@login_required
def transaction_history():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # ----------------- Get all transactions -----------------
    cursor.execute("""
    SELECT tr.id, tr.amount, tr.created_at, c.type, c.name AS category
    FROM transactions tr
    JOIN categories c
    ON tr.category_id=c.id
    WHERE tr.user_id=%s
    ORDER BY tr.created_at DESC
    """, (current_user.id,))

    transactions = cursor.fetchall()

    return render_template(
        "transaction_history.html",
        show_nav=True,
        transactions=transactions
    )



# =========================
# MANAGE CATEGORIES Page
# =========================
@finance_bp.route("/manage", methods=["GET", "POST"])
@login_required
def manage():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # ----------------- Insert new categories to the database -----------------
    if request.method == "POST":
        cursor.execute("""
            INSERT INTO categories (name, type, user_id)
            VALUES (%s, %s, %s)
        """, (
            request.form["category_name"],
            request.form["type"],
            current_user.id
        ))
        db.commit()

    # ----------------- Get all categories from database -----------------
    cursor.execute("""
        SELECT id, name, type
        FROM categories
        WHERE user_id=%s
    """, (current_user.id,))

    categories = cursor.fetchall()

    return render_template(
    "manage.html",
    show_nav=True,
    categories=categories
)


# ----------------- Update Category -----------------
@finance_bp.route("/update-category/<int:id>", methods=["POST"])
@login_required
def update_category(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    UPDATE categories
    SET name=%s,
        type=%s
    WHERE id=%s
    AND user_id=%s
    """, (
        request.form["name"],
        request.form["type"],
        id,
        current_user.id
    ))
    db.commit()
    return redirect(url_for("finance.manage"))


# ----------------- Delete Category -----------------
@finance_bp.route("/delete-category/<int:id>")
@login_required
def delete_category(id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM categories WHERE id=%s AND user_id=%s",
        (id, current_user.id)
    )
    db.commit()

    return redirect(url_for("finance.manage"))