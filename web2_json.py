from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
@app.route("/", methods = [ 'POST'])
def info():
        data = request.get_json()
        if not data:
            return jsonify({"error" : "no data received"}), 400

        name = data.get('name')
        Father_name = data.get('Father_name')
        email = data.get('email')
        city = data.get('city')
        country = data.get('country')
        phone = data.get('phone')
        print(f"Name: {name},Father_name :{Father_name} Email: {email}, City: {city}, Country: {country}, Phone: {phone}")
        if not all([name, Father_name, email, city, country, phone]):
            return jsonify({"error": "Missing data"}), 400

        response_data = {
            "success": "Form submitted successfully",
            "submitted_data": data  # Returning the received JSON data
        }

        return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(debug = True)