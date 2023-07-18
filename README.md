
# pysonweb-host

This project is a Python-based database management system that uses PysonDB and Flask to create, read, update, and delete (CRUD) records. PysonDB is a lightweight, simple-to-use JSON-based database that is ideal for small-to-medium-sized applications. Flask is a web framework that provides the necessary functionality to create a web-based application that can be used to manage data in the PysonDB database.

The system provides an easy-to-use web interface that allows users to interact with the database and perform CRUD operations. Users can add new records, edit existing records, delete records, and search for records based on various criteria. The interface is intuitive and user-friendly, making it easy for users with no programming experience to manage the database.


## Installation

- Installing pysonweb in a host machine

```
git clone https://github.com/tadiyusss/pysondb-web
cd pysondb-web
python3 app.py
```
    
- Installing pysonweb in a client machine 
 

```
git clone https://github.com/tadiyusss/pysondb-client
cd pysondb-client
mv pysonclient.py /path/to/project
```

After moving the client.py file you can now import it to your project

```
import pysonclient
```
## Server Usage
```
help - show this message
list - list all tables
create - <tbl_name> - create a table
drop - <tbl_name> - drop a table
insert - <tbl_name> <data:json> - insert data to a table
delete - <tbl_name> <search_query:json> - delete data from a table                      
search - <tbl_name> <search_query:json> - search data in a table (use "*" to get all data)
adduser - <username> <password> - add a user to the database
deluser - <username> - delete a user from the database
update - <tbl_name> <search_query:json> <update_data:json> - update data in a table
clear - clear the console
authorize - <tbl_name> <username> - authorize a user to a table
deauthorize - <tbl_name> <username> - deauthorize a user from a table         
```

## Client Usage

- Delete 

```
delete(tbl_name, search_query)
>>> {'status': 'success', 'message': 'x rows deleted from x', 'rows': x}
```

- Insert

```
insert(tbl_name, insert_data)
>>> {'data': "{'name': 'test'}", 'status': 'success', 'tbl_name': 'test'}
```

- Update

```
update(tbl_name, search_query, update_data)
>>> {'rows': 1, 'search_query': "{'name': 'test'}", 'status': 'success', 'tbl_name': 'test', 'update_data': "{'name': 'test2'}"}
```

- Search

```
search(tbl_name, search_query)
>>> {'data': [{'id': 167163754919151945, 'name': 'test'}], 'rows': 1, 'status': 'success', 'tbl_name': 'test'}
```

- Drop

```
drop(tbl_name)
>>> {'status': 'success', 'tbl_name': 'tbl_users'}
```

- Create

```
create(tbl_name)
>>> {'status': 'success', 'tbl_name': 'tbl_users'}
```

- List

```
list_tbl()
>>> {'data': ['test'], 'status': 'success', 'tables_count': 1}
```