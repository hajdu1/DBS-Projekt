# DBS project 

### Jakub Hajdu

Python **Django** framework application working with a **PostgreSQL** database containing a modified snapshot of the Slovak Business Register.

The database itself is not included here for its large size. 



First part: 

/v1/health/ 

* returns the uptime of the connected database server



Second part (API to access table or_podanie_issues): 

/v1/ov/submissions/

1. GET request handling

- paging via page and per_page
- result ordering via order_by and order_type
- date filtering via registration_date_lte and registration_date_gte
- full-text search on columns *corporate_body_name*, *cin*, *city*

2. POST request handling

- validation of input fields, reasons are returned in case of an error
-  new records with required references are created in tables **or_podanie_issues**, **raw_issues**, **bulletin_issues**

3. DELETE request handling

- removal of the record specified by its id from table **or_podanie_issues**
- removal of referenced records in tables **raw_issues** and **bulletin_issues**, if possible (no other references remain)



Third part (normalization and statistics):

/v1/companies/

1. Normalization

* table **companies** is created via migration *0002_companies*
* the table collects the most up-to-date records about each company

2. Stats

* another API was created to work with the new table
* GET functionality is similar to the API from the second part
* for each company, the GET response contains numbers of its occurences in each of the main tables



[To be added] Fourth part (ORM and PUT request handling)