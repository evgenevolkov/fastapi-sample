# Sample FastAPI backend project for notetaking app

A user, once registered, can create, view, search for or delete their own text notes

## Features:
1. __Access control:__ 
    *    A user needs to login prior to use the app 
    *    A user account can only be deleted by the user themselves

2. __Role-based access__ with 2 roles:
    * __End user__ - can create, see or drop own text entries only
    * __Admin__ - can view all users and all records

3. __Notes search and filter:__
    * __Search by name__: a user can search for notes by providing part of a note's name (substring)
    * __Limit output__: a user can define a number of entries to view
    * __Skip entries__: a user can set a number of the first entries to skip, allowing to view entries or search results starting from an arbitrary point in the list

## Implementation details:

__Access validation relies on JWT__ to keep the backend stateless thus reducing complexity

__Data validation and type checking__ to increase reliability and readability

__Implemented database modeling__ (defining tables and relationships) to streamline project setting up and ensure allignment between database schema and Python code


## Tech stack:
* Language: __Python__
* Famework: __FastAPI__
* Access control: __JWT__
* Data validation: __Pydantic__
* Databasing: __PostgreSQL, SQLAlchemy__

## Installation:

1. Clone project repo: `git clone https://github.com/evgenevolkov/fastapi-sample.git`
2. Create a virtual environment:
    1. On Mac / Linux: `python3 -m venv .venv`
    2. On Windows: `python -m venv .venv`
3. Activate virtual environment:
    1. On Mac / Linux: `source .venv/bin/activate`
    2. On Windows: `.venv\Scripts\activate`
4. Install required dependencies: `pip install -r requirements.txt`
5. Install PostgreSQL. Refer to PostgreSQL [official docs](https://www.postgresql.org/download) for reference. 
6. Create a database for the project, preferably named `fastapi_sample` 
7. In a project folder rename a `.env.template` file to `.env`. Fill in the Postgres username and password.

## Running:
1. To start project, open terminal in the  project folder and execute  `uvicorn app.app:app --reload` 
2. This is a back-end project, so to test it you have several options:
    1. Use in-built FastAPI docs 
       by opening http://localhost:8000/docs
    2. A more convenient way is to install [Postman](http://www.postman.com) and use provided `fastapi_sample.postman_collection.json` file with  collection of API calls
    3. Implement own front-end 

## Testing 
To run tests you would need to: 
1. Create another one database in Postgres named `fastapi_sample_test` with the same username and password as the main database
2. From project folder run `pytest`

## Enjoy:)