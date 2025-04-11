from flask import Flask, render_template, request, redirect, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flash messages


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

    def get_all_data(self):
        """Retrieve all participants from the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM participants')
        data = cursor.fetchall()
        conn.close()
        return data


# Initialize Database
db = Database('database.db')
db.create_table()  # Create the table when the app starts


@app.route("/", methods=['GET', 'POST'])
def form():
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

@app.route("/participant/update/<int:id>", methods=['GET', 'POST'])
def update_participant(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Get the participant's current data
    cursor.execute("SELECT * FROM participants WHERE id = ?", (id,))
    participant = cursor.fetchone()

    # If the participant doesn't exist, return a 404 error
    if participant is None:
        conn.close()
        return "Participant not found", 404

    if request.method == 'POST':
        # Get updated data from the form
        name = request.form['name']
        Father_name = request.form['Father_name']
        email = request.form['email']
        city = request.form['city']
        country = request.form['country']
        phone = request.form['phone']

        # Update participant data in the database
        try:
            cursor.execute('''UPDATE participants SET 
                            name = ?, Father_name = ?, email = ?, 
                            city = ?, country = ?, phone = ? 
                            WHERE id = ?''',
                           (name, Father_name, email, city, country, phone, id))
            conn.commit()
        except sqlite3.IntegrityError:
            # Handle the case where the email already exists in the database
            conn.close()
            return "Email already exists.", 400

        conn.close()
        return redirect(f"/participant/{id}")  # Redirect to the participant's details page after update

    conn.close()
    return render_template('update_participant.html', participant=participant)

@app.route("/participant/delete/<int:id>", methods=['DELETE'])
def delete_participant(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Check if the participant exists
    cursor.execute("SELECT * FROM participants WHERE id = ?", (id,))
    participant = cursor.fetchone()

    if participant:
        # Delete the participant
        cursor.execute("DELETE FROM participants WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Participant with ID {id} deleted successfully"}), 200
    else:
        conn.close()
        return jsonify({"error": "Participant not found"}), 404




# @app.route("/submitted", methods = ['get'])
# def submitted():
#      data = db.get_all_data()
#      return render_template('participants.html', data=data)
#
@app.route("/submitted", methods=['GET'])
def submitted():
    # Fetch all participants from the database
    data = db.get_all_data()

    # Prepare the data as a list of dictionaries for JSON format
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

    return jsonify(participants_list)  # Return the list of participants as JSON

if __name__ == '__main__':
    app.run(debug=True)
