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
* the table collects the most up-to-date records about each company from tables **or_podanie_issues**, **znizenie_imania_issues**, **likvidator_issues**, **konkurz_vyrovnanie_issues**, **konkurz_restrukturalizacia_actors** upon its creation during migration

2. GET request handling and stats

* another API endpoint was created to work with the new table
* GET functionality is similar to the ov/submissions/ API  - full-text search on columns *name* and *address_line*
* for each company, the GET response contains numbers of its occurences in each of the main tables
* ordering can be done by any of the returned columns



Fourth part (request handling written using ORM):

ORM models were created for all of the tables from the database. This was done when those tables had already existed in the database, so the migration *0003_orm* was faked in order to not let the database attempt creating an already existing table. 

IMPORTANT: migration *0003_orm* has to be faked via **py manage.py migrate --fake app 0003_orm**

/v2/ov/submissions/

1. GET request handling - now implemented using Django ORM

- [same as v1] paging via page and per_page
- [same as v1] result ordering via order_by and order_type
- [same as v1] date filtering via registration_date_lte and registration_date_gte
- [same as v1] full-text search on columns *corporate_body_name*, *cin*, *city*
- [new] when an id is specified at the end of the URL (v2/submissions/*id*), a single matching record is returned

2. POST request handling - now implemented using Django ORM

- [same as v1] validation of input fields, reasons are returned in case of an error
- [same as v1] new records with required references are created in tables **or_podanie_issues**, **raw_issues**, **bulletin_issues**

3. DELETE request handling - now implemented using Django ORM

- removal of the record specified by its id from table **or_podanie_issues**
- removal of referenced records in tables **raw_issues** and **bulletin_issues**, if possible (no other references remain)

4. [NEW] PUT request handling implemented using Django ORM

* validation of input fields, reasons are returned in case of an error
* it is possible to update only some of the fields of the record, however, at least one of the available fields has to be specified in order for the update operation to succeed
* an existing record with requested id  in table **or_podanie_issues** is updated according to the values specified in the request body

/v2/companies/

1. GET request handling - now implemented using Django ORM

* [same as v1] request functionality is similar to the ov/submissions/ API  - full-text search on columns *name* and *address_line*
* [same as v1] for each company, the GET response contains numbers of its occurences in each of the main tables
* [same as v1] ordering can be done by any of the returned columns

