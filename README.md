# DEVOPS-API-CHALLENGE
## Instalation
## Installation
1. Clone the repository and navigate into the project directory.
2. Set up a virtual environment and activate it.
3. Install dependencies: `pip install -r requirements.txt`.
4. Initialize the database with Alembic: `alembic upgrade head`.
5. Run the Flask app: `python app.py`.

**3. Install dependencies **
api.py
`python -m venv venv`

`venv\Scripts\activate`

`pip install -r requirements.txt`

**1. SET UP IN YOUR PYTHON PROJECT WORKSPACE**

## Usage
- **Upload CSV**: POST `/upload-csv/<table_name>` with a multipart/form-data request containing the CSV file.
- **Batch Insert**: POST `/insert-batch/<table_name>` with JSON payload.
