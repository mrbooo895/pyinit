from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello from your new Flask app, ##PROJECT_NAME##!</p>"

# To run this app:
# 1. pip install -e .
# 2. flask run
