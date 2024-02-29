from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)


@app.route('/upload-csv/<table_name>', methods=['POST'])
def upload_csv(table_name):
    # CSV upload logic here
    pass

@app.route('/insert-batch/<table_name>', methods=['POST'])
def insert_batch(table_name):
    # Batch insert logic here
    pass

@app.route("/")
def index():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)