from flask import Flask
from flask_login import LoginManager
from src.models.user import User
from src.routes.auth_routes import auth_bp
from src.routes.finance_routes import finance_bp

# ---------- Create FLASK application ----------
app = Flask(__name__)
app.secret_key = "secret123"    # Secret key used for session management


# ---------- Configure FLASK login ----------
login_manager = LoginManager()
login_manager.login_view = "auth.login" # Redirect unauthenticated users to the login page
login_manager.init_app(app) # Initialize Flask-Login with the Flask app


# ---------- USER LOADER ----------
# Called automatically by Flask-Login to reload the logged-in user from the session.
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# ---------- Authentication routes (Login, Register, Logout) ----------
app.register_blueprint(auth_bp)


# ---------- Finance routes (Dashboard, Transactions, Savings, Categories) ----------
app.register_blueprint(finance_bp)


# ---------- Run theApplication ----------
if __name__ == "__main__":
    app.run(debug=True) # Start the Flask development server