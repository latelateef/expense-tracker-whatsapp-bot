from sqlalchemy import func
from datetime import datetime
from models import db, User, Expense

def add_expense(user_phone, res):
    user = db.session.query(User).filter_by(user_phone=user_phone).first()  # Get the user

    # Create an expense object
    expense = Expense(
        user_id=user.id,
        category=res["add_expense"]["category"].lower(),
        amount=res["add_expense"]["amount"],
        description=res["add_expense"]["description"].lower(),
    )

    # Add the expense to the session and commit it to the database
    db.session.add(expense)
    db.session.commit()

    # Prepare the message about the added expense
    message = f"""
✅ Expense added successfully!
    🗓 Date: {expense.date.strftime("%d-%m-%Y")}
    💰 Amount: ₹ {expense.amount}
    📝 Category: {expense.category}
    📄 Description: {expense.description}

"""

    # Fetch the user's budget limit and calculate total expenses for the current month
    budget = user.limit_amount
    current_month = datetime.now().month
    current_year = datetime.now().year

    total_expenses = (
        db.session.query(func.sum(Expense.amount))
        .filter(
            func.extract("month", Expense.date) == current_month,
            func.extract("year", Expense.date) == current_year,
        )
        .scalar()
    )

    # Determine if the user has exceeded the budget and update the message
    if total_expenses > budget:
        message += f"""
🚨 You have exceeded your budget of *₹ {budget}* for this month.
💸 The total expenses for the current month is *₹ {total_expenses}*.
"""
    else:
        message += f"""
💸 The total expenses for the current month is *₹ {total_expenses}*.
💰 You have *₹ {budget - total_expenses}* left in your budget for this month.
"""

    return message


def update_limit(user_phone, res):
    user = db.session.query(User).filter_by(user_phone=user_phone).first()  # Get the user

    # Update the user's limit amount
    user.limit_amount = res["update_limit"]["limit_amount"]
    db.session.commit()

    # Calculate total expenses for the current month
    current_month = datetime.now().month
    current_year = datetime.now().year
    total_expenses = (
        db.session.query(func.sum(Expense.amount))
        .filter(
            func.extract("month", Expense.date) == current_month,
            func.extract("year", Expense.date) == current_year,
        )
        .scalar()
    )

    # Prepare the response message
    msg = f"""
✅ The limit amount has been updated.
💵 You have currently set a limit of *₹ {res["update_limit"]["limit_amount"]}*.
💸 The total expenses for the current month is *₹ {total_expenses}*.
"""

    return msg


def view_limit(user_phone):
    user = db.session.query(User).filter_by(user_phone=user_phone).first()  # Get the user

    # Fetch the user's budget limit
    budget = user.limit_amount

    # Calculate total expenses for the current month
    current_month = datetime.now().month
    current_year = datetime.now().year
    total_expenses = (
        db.session.query(func.sum(Expense.amount))
        .filter(
            func.extract("month", Expense.date) == current_month,
            func.extract("year", Expense.date) == current_year,
        )
        .scalar()
    )

    # Prepare the response message
    msg = f"""
💵 Your current monthly limit is *₹ {budget}*.
💸 The total expenses for the current month is *₹ {total_expenses}*.
"""

    return msg


def delete_all_expenses(user_phone):
    # Delete all expenses for the user
    db.session.query(Expense).filter_by(user_id=db.session.query(User).filter_by(user_phone=user_phone).first().id).delete()
    db.session.commit()

    # Prepare the response message
    msg = """
    🗑️ All your expenses have been deleted successfully.
    """

    return msg


def delete_account(user_phone):
    # Delete all expenses for the user
    msg = delete_all_expenses(user_phone)
    # Delete the user account
    db.session.query(User).filter_by(user_phone=user_phone).delete()
    db.session.commit()

    # Prepare the response message
    msg = """
    🗑️ Your account has been deleted successfully.
    """

    return msg


def help():
    return """
✨ What you can do:
    📝 Update your monthly limit
    💸 Add new expenses
    🔍 Retrieve past expense details
    🔄 View your current monthly limit
    🧹 Delete all expenses
    🗑️ Delete your account

📝 Here are some example queries you can try:
    1. "Add ₹ 500 for groceries"
    2. "Add 200 for travel"
    3. "Update my monthly limit to Rs 5000"
    4. "Show my expenses"
    5. "Delete my expenses"
    6. "Delete my account"
    7. "Show my limit"
    8. "Help"
"""