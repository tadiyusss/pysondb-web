
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

After moving the client.py file you can now import it to your projection

```
import pysonclient
```
## Server Usage
```
help - show this message
list - list all tables
create - <tbl_name> - create a table
drop - <tbl_name> - drop a table
insert - <tbl_name> <data> - insert data to a table
delete - <tbl_name> <search_query> - delete row to a table
search - <tbl_name> <search_query> - search data in a table (use "*" to get all data)
adduser - <username> <password> - add a user to the database
deluser - <username> - delete a user from the database
update - <tbl_name> <search_query> <update_data> - update data in a table
clear - clear the console
```

## Client Usage


- Insert
Insert data to table
```
insert(tbl_name, insert_data)
>>> {'data': "{'name': 'test'}", 'status': 'success', 'tbl_name': 'test'}
```

- Delete
Delete data from table
```
delete(tbl_name, search_query)
>>> {'data': 1, 'message': 'Data removed', 'status': 'success'}
```

- Update
Update data from table
```
update(tbl_name, search_query, update_data)
>>> {'rows': 1, 'search_query': "{'name': 'test'}", 'status': 'success', 'tbl_name': 'test', 'update_data': "{'name': 'test2'}"}
```

- Search
Search data on table
```
search(tbl_name, search_query)
>>> {'data': [{'id': 167163754919151945, 'name': 'test'}], 'rows': 1, 'status': 'success', 'tbl_name': 'test'}
```

- Drop
Drop a table
```
drop(tbl_name)
>>> {'status': 'success', 'tbl_name': 'tbl_users'}
```

- Create
Create a table
```
create(tbl_name)
>>> {'status': 'success', 'tbl_name': 'tbl_users'}
```

- List
List all available tables
```
list_tbl()
>>> {'data': ['test'], 'status': 'success', 'tables_count': 1}
```