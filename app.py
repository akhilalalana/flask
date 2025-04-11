from flask import Flask, render_template, url_for
app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/join')
def join():
    return "this is the join form page"

@app.route("/participants")
def participants():
    return "list of participants"

if __name__ == "__main__":
    app.run(debug = True)