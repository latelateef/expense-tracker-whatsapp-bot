from models import db, User


def get_user_state(user_phone):
    # Retrieve the state from the database or session
    user = db.session.query(User).filter_by(user_phone=user_phone).first()
    return user.state if user else None

def set_user_state(user_phone, state):
    # Store the state in the database or session
    user = db.session.query(User).filter_by(user_phone=user_phone).first()
    if user:
        user.state = state
        db.session.commit()

def reset_user_state(user_phone):
    # Reset the user state after the confirmation process
    user = db.session.query(User).filter_by(user_phone=user_phone).first()
    if user:
        user.state = None  # or some default state
        db.session.commit()
