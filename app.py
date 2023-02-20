#!/usr/bin/python3

from pysondb import getDb
from flask import Flask, request, jsonify
from tabulate import tabulate
import getpass
import ast
import pysondb
import threading
import os 
import sys
import re

if os.path.isdir('tables') == False:
    os.mkdir('tables')
if os.path.isdir('data') == False:
    os.mkdir('data')
if os.path.isfile('data/users.json') == False:
    print('No users found, creating a new user...')
    username = input('Enter a username: ')
    password = getpass.getpass('Enter a password: ')
    users_tbl = getDb('data/users.json')
    users_tbl.add({'username': username, 'password': password})

app = Flask(__name__)
users_tbl = getDb('data/users.json')

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
insert - <tbl_name> <data> - insert data to a table
search - <tbl_name> <search_query> - search data in a table (use "*" to get all data)
adduser - <username> <password> - add a user to the database
deluser - <username> - delete a user from the database
update - <tbl_name> <search_query> <update_data> - update data in a table
clear - clear the console
''')        
            elif splitted_command[0] == 'update':
                tbl_name = splitted_command[1]
                search_query = re.findall(r'{.*?}', command)[0]
                update_data = re.findall(r'{.*?}', command)[1]
                if os.path.isfile(f'tables/{tbl_name}.json'):
                    table = getDb(f'tables/{tbl_name}.json')
                    rows = table.getByQuery(ast.literal_eval(search_query))
                    table.updateByQuery(ast.literal_eval(search_query), ast.literal_eval(update_data))
                    print('Data updated, {} rows updated'.format(len(rows)))
                else:
                    print('Table not found')
            elif splitted_command[0] == 'insert':
                tbl_name = splitted_command[1]
                insert_data = re.findall(r'{.*?}', command)[0]
                if os.path.isfile(f'tables/{tbl_name}.json'):
                    table = getDb(f'tables/{tbl_name}.json')
                    table.add(ast.literal_eval(insert_data))
                    print('Data inserted')
                else:
                    print('Table not found')

            elif command == 'clear':
                if os.name == 'nt':
                    os.system('cls')
                else:
                    os.system('clear')
            elif splitted_command[0] == 'create':
                if os.path.isfile(f'tables/{splitted_command[1]}.json'):
                    print('Table already exists')
                else:
                    getDb(f'tables/{splitted_command[1]}.json')
                    print('Table created')
            elif splitted_command[0] == 'drop':
                if os.path.isfile(f'tables/{splitted_command[1]}.json'):
                    os.remove(f'tables/{splitted_command[1]}.json')
                    print('Table dropped')
                else:
                    print('Table not found')
            elif splitted_command[0] == 'adduser':
                username = splitted_command[1]
                password = splitted_command[2]
                if len(users_tbl.getByQuery({'username': username})) != 0:
                    print('Username already exists')
                    continue
                users_tbl.add({'username': username, 'password': password})
                print('User added')
            elif splitted_command[0] == 'deluser':
                username = splitted_command[1]
                if len(users_tbl.getByQuery({'username': username})) != 0:
                    users_tbl.deleteById(users_tbl.getByQuery({'username': username})[0]['id'])
                else:
                    print('User not found')
            elif splitted_command[0] == 'list':
                data = [x.replace('.json', '') for x in os.listdir('tables')]
                table = []
                for x in data:
                    table.append([x])
                print(tabulate(table , headers=['Tables'], tablefmt='psql'))
            elif splitted_command[0] == 'search':
                tbl_name = splitted_command[1]
                search_query = splitted_command[2]
                if os.path.isfile(f'tables/{tbl_name}.json'):
                    table = getDb(f'tables/{tbl_name}.json')
                    if search_query == '*':
                        data = table.getAll()
                    else:
                        data = table.getByQuery(search_query)
                    print(tabulate(data, headers='keys', tablefmt='psql'))
                else:
                    print('Table not found')
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

@app.route('/remove', methods=["POST"])
def remove():
    try:
        tbl_name = request.form.get('tbl_name')
        search_query = request.form.get('search_query')

        if len(users_tbl.getByQuery({'username': request.form.get('username'), 'password': request.form.get('password')})) == 0:
            return jsonify({'status': 'error','message': 'Invalid username or password'})
        else:
            if os.path.isfile(f'tables/{tbl_name}.json'):
                table = getDb(f'tables/{tbl_name}.json')
                rows = table.getByQuery(ast.literal_eval(search_query))
                if len(rows) == 0:
                    print(rows)
                    return jsonify({'status': 'error','message': 'No rows found'})
                else:
                    for row in rows:
                        table.deleteById(row['id'])
                    return jsonify({'status': 'success','message': 'Data removed', 'data': len(rows)})
            else:
                return jsonify({'status': 'error','message': 'Table not found'})
    except Exception as e:
        return jsonify({'status': 'error','message': f"{type(e).__name__}: {str(e)}"})

@app.route('/update', methods=["POST"])
def update():
    try:
        tbl_name = request.form.get('tbl_name')
        update_data = request.form.get('data')
        search_query = request.form.get('search_query')

        if len(users_tbl.getByQuery({'username': request.form.get('username'), 'password': request.form.get('password')})) == 0:
            return jsonify({'status': 'error','message': 'Invalid username or password'})
            
        if os.path.isfile(f'tables/{tbl_name}.json'):
            table = getDb(f'tables/{tbl_name}.json')
            rows = table.getByQuery(ast.literal_eval(search_query))
            try:
                table.updateByQuery(ast.literal_eval(search_query), ast.literal_eval(update_data))
            except pysondb.errors.db_errors.DataNotFoundError:
                return jsonify({'status': 'error','message': 'Search query not found'})
            
            return jsonify({'status': 'success','tbl_name': tbl_name,'search_query': search_query,'update_data': update_data,'rows': len(rows)})
        else:
            return jsonify({'status': 'error','message': 'Table not found'})
    except Exception as e:
        return jsonify({'status': 'error','message': f"{type(e).__name__}: {str(e)}"})
@app.route('/search', methods=["POST"])
def search():
    try:
        tbl_name = request.form.get('tbl_name')
        search_query = request.form.get('search_query')
        
        if len(users_tbl.getByQuery({'username': request.form.get('username'), 'password': request.form.get('password')})) == 0:
            return jsonify({'status': 'error','message': 'Invalid username or password'})
        if search_query == '':
            return jsonify({'status': 'error','message': 'Search query cannot be empty'})
        else:
            if os.path.isfile(f'tables/{tbl_name}.json'):
                table = getDb(f'tables/{tbl_name}.json')
                if search_query == '*':
                    data = table.getAll()
                    return jsonify({'status': 'success','tbl_name': tbl_name,'data': data, 'rows': len(data)}) 
                else:
                    data = table.getByQuery(ast.literal_eval(search_query))
                    return jsonify({'status': 'success','tbl_name': tbl_name,'data': data, 'rows': len(data)})
                
            else:
                return jsonify({'status': 'error','message': 'Table not found'})
    except Exception as e:
        return jsonify({'status': 'error','message': f"{type(e).__name__}: {str(e)}"})
@app.route('/insert', methods=["POST"])
def insert():
    try:
        tbl_name = request.form.get('tbl_name')
        insert_data = request.form.get('data')
        if len(users_tbl.getByQuery({'username': request.form.get('username'), 'password': request.form.get('password')})) == 0:
            return jsonify({'status': 'error','message': 'Invalid username or password'})

        if os.path.isfile(f'tables/{tbl_name}.json'):
            table = getDb(f'tables/{tbl_name}.json')
            table.add(ast.literal_eval(insert_data))
            return jsonify({'status': 'success','tbl_name': tbl_name,'data': insert_data})
        else:
            return jsonify({'status': 'error','message': 'Table not found'})
    except Exception as e:
        return jsonify({'status': 'error','message': f"{type(e).__name__}: {str(e)}"})
    
@app.route('/drop', methods=["POST"])
def drop():
    try:
        tbl_name = request.form.get('tbl_name')
        
        if len(users_tbl.getByQuery({'username': request.form.get('username'), 'password': request.form.get('password')})) == 0:
            return jsonify({'status': 'error','message': 'Invalid username or password'})

        if os.path.isfile(f'tables/{tbl_name}.json'):
            os.remove(f'tables/{tbl_name}.json')
            return jsonify({'status':'success','tbl_name':tbl_name})
        else:
            return jsonify({'status':'error','message':'Table not found'})
    except Exception as e:
        return jsonify({'status': 'error','message': f"{type(e).__name__}: {str(e)}"})
@app.route('/create', methods=["POST"])
def create():
    try:
        tbl_name = request.form.get('tbl_name')
        
        if len(users_tbl.getByQuery({'username': request.form.get('username'), 'password': request.form.get('password')})) == 0:
            return jsonify({'status': 'error','message': 'Invalid username or password'})

        if os.path.isfile(f'tables/{tbl_name}.json'):
            return jsonify({'status': 'error','message': 'Table already exists'})
        else:
            try:
                getDb(f'tables/{tbl_name}.json')
            except OSError:
                return jsonify({'status': 'error','message': 'Invalid table name'})
            return jsonify({'status':'success','tbl_name':tbl_name})
    except Exception as e:
        return jsonify({'status': 'error','message': f"{type(e).__name__}: {str(e)}"})
    
@app.route('/list', methods=["POST"])
def list_tbls():
    try:
        if len(users_tbl.getByQuery({'username': request.form.get('username'), 'password': request.form.get('password')})) == 0:
            return jsonify({'status': 'error','message': 'Invalid username or password'})
        else:
            data = os.listdir('tables')
            files = []
            for file in data:
                if file.endswith('.json'):
                    files.append(file[:-5])  
        return jsonify({'status':'success','data':files, 'tables_count': len(files)})
    except Exception as e:
        return jsonify({'status': 'error','message': f"{type(e).__name__}: {str(e)}"})
    
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=3363)
