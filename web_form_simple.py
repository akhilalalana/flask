from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def info():
    if request.method == 'POST':
        name = request.form.get('name')
        Father_name = request.form.get('Father_name')
        email = request.form.get('email')
        city = request.form.get('city')
        country = request.form.get('country')
        phone = request.form.get('phone')

        print(
            f"Name: {name}, Father Name: {Father_name}, Email: {email}, City: {city}, Country: {country}, Phone: {phone}")

        return "Form submitted successfully!"

    return render_template('form1.html')  # This will render the HTML form if the method is GET.


if __name__ == '__main__':
    app.run(debug=True)
