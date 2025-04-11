from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session-based authentication

# Hardcoded user credentials for simplicity (for Postman and URL verification)
users = {
    'admin@example.com': 'password123'}

class Database:
    def __init__(self, db_name):
        self.db_name = db_name

    def create_table(self):
        """Create the participants table if it doesn't exist"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS participants (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,  
                            name TEXT, 
                            Father_name TEXT, 
                            email TEXT UNIQUE,  
                            city TEXT, 
                            country TEXT, 
                            phone TEXT)''')
        conn.commit()
        conn.close()

    def insert_data(self, name, Father_name, email, city, country, phone):
        """Insert a new participant into the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO participants (name, Father_name, email, city, country, phone)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (name, Father_name, email, city, country, phone))
            conn.commit()
            conn.close()
            return "success"
        except sqlite3.IntegrityError:
            conn.close()
            return "email_exists"

    def get_all_data(self):
        """Retrieve all participants from the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM participants')
        data = cursor.fetchall()
        conn.close()
        return data

    def get_participant(self, id):
        """Retrieve a single participant by ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM participants WHERE id = ?", (id,))
        participant = cursor.fetchone()
        conn.close()
        return participant


# Initialize Database
db = Database('database.db')
db.create_table()  # Create the table when the app starts

def is_logged_in():
    """Check if the user is logged in."""
    return 'user' in session

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Login page to authenticate users."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        print(f"Attempting to login with email: {email} and password: {password}")  # Debug line

        # Check if email and password match
        if email in users and users[email] == password:
            session['user'] = email  # Store the email in the session
            flash("Login successful!", "success")
            return redirect(url_for('form'))  # Redirect to the form page (or any protected page)
        else:
            flash("Invalid email or password", "error")

    return render_template('login.html')



@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration page to create new users."""
    if request.method == "POST":
        data = request.form  # Dictionary of form data

        print(data)
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check if the username already exists
        if email in users:
            flash("Username already exists! Please choose a different username.", "error")
        elif password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
        else:
            # Store the new user's password (you should hash the password in a real app)
            users[email] = password
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    """Logout the user by clearing the session."""
    session.pop('user', None)
    flash("You have been logged out", "success")
    return redirect(url_for('login'))


@app.route("/form", methods=['GET', 'POST'])
def form():
    """Form page for submitting data"""
    if not is_logged_in():
        return redirect(url_for('login'))  # Redirect to login if not logged in


    if request.method == 'POST':
        name = request.form['name']
        Father_name = request.form['Father_name']
        email = request.form['email']
        city = request.form['city']
        country = request.form['country']
        phone = request.form['phone']

        result = db.insert_data(name, Father_name, email, city, country, phone)

        if result == "email_exists":
            flash("Email already exists! Use a different email.", "error")
        else:
            flash("Participant added successfully!", "success")
            return redirect("/submitted")

    return render_template('form1.html')


@app.route("/participant/<int:id>", methods=['GET'])
def get_participant(id):
    """Fetch a participant's details by ID"""
    if not is_logged_in():
        return redirect(url_for('login'))

    participant = db.get_participant(id)

    if participant:
        return jsonify({
            "id": participant[0],
            "name": participant[1],
            "Father_name": participant[2],
            "email": participant[3],
            "city": participant[4],
            "country": participant[5],
            "phone": participant[6]
        })
    else:
        return jsonify({"error": "Participant not found"}), 404


@app.route("/submitted", methods=['GET'])
def submitted():
    """Show all participants"""
    if not is_logged_in():
         return redirect(url_for('login'))

    data = db.get_all_data()

    participants_list = []
    for p in data:
        participants_list.append({
            "id": p[0],
            "name": p[1],
            "Father_name": p[2],
            "email": p[3],
            "city": p[4],
            "country": p[5],
            "phone": p[6]
        })

    return jsonify(participants_list)


# Routes for update and delete (with session-based authentication)
@app.route("/participant/update/<int:id>", methods=['GET', 'POST'])
def update_participant(id):
    if not is_logged_in():
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM participants WHERE id = ?", (id,))
    participant = cursor.fetchone()

    if participant is None:
        conn.close()
        return "Participant not found", 404

    if request.method == 'POST':
        name = request.form['name']
        Father_name = request.form['Father_name']
        email = request.form['email']
        city = request.form['city']
        country = request.form['country']
        phone = request.form['phone']

        try:
            cursor.execute('''UPDATE participants SET 
                            name = ?, Father_name = ?, email = ?, 
                            city = ?, country = ?, phone = ? 
                            WHERE id = ?''',
                           (name, Father_name, email, city, country, phone, id))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already exists.", 400

        conn.close()
        return redirect(f"/participant/{id}")  # Redirect to the participant's details page after update

    conn.close()
    return render_template('update_participant.html', participant=participant)


@app.route("/participant/delete/<int:id>", methods=['DELETE'])
def delete_participant(id):
    if not is_logged_in():
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM participants WHERE id = ?", (id,))
    participant = cursor.fetchone()

    if participant:
        cursor.execute("DELETE FROM participants WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Participant with ID {id} deleted successfully"}), 200
    else:
        conn.close()
        return jsonify({"error": "Participant not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
