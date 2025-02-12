from models import User, Expense
import json
import logging


logging.basicConfig(level=logging.ERROR, filename="app.log", filemode="a")
logger = logging.getLogger(__name__)

def add_expense(user_phone, res):
    try:
        user = User.get_user_by_phone(user_phone)
        if int(res["add_expense"].get("amount", 0))<=0:
            return "Expense should be positive!"
        expense = Expense.create_expense(
            user_id=user.id,
            category=res["add_expense"].get("category", "").lower(),
            amount=res["add_expense"].get("amount", 0),
            description=res["add_expense"].get("description", "").lower(),
        )

        with open("texts/messages.json", "r", encoding="utf-8") as file:
            messages = json.load(file)

        message = messages.get("expense_added", "Expense added: {amount} in {category}").format(
            date=expense.date.strftime("%d-%m-%Y"), amount=expense.amount, category=expense.category, description=expense.description
        )

        budget = user.limit_amount
        total_expenses = Expense.get_current_month_total_expenses(user.id)

        if total_expenses > budget:
            message += messages.get("budget_exceeded", " Warning: Budget exceeded.").format(
                total_expenses=total_expenses, limit_amount=budget
            )
        else:
            message += messages.get("budget_ok", " Budget is within limits.").format(
                total_expenses=total_expenses, limit_amount=budget
            )

        return message
    except Exception as e:
        logger.error(f"Error adding expense: {str(e)}")
        return None


def update_limit(user_phone, res):
    try:
        user = User.update_user_limit(user_phone, res["update_limit"].get("limit_amount", 0))

        total_expenses = Expense.get_current_month_total_expenses(user.id)

        with open("texts/messages.json", "r", encoding="utf-8") as file:
            messages = json.load(file)

        message = messages.get("limit_updated", "Limit updated.").format(
            limit_amount=res["update_limit"].get("limit_amount", 0), total_expenses=total_expenses
        )

        return message
    except Exception as e:
        logger.error(f"Error updating limit: {str(e)}")
        return None


def view_limit(user_phone):
    try:
        budget = User.get_user_limit(user_phone)

        total_expenses = Expense.get_current_month_total_expenses(User.get_user_by_phone(user_phone).id)

        with open("texts/messages.json", "r", encoding="utf-8") as file:
            messages = json.load(file)

        return messages.get("view_limit", "View limit: {limit_amount}").format(
            limit_amount=budget, total_expenses=total_expenses
        )
    except Exception as e:
        logger.error(f"Error viewing limit: {str(e)}")
        return None


def delete_all_expenses(user_phone):
    try:
        user = User.get_user_by_phone(user_phone)

        Expense.delete_all_expenses(user.id)

        with open("texts/messages.json", "r", encoding="utf-8") as file:
            messages = json.load(file)

        return messages.get("expenses_deleted", "All expenses deleted.")
    except Exception as e:
        logger.error(f"Error deleting expenses: {str(e)}")
        return None


def delete_account(user_phone):
    try:
        msg = delete_all_expenses(user_phone)
        User.delete_user(user_phone)

        with open("texts/messages.json", "r", encoding="utf-8") as file:
            messages = json.load(file)

        return messages.get("account_deleted", "Account deleted.")
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        return None


def help():
    try:
        with open("texts/messages.json", "r", encoding="utf-8") as file:
            messages = json.load(file)
        return messages.get("help_message", "Sorry, Please try again after some time.")
    except Exception as e:
        logger.error(f"Error retrieving help message: {str(e)}")
        return None


def miscellaneous():
    try:
        with open("texts/messages.json", "r", encoding="utf-8") as file:
            messages = json.load(file)
        return messages.get("miscellaneous", "Sorry, Please try again after some time.")
    except Exception as e:
        logger.error(f"Error retrieving miscellaneous message: {str(e)}")
        return None
