#!/usr/bin/python3

from pysondb import getDb
from flask import Flask, request, jsonify
from tabulate import tabulate
import getpass
import ast
import hashlib
import pysondb
import threading
import os 
import sys
import re
import random
import string

def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def hash_password(password):
    salt = random_string(32)
    salted_password = password + salt
    return {
        'salt': salt,
        'password': hashlib.sha256(salted_password.encode()).hexdigest()
    }

if os.path.isdir('tables') == False:
    os.mkdir('tables')
if os.path.isdir('data') == False:
    os.mkdir('data')
if os.path.isfile('data/users.json') == False:
    print('No users found, creating a new user...')
    username = input('Enter a username: ')
    password = getpass.getpass('Enter a password: ')
    hashed_password = hash_password(password)
    getDb('data/users.json').add({'username': username, 'password': hashed_password['password'], 'salt': hashed_password['salt'], 'authorized_tbl': []})

app = Flask(__name__)

class UserHandler:
    def deauthorize_user(self, username, table_name):
        data = getDb('data/users.json').getByQuery({'username': username})
        if len(data) == 0:
            return {
                'status': 'error',
                'message': 'User not found'
            }
        if table_name not in data[0]['authorized_tbl']:
            return {
                'status': 'error',
                'message': f'User not authorized to table {table_name}'
            }
        data[0]['authorized_tbl'].remove(table_name)
        getDb('data/users.json').updateById(data[0]['id'], {'authorized_tbl': data[0]['authorized_tbl']})
        return {
            'status': 'success',
            'message': f'User deauthorized from table {table_name}'
        }
    def authorize_user(self, username, table_name):
        data = getDb('data/users.json').getByQuery({'username': username})
        if len(data) == 0:
            return {
                'status': 'error',
                'message': 'User not found'
            }
        if table_name not in TableHandler().list_tables():
            return {
                'status': 'error',
                'message': 'Table not found'
            }
        if table_name in data[0]['authorized_tbl']:
            return {
                'status': 'error',
                'message': f'User already authorized to table {table_name}'
            }
        data[0]['authorized_tbl'].append(table_name)
        getDb('data/users.json').updateById(data[0]['id'], {'authorized_tbl': data[0]['authorized_tbl']})
        return {
            'status': 'success',
            'message': f'User authorized to table {table_name}'
        }
    
    def check_user_validity(self, username, password):
        data = getDb('data/users.json').getByQuery({'username': username})
        if len(data) == 0:
            return False
        salt = data[0]['salt']
        hashed_password = data[0]['password']
        salted_password = password + salt
        return hashlib.sha256(salted_password.encode()).hexdigest() == hashed_password
    
    def check_table_authorization(self, table, username):
        data = getDb('data/users.json').getByQuery({'username': username})
        if len(data) == 0:
            return False
        if table not in data[0]['authorized_tbl']:
            return False
        return True
    
    def create_user(self, username, password):
        hashed_password = hash_password(password)
        if len(getDb('data/users.json').getByQuery({'username': username})) != 0:
            return {
                'status': 'error',
                'message': 'Username already exists'
            }
        getDb('data/users.json').add({'username': username, 'password': hashed_password['password'], 'salt': hashed_password['salt'], 'authorized_tbl': []})
        return {
            'status': 'success',
            'message': 'User created'
        }
    
    def delete_user(self, username):
        if len(getDb('data/users.json').getByQuery({'username': username})) == 0:
            return {
                'status': 'error',
                'message': 'User not found'
            }
        getDb('data/users.json').deleteById(getDb('data/users.json').getByQuery({'username': username})[0]['id'])
        return {
            'status': 'success',
            'message': 'User deleted'
        }

class TableHandler:
    def list_tables(self):
        data = os.listdir('tables')
        files = []
        for file in data:
            if file.endswith('.json'):
                files.append(file[:-5])  
        return files
    
    def create_table(self, table_name):
        if table_name in self.list_tables():
            return {
                'status': 'error',
                'message': 'Table already exists'
            }
        try:
            getDb(f'tables/{table_name}.json')
        except OSError:
            return {
                'status': 'error',
                'message': 'Invalid table name'
            }
        return {
            'status':'success',
            'message': f'Table {table_name} created',
        }
    
    def delete_table(self, table_name):
        if table_name not in self.list_tables():
            return {
                'status': 'error',
                'message': 'Table not found'
            }
        os.remove(f'tables/{table_name}.json')
        return {
            'status':'success',
            'message': f'Table {table_name} deleted',
        }
    
    def insert_data(self, table_name, data):
        if table_name not in self.list_tables():
            return {
                'status': 'error',
                'message': 'Table not found'
            }
        table = getDb(f'tables/{table_name}.json')
        try:
            table.add(data)
        except Exception as e:
            return {
                'status': 'error',
                'message': 'Invalid data type'
            }
        
        return {
            'status':'success',
            'message': f'Data inserted to {table_name}'
        }
    
    def search_data(self, table_name, search_query):
        if table_name not in self.list_tables():
            return {
                'status': 'error',
                'message': 'Table not found'
            }
        table = getDb(f'tables/{table_name}.json')
        if type(search_query) != dict and search_query != '*' and search_query != 'all':
            return {
                'status': 'error',
                'message': 'Search query must be a dictionary'
            }
        if search_query == '*' or search_query == 'all':
            data = table.getAll()
        else:
            data = table.getByQuery(search_query)
        return {
            'status': 'success',
            'message': f'{len(data)} rows found',
            'rows': len(data),
            'data': data
        }

    def delete_data(self, table_name, search_query):
        if table_name not in self.list_tables():
            return {
                'status': 'error',
                'message': 'Table not found'
            }
        if type(search_query) != dict:
            return {
                'status': 'error',
                'message': 'Search query must be a dictionary'
            }
        data = self.search_data(table_name, search_query)
        if data['rows'] == 0:
            return {
                'status': 'error',
                'message': 'No rows found'
            }
        table = getDb(f'tables/{table_name}.json')
        for row in data['data']:
            table.deleteById(row['id'])
        return {
            'status': 'success',
            'message': f'{data["rows"]} rows deleted from {table_name}',
            'rows': data['rows']
        }
    
    def delete_data(self, table_name, search_query):
        if table_name not in self.list_tables():
            return {
                'status': 'error',
                'message': 'Table not found'
            }
        if type(search_query) != dict:
            return {
                'status': 'error',
                'message': 'Search query must be a dictionary'
            }
        data = self.search_data(table_name, search_query)
        if data['rows'] == 0:
            return {
                'status': 'error',
                'message': 'No rows found'
            }
        table = getDb(f'tables/{table_name}.json')
        for row in data['data']:
            table.deleteById(row['id'])
        return {
            'status': 'success',
            'message': f'{data["rows"]} rows deleted from {table_name}',
            'rows': data['rows']
        }
    
    def update_data(self, table_name, search_query, update_data):
        if table_name not in self.list_tables():
            return {
                'status': 'error',
                'message': 'Table not found'
            }
        if type(search_query) != dict:
            return {
                'status': 'error',
                'message': 'Search query must be a dictionary'
            }
        if type(update_data) != dict:
            return {
                'status': 'error',
                'message': 'Update data must be a dictionary'
            }
        data = self.search_data(table_name, search_query)
        if data['rows'] == 0:
            return {
                'status': 'error',
                'message': 'No rows found'
            }
        table = getDb(f'tables/{table_name}.json')
        try:
            table.updateByQuery(search_query, update_data)
        except pysondb.errors.db_errors.DataNotFoundError:
            return {
                'status': 'error',
                'message': 'Search query not found'
            }
        return {
            'status': 'success',
            'message': f'{data["rows"]} rows updated from {table_name}',
            'rows': data['rows']
        }



def console():
    while True:
        command = input('>>> ')
        splitted_command = command.split(' ')
        try:
            if command == 'help':
                print(''' 
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
                ''')      
            elif splitted_command[0] == 'delete':
                tbl_name = splitted_command[1]
                search_query = re.findall(r'{.*?}', command)[0]
                print(TableHandler().delete_data(tbl_name, ast.literal_eval(search_query)))
            elif splitted_command[0] == 'deauthorize':
                tbl_name = splitted_command[1]
                username = splitted_command[2]
                print(UserHandler().deauthorize_user(username, tbl_name))
            elif splitted_command[0] == 'authorize':
                tbl_name = splitted_command[1]
                username = splitted_command[2]
                print(UserHandler().authorize_user(username, tbl_name))
            elif splitted_command[0] == 'update':
                tbl_name = splitted_command[1]
                search_query = re.findall(r'{.*?}', command)[0]
                update_data = re.findall(r'{.*?}', command)[1]
                print(TableHandler().update_data(tbl_name, ast.literal_eval(search_query), ast.literal_eval(update_data)))
            elif splitted_command[0] == 'insert':
                tbl_name = splitted_command[1]
                insert_data = re.findall(r'{.*?}', command)[0]
                print(TableHandler().insert_data(tbl_name, ast.literal_eval(insert_data)))

            elif command == 'clear':
                if os.name == 'nt':
                    os.system('cls')
                else:
                    os.system('clear')
            elif splitted_command[0] == 'create':
                table_name = splitted_command[1]
                print(TableHandler().create_table(table_name))

            elif splitted_command[0] == 'drop':
                table_name = splitted_command[1]
                print(TableHandler().delete_table(table_name))

            elif splitted_command[0] == 'adduser':
                username = splitted_command[1]
                password = splitted_command[2]
                print(UserHandler().create_user(username, password))

            elif splitted_command[0] == 'deluser':
                username = splitted_command[1]
                print(UserHandler().delete_user(username))

            elif splitted_command[0] == 'list':
                data = TableHandler().list_tables()
                tables_list = []
                for table in data:
                    tables_list.append([table])
                print(data)
                print(tabulate(tables_list, headers=['Tables'], tablefmt='psql'))
            elif splitted_command[0] == 'search':
                tbl_name = splitted_command[1]
                search_query = splitted_command[2]
                if search_query == '*':
                    search_query = 'all'
                else: 
                    search_query = ast.literal_eval(search_query)
                data = TableHandler().search_data(tbl_name, search_query)
                print(data)
                print(tabulate(data['data'], headers='keys', tablefmt='psql'))
                
            else:
                print('Invalid command. Type "help" to see all commands')
        except IndexError:
            print('Invalid command. Type "help" to see all commands')
        except Exception as e:
            print(e)
console = threading.Thread(target=console)
console.start()

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'status': 'error','message': 'Page not found'})

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'status': 'error','message': 'Invalid request or missing fields'})

@app.route('/remove', methods=["POST"])
def remove():
    required = ['tbl_name', 'search_query', 'username', 'password']
    for field in required:
        if field not in request.form:
            return jsonify({'status': 'error','message': f"Missing field {field}"})
    if UserHandler().check_user_validity(request.form.get('username'), request.form.get('password')) == False:
        return jsonify({'status': 'error','message': 'Invalid username or password'})
    if UserHandler().check_table_authorization(request.form.get('username'), request.form.get('tbl_name')) == False:
        return jsonify({'status': 'error','message': 'You are not authorized to this table'})
    return TableHandler().delete_data(request.form.get('tbl_name'), ast.literal_eval(request.form.get('search_query')))

@app.route('/update', methods=["POST"])
def update():
    required = ['tbl_name', 'data', 'search_query', 'username', 'password']
    for field in required:
        if field not in request.form:
            return jsonify({'status': 'error','message': f"Missing field {field}"})
    if UserHandler().check_user_validity(request.form.get('username'), request.form.get('password')) == False:
        return jsonify({'status': 'error','message': 'Invalid username or password'})
    if UserHandler().check_table_authorization(request.form.get('tbl_name'), request.form.get('username')) == False:
        return jsonify({'status': 'error','message': 'You are not authorized to this table'})
    return TableHandler().update_data(request.form.get('tbl_name'), ast.literal_eval(request.form.get('search_query')), ast.literal_eval(request.form.get('data')))
    
@app.route('/search', methods=["POST"])
def search():
    required = ['tbl_name', 'search_query', 'username', 'password']
    for field in required:
        if field not in request.form:
            return jsonify({'status': 'error','message': f"Missing field {field}"})
    if UserHandler().check_user_validity(request.form.get('username'), request.form.get('password')) == False:
        return jsonify({'status': 'error','message': 'Invalid username or password'})
    if UserHandler().check_table_authorization(request.form.get('tbl_name'), request.form.get('username')) == False:
        return jsonify({'status': 'error','message': 'You are not authorized to this table'})
    if request.form.get('search_query') == '*' or request.form.get('search_query') == 'all':
        return TableHandler().search_data(request.form.get('tbl_name'), request.form.get('search_query'))
    return TableHandler().search_data(request.form.get('tbl_name'), ast.literal_eval(request.form.get('search_query')))

@app.route('/insert', methods=["POST"])
def insert():
    required = ['tbl_name', 'data', 'username', 'password']
    for field in required:
        if field not in request.form:
            return jsonify({'status': 'error','message': f"Missing field {field}"})
    if UserHandler().check_user_validity(request.form.get('username'), request.form.get('password')) == False:
        return jsonify({'status': 'error','message': 'Invalid username or password'})
    if UserHandler().check_table_authorization(request.form.get('tbl_name'), request.form.get('username')) == False:
        return jsonify({'status': 'error','message': 'You are not authorized to this table'})
    return TableHandler().insert_data(request.form.get('tbl_name'), ast.literal_eval(request.form.get('data')))
    
@app.route('/delete', methods=["POST"])
def delete():
    required = ['username', 'password', 'tbl_name', 'search_query']
    for field in required:
        if field not in request.form:
            return jsonify({'status': 'error','message': f"Missing field {field}"})
    if UserHandler().check_user_validity(request.form.get('username'), request.form.get('password')) == False:
        return jsonify({'status': 'error','message': 'Invalid username or password'})
    if UserHandler().check_table_authorization(request.form.get('tbl_name'), request.form.get('username')) == False:
        return jsonify({'status': 'error','message': 'You are not authorized to this table'})
    try:
        query = ast.literal_eval(request.form.get('search_query'))
    except ValueError:
        return jsonify({'status': 'error','message': 'Search query must be a dictionary'})
    return TableHandler().delete_data(request.form.get('tbl_name'), query)

@app.route('/drop', methods=["POST"])
def drop():
    required = ['tbl_name', 'username', 'password']
    for field in required:
        if field not in request.form:
            return jsonify({'status': 'error','message': f"Missing field {field}"})
    if UserHandler().check_user_validity(request.form.get('username'), request.form.get('password')) == False:
        return jsonify({'status': 'error','message': 'Invalid username or password'})
    if UserHandler().check_table_authorization(request.form.get('tbl_name'), request.form.get('username')) == False:
        return jsonify({'status': 'error','message': 'You are not authorized to this table'})
    return TableHandler().delete_table(request.form.get('tbl_name'))
    
@app.route('/create', methods=["POST"])
def create():
    required = ['tbl_name', 'username', 'password']
    for field in required:
        if field not in request.form:
            return jsonify({'status': 'error','message': f"Missing field {field}"})
    if UserHandler().check_user_validity(request.form.get('username'), request.form.get('password')) == False:
        return jsonify({'status': 'error','message': 'Invalid username or password'})
    return TableHandler().create_table(request.form.get('tbl_name'))
    
@app.route('/list', methods=["POST"])
def list_tbls():
    required = ['username', 'password']
    for field in required:
        if field not in request.form:
            return jsonify({'status': 'error','message': f"Missing field {field}"})
    if UserHandler().check_user_validity(request.form.get('username'), request.form.get('password')) == False:
        return jsonify({'status': 'error','message': 'Invalid username or password'})
    return jsonify({'status': 'success','message': 'Tables listed', 'tables': TableHandler().list_tables()})
    
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=3363)
