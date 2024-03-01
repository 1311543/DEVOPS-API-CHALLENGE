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

# REQUEST FROM WINDOW

# GET  
Invoke-WebRequest -Uri http://127.0.0.1:8081 -Method Get


### Define the URI
$uri = 'http://127.0.0.1:8081'

### Create a hashtable for your form data or JSON payload
$body = @{
    key1 = 'value1'
    key2 = 'value2'
} | ConvertTo-Json

### Send the POST request
$response = Invoke-WebRequest -Uri $uri -Method Post -Body $body -ContentType 'application/json'

### Output the response content
$response.Content


## DOCKERIZATION
docker build -t francisjosue/globant-api:latest .
docker run -p 8080:8080 francisjosue/globant-api
docker exec -it -p 8080:8080 francisjosue/globant-api bash

## 
docker tag francisjosue/globant-api:latest francisjosue/globant-api:1.0.0
Docker push francisjosue/globant-api:1.0.0
