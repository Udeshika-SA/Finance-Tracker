def get_recommendations(transactions, total_income, total_expense, savings):

    # No expense data
    if not transactions:
        return "No expense transactions found."

    totals = {}

    for row in transactions:
        category = row["category"]
        amount = float(row["amount"])

        totals[category] = totals.get(category, 0) + amount

    highest = max(totals, key=totals.get)
    amount = totals[highest]

    recommendation = ""


    # =========================
    # Highest spending category recommendation
    # =========================
    if highest.lower() == "food":
        recommendation = f"You spent Rs. {amount:.2f} on Food. Consider planning meals to reduce expenses."

    elif highest.lower() == "transport":
        recommendation = f"You spent Rs. {amount:.2f} on Transport. Using public transport may help save money."

    elif highest.lower() == "shopping":
        recommendation = f"You spent Rs. {amount:.2f} on Shopping. Setting a monthly shopping budget could help."

    elif highest.lower() == "entertainment":
        recommendation = f"You spent Rs. {amount:.2f} on Entertainment. Reducing unnecessary subscriptions could save money."

    else:
        recommendation = f"Your highest spending is on {highest} (Rs. {amount:.2f}). Consider reducing expenses in this category."

   
    # =========================
    # 80% expense warning
    # =========================
    if total_income > 0:
        expense_percentage = ((total_expense+ savings ) / total_income) * 100

        recommendation += (
            f"<br>Your expenses are {expense_percentage:.1f}% "
            "of your income. Try to keep your expenses below 80% to improve your financial stability."
        )

    return recommendation