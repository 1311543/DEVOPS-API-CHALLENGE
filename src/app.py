from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask import current_app

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Eliam@localhost:3306/demo_db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Eliam@mysql-demo:3306/demo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

class Jobs(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

@app.route('/upload-csv/departments', methods=['POST'])
def upload_csv_departments():
    csv_path = '../dataset/departments.csv'
    headers = ["id", "name"]
    df = pd.read_csv(csv_path, header=None, names=headers)

    for index, row in df.iterrows():
        existing_department = Department.query.filter_by(id=row['id']).first()
        if existing_department is None:
            new_department = Department(id=int(row['id']), name=row['name'])
            db.session.add(new_department)

    # Commit the session to save all new departments to the database
    db.session.commit()
    return jsonify(
        {'success': True,
         'message': 'Departments uploaded successfully'})\
        , 200

@app.route('/upload-csv/jobs', methods=['POST'])
def upload_csv_jobs():
    csv_path = '../dataset/jobs.csv'
    headers = ["id", "name"]
    df = pd.read_csv(csv_path, header=None, names=headers)

    for index, row in df.iterrows():
        existing_job = Jobs.query.filter_by(id=row['id']).first()
        if existing_job is None:
            new_jobs = Jobs(id=int(row['id']), name=row['name'])
            db.session.add(new_jobs)

    # Commit the session to save all new departments to the database
    db.session.commit()
    return jsonify(
        {'success': True,
         'message': 'Jobs uploaded successfully'})\
        , 200

# def upload_csv_to_db(csv_file):
#     upload_csv_to_db('../dataset/departments.csv')
#     data = pd.read_csv(csv_file)
#     for _, row in data.iterrows():
#         department = Department(id=row['id'], name=row['name'])
#         db.session.merge(department)  # Usde merge to avoid duplicates
#     db.session.commit()


@app.route("/")
def index():
    csv_path = '../dataset/departments.csv'
    headers = ["id", "name"]
    df = pd.read_csv(csv_path, header=None, names=headers)
    print(df.columns)

    for index, row in df.iterrows():
        print(row)
        existing_department = Department.query.filter_by(id=row['id']).first()
        if existing_department is None:
            # Create a new Department instance for each row
            new_department = Department(id=int(row['id']), name=row['name'])
            db.session.add(new_department)

    # Commit the session to save all new departments to the database
    db.session.commit()
    return jsonify(
        {'success': True,
         'message': 'Departments uploaded successfully'})\
        , 200

if __name__ == '__main__':
    app.run(debug=True)