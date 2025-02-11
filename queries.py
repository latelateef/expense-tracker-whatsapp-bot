from datetime import datetime
from sqlalchemy import func
from models import db, User, Expense
import json

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
    with open("messages.json", "r", encoding="utf-8") as file:
        messages = json.load(file)
    message = messages["expense_added"].format(date=expense.date.strftime("%d-%m-%Y"), amount=expense.amount, category=expense.category, description=expense.description)

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
        message += messages["budget_exceeded"].format(total_expenses=total_expenses, limit_amount=budget)
    else:
        message += messages["budget_ok"].format(total_expenses=total_expenses, limit_amount=budget)

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
    with open("messages.json", "r", encoding="utf-8") as file:
        messages = json.load(file)
    message = messages["limit_updated"].format(limit_amount=res["update_limit"]["limit_amount"], total_expenses=total_expenses)

    return message


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
    with open("messages.json", "r", encoding="utf-8") as file:
        messages = json.load(file)
    message = messages["view_limit"].format(limit_amount=budget, total_expenses=total_expenses)

    return message


def delete_all_expenses(user_phone):
    # Delete all expenses for the user
    db.session.query(Expense).filter_by(user_id=db.session.query(User).filter_by(user_phone=user_phone).first().id).delete()
    db.session.commit()

    # Prepare the response message
    with open("messages.json", "r", encoding="utf-8") as file:
        messages = json.load(file)
    message = messages["expenses_deleted"]

    return message


def delete_account(user_phone):
    # Delete all expenses for the user
    msg = delete_all_expenses(user_phone)
    # Delete the user account
    db.session.query(User).filter_by(user_phone=user_phone).delete()
    db.session.commit()

    # Prepare the response message
    with open("messages.json", "r", encoding="utf-8") as file:
        messages = json.load(file)
    message = messages["account_deleted"]

    return message


def help():
    with open("messages.json", "r", encoding="utf-8") as file:
        messages = json.load(file)
    return messages["help"]


def miscellaneous():
    with open("messages.json", "r", encoding="utf-8") as file:
        messages = json.load(file)
    return messages["miscellaneous"]