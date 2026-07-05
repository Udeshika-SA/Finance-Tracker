def get_insights(data):
    total = sum([row["amount"] for row in data])

    return f"Total spending is {total}"