from flask import Flask, render_template

# Create Flask Instance
app = Flask(__name__)

# Index
@app.route("/")
def index():
    return "<h1>Hello World</h1>"