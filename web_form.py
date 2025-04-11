from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def info():
    if request.method == 'POST':
        # Get the form data
        name = request.form['name']
        Father_name = request.form["Father_name"]
        email = request.form['email']
        city = request.form['city']
        country = request.form['country']
        phone = request.form['phone']

        # Print data to the console (You can store it in a database if needed)
        print(f"Name: {name},Father_name = {Father_name}, Email: {email}, City: {city}, Country: {country}, Phone: {phone}")

        # Return a success message to the user
        #return "Form submitted successfully"

    # For GET request, just show the form
        return render_template('form.html',
                           name = name,
                           Father_name=Father_name,
                           email=email,
                           city=city,
                           country=country,
                           phone=phone,
                           success = "form submitted succesfully")
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)
