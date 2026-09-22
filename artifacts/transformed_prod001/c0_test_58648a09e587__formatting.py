from flask import Flask, request, redirect, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create")
def create_instrument():
    return render_template("create_instrument.html")


@app.route("/list_instruments")
def list_instruments():
    return "The new instrument has been created."


if __name__ == "__main__":
    app.run(debug=True)
