from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask import current_app
from sqlalchemy import func, extract
from datetime import datetime
import subprocess
import os

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Eliam@localhost:3306/demo_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Eliam@mysql-demo3:3306/demo_db'
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
        date = datetime.strptime(row['hire_date'].rstrip('Z'), "%Y-%m-%dT%H:%M:%S") if pd.notnull(
            row['hire_date']) else None
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
         'message': 'Departments uploaded successfully'}) \
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
         'message': 'Jobs uploaded successfully'}) \
        , 200


@app.route('/employee-hires-2021')
def employee_hires_2021():
    """
    SELECT
    d.name AS Department,
    j.name AS Job,
    SUM(CASE WHEN QUARTER(e.hire_date) = 1 THEN 1 ELSE 0 END) AS Q1,
    SUM(CASE WHEN QUARTER(e.hire_date) = 2 THEN 1 ELSE 0 END) AS Q2,
    SUM(CASE WHEN QUARTER(e.hire_date) = 3 THEN 1 ELSE 0 END) AS Q3,
    SUM(CASE WHEN QUARTER(e.hire_date) = 4 THEN 1 ELSE 0 END) AS Q4
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    JOIN jobs j ON e.job_id = j.id
    WHERE YEAR(e.hire_date) = 2021
    GROUP BY d.name, j.name
    ORDER BY d.name, j.name;
    :return:
    """
    results = db.session.query(
        Department.name.label('department_name'),
        Jobs.name.label('job_name'),
        func.quarter(Employee.hire_date).label('quarter'),
        func.count().label('num_employees'))\
        .join(Employee.department)\
        .join(Employee.job)\
        .filter(func.year(Employee.hire_date) == 2021)\
        .group_by('department_name', 'job_name', 'quarter')\
        .all()

    df = pd.DataFrame(results, columns=['department_name', 'job_name', 'quarter', 'num_employees'])

    # Pivot the DataFrame
    pivot_df = df.pivot_table(
        index=['department_name', 'job_name'],
        columns='quarter',
        values='num_employees',
        fill_value=0,  # Fill missing values with 0
        aggfunc=sum  # Ensure the aggregation function is sum
    ).reset_index()

    # Rename columns for clarity
    pivot_df.columns = ['Department', 'Job', 'Q1', 'Q2', 'Q3', 'Q4']

    # Convert the pivoted DataFrame to a list of dictionaries for JSON response
    data = pivot_df.to_dict(orient='records')

    return jsonify(data)

@app.route('/departments/higher-than-average-hires')
def higher_than_average_hires():
    """
        SELECT
        d.id AS id,
        d.name AS department,
        COUNT(e.id) AS hired
    FROM
        departments d
    JOIN
        employees e ON d.id = e.department_id
    WHERE
        YEAR(e.hire_date) = 2021
    GROUP BY
        d.id, d.name
    HAVING
        COUNT(e.id) > (SELECT AVG(department_hires) FROM (
                            SELECT
                                COUNT(e.id) AS department_hires
                            FROM
                                employees e
                            WHERE
                                YEAR(e.hire_date) = 2021
                            GROUP BY
                                e.department_id
                       ) AS subquery)
    ORDER BY
        hired DESC;
    :return:
    """
    total_hires_and_departments = db.session.query(
        func.count(Employee.id).label('total_hires'),
        func.count(func.distinct(Employee.department_id)).label('num_departments')
    ).filter(extract('year', Employee.hire_date) == 2021).first()

    # Calculate the average hires per department in 2021
    avg_hires = (
                total_hires_and_departments.total_hires / total_hires_and_departments.num_departments) if total_hires_and_departments.num_departments else 0

    departments = db.session.query(
        Department.id,
        Department.name,
        func.count(Employee.id).label('hired'))\
        .join(Employee, Employee.department_id == Department.id)\
        .filter(extract('year', Employee.hire_date) == 2021)\
        .group_by(Department.id)\
        .having(func.count(Employee.id) > avg_hires)\
        .order_by(func.count(Employee.id).desc()
                  ).all()

    result = [{
        'id': d[0],
        'department': d[1],
        'hired': d[2]
    } for d in departments]

    return jsonify(result)

@app.route("/")
def index():
    # Define the path to the shell script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path, 'src', 'alembic_migrations.sh')

    try:
        # Run the shell script
        result = subprocess.run([script_path], check=True, text=True, capture_output=True)

        # If the script executes successfully, 'check=True' ensures that a non-zero exit
        # status raises a CalledProcessError. If the script succeeds, you can proceed.

        print("Script executed successfully.")
        print("Output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        # The script did not execute successfully
        print("Script execution failed.")
        print("Standard Error:\n", e.stderr)
        print("Standard Output (for debugging):\n", e.stdout)
    return jsonify(
        {'success': True,
         'message': 'just testing'}) \
        , 200


if __name__ == '__main__':
    app.run(debug=True)
