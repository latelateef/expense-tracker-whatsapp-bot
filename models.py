from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Initialize the database
db = SQLAlchemy()

# Configure logging
logging.basicConfig(level=logging.ERROR, filename='app.log', filemode='a')
logger = logging.getLogger(__name__)

def init_app(app):
    db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_phone = db.Column(db.String(20), unique=True, nullable=False)
    limit_amount = db.Column(db.Float, nullable=False)
    state = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<User {self.user_phone}, Limit: {self.limit_amount}>"

    @staticmethod
    def create_user(user_phone, limit_amount, state=None):
        try:
            new_user = User(user_phone=user_phone, limit_amount=limit_amount, state=state)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database Error: {e}")
            return None

    @staticmethod
    def get_user_by_phone(user_phone):
        try:
            return User.query.filter_by(user_phone=user_phone).first()
        except SQLAlchemyError as e:
            logger.error(f"Database Error: {e}")
            return None

    @staticmethod
    def update_user_limit(user_phone, new_limit):
        """
        Updates the budget limit for a user.
        """

        user = User.get_user_by_phone(user_phone)

        try:
            user.limit_amount = new_limit
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database Error: {e}")
            return None

    @staticmethod
    def get_user_limit(user_phone):
        """
        Retrieves the budget limit for a user.
        """
        user = User.get_user_by_phone(user_phone)

        return user.limit_amount

    @staticmethod
    def delete_user(user_phone):
        """
        Deletes a user by phone number.
        """
        user = User.get_user_by_phone(user_phone)

        try:
            db.session.delete(user)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database Error: {e}")
            return None

    @staticmethod
    def set_user_state(user_phone, state):
        user = User.get_user_by_phone(user_phone)
        user.state = state
        db.session.commit()

    @staticmethod
    def reset_user_state(user_phone):
        user = User.get_user_by_phone(user_phone)
        user.state = None
        db.session.commit()

def get_date_time():
    return datetime.now()

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime, default=get_date_time, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Expense {self.category}, Amount: {self.amount}, User ID: {self.user_id}, Date: {self.date}>"

    @staticmethod
    def create_expense(category, amount, user_id, description=None):
        """
        Creates a new expense after validating input data.
        """

        try:
            new_expense = Expense(category=category, amount=amount, user_id=user_id, description=description,
                                  date=get_date_time())
            db.session.add(new_expense)
            db.session.commit()
            return new_expense
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            logger.error(f"Database Error: {e}")
            return None

    @staticmethod
    def get_current_month_total_expenses(user_id):
        """
        Retrieves the total expenses for the current month.
        """
        current_month = datetime.now().month
        current_year = datetime.now().year

        try:
            total_expenses = (
                db.session.query(db.func.sum(Expense.amount))
                .filter(
                    db.func.extract("month", Expense.date) == current_month,
                    db.func.extract("year", Expense.date) == current_year,
                    Expense.user_id == user_id,
                )
                .scalar()
            )
            return total_expenses if total_expenses else 0
        except SQLAlchemyError as e:
            logger.error(f"Database Error: {e}")
            return None

    @staticmethod
    def delete_all_expenses(user_id):
        """
        Deletes all expenses for a given user.
        """
        try:
            Expense.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database Error: {e}")
            return None
