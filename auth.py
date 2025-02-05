from flask import render_template, request, flash, redirect, session, Blueprint
from app import mysql, bcrypt  # Import app-related extensions from app.py, not app itself

# Create a Blueprint for auth routes
auth_bp = Blueprint('auth', __name__)

# Define the login route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        
        if user and bcrypt.check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Login successful!", "success")
            return redirect('/home')  # Redirect to home page after login
        else:
            flash("Invalid email or password!", "danger")
    
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            cur = mysql.connection.cursor()

            # Check if email or username already exists
            cur.execute("SELECT * FROM users WHERE email = %s OR username = %s", (email, username))
            existing_user = cur.fetchone()

            if existing_user:
                flash("Email or Username already registered! Please login.", "danger")
                return redirect('/auth/login')

            # Insert user credentials into the database
            cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", 
                        (username, email, password_hash))
            mysql.connection.commit()

            flash("Signup successful! Please login.", "success")
            return redirect('/auth/login')

        except Exception as e:
            flash(f"Error during signup process: {str(e)}", "danger")
            return render_template('signup.html')
        finally:
            cur.close()  # Always close the cursor
    return render_template('signup.html')

# Define the logout route
@auth_bp.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect('/auth/login')  # Redirect to login page after logout
