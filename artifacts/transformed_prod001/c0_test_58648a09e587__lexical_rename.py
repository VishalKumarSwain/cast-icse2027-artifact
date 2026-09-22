from flask import Flask, request, redirect, render_template

app_renamed = Flask(__name__)

@app_renamed.route('/')
def index():
    return render_template('index.html')

@app_renamed.route('/create')
def create_instrument():
    return render_template('create_instrument.html')

@app_renamed.route('/list_instruments')
def list_instruments():
    return "The new instrument has been created."

if __name__ == '__main__':
    app_renamed.run(debug=True)
