from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask import current_app
from datetime import datetime

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

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    hire_date = db.Column(db.DateTime, nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)

    job = db.relationship('Jobs', backref='employees')
    department = db.relationship('Department', backref='employees')

class EmployeeAudit(db.Model):
    __tablename__ = 'employee_audit'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    hire_date = db.Column(db.DateTime, nullable=True)
    missing_fields = db.Column(db.String(255), nullable=False)

@app.route('/upload-csv/employees', methods=['POST'])
def upload_csv_employees():
    csv_path = '../dataset/hired_employees.csv'
    headers = ["id", "name", "hire_date", "department_id", "job_id"]
    df = pd.read_csv(csv_path, header=None, names=headers)

    for index, row in df.iterrows():
        name = row['name'] if pd.notnull(row['name']) else "NONAME"

        department_id = row['department_id'] if pd.notnull(row['department_id']) else None
        job_id = row['job_id'] if pd.notnull(row['job_id']) else None
        missing_fields = []

        if job_id is None:
            missing_fields.append('job_id')
        if department_id is None:
            missing_fields.append('department_id')
        date = datetime.strptime(row['hire_date'].rstrip('Z'), "%Y-%m-%dT%H:%M:%S") if pd.notnull(row['hire_date']) else None
        if missing_fields:
            print("sending rows with null {}".format(missing_fields))
            audit_entry = EmployeeAudit(
                employee_id=row['id'],
                name=row['name'],
                hire_date=date,
                missing_fields=', '.join(missing_fields)
            )
            db.session.add(audit_entry)
        else:
            existing_employee = Employee.query.filter_by(id=row['id']).first()
            if existing_employee is None:
                new_employee = Employee(
                    id=row['id'],
                    name=name,
                    hire_date=date,
                    department_id=int(department_id),  # Cast to int, assuming the column is not null
                    job_id=int(job_id)  # Cast to int, assuming the column is not null
                )
                db.session.add(new_employee)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Employees uploaded successfully'}), 200


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