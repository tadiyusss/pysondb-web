# TODO - Add user encryption
# TODO - Add user authentication
# TODO - Add database encryption

from pysondb import getDb
from flask import Flask, request, jsonify
from tabulate import tabulate
import threading
import os 
import sys

if '-d' in sys.argv:
    debug = True
else:
    debug = False

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
    create <tbl_name> - create a table
    drop <tbl_name> - drop a table
    insert <tbl_name> <data> - insert data to a table
    search <tbl_name> <search_query> - search data in a table (use "*" to get all data)
    adduser <username> <password> - add a user to the database
    deluser <username> - delete a user from the database
    clear - clear the console
    ''')    
            elif splitted_command[0] == 'insert':
                tbl_name = splitted_command[1]
                insert_data = splitted_command[2]
                if os.path.isfile(f'tables/{tbl_name}.json'):
                    table = getDb(f'tables/{tbl_name}.json')
                    table.add(insert_data)
                    print('Data inserted')
                else:
                    print('Table not found')

            elif command == 'clear':
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
        except Exception as e:
            print(e)
console = threading.Thread(target=console)
console.start()

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'status': 'error','message': 'Page not found'})

@app.route('/search', methods=["POST"])
def search():
    tbl_name = request.form.get('tbl_name')
    search_query = request.form.get('search_query')
    
    if len(users_tbl.getByQuery({'username': request.form.get('username'), 'password': request.form.get('password')})) == 0:
        return jsonify({'status': 'error','message': 'Invalid username or password'})

    if os.path.isfile(f'tables/{tbl_name}.json'):
        table = getDb(f'tables/{tbl_name}.json')
        if search_query == 'all':
            data = table.getAll()
        else:
            data = table.getByQuery(search_query)
        return jsonify({'status': 'success','tbl_name': tbl_name,'data': data})
    else:
        return jsonify({'status': 'error','message': 'Table not found'})
    
@app.route('/insert', methods=["POST"])
def insert():
    tbl_name = request.form.get('tbl_name')
    insert_data = request.form.get('data')
    
    if len(users_tbl.getByQuery({'username': request.form.get('username'), 'password': request.form.get('password')})) == 0:
        return jsonify({'status': 'error','message': 'Invalid username or password'})

    if os.path.isfile(f'tables/{tbl_name}.json'):
        table = getDb(f'tables/{tbl_name}.json')
        table.add(insert_data)
        return jsonify({'status': 'success','tbl_name': tbl_name,'data': insert_data})
    else:
        return jsonify({'status': 'error','message': 'Table not found'})
    
@app.route('/drop', methods=["POST"])
def drop():
    tbl_name = request.form.get('tbl_name')
    
    if len(users_tbl.getByQuery({'username': request.form.get('username'), 'password': request.form.get('password')})) == 0:
        return jsonify({'status': 'error','message': 'Invalid username or password'})

    if os.path.isfile(f'tables/{tbl_name}.json'):
        os.remove(f'tables/{tbl_name}.json')
        return jsonify({'status':'success','tbl_name':tbl_name})
    else:
        return jsonify({'status':'error','message':'Table not found'})

@app.route('/create', methods=["POST"])
def create():
    tbl_name = request.form.get('tbl_name')
    
    if len(users_tbl.getByQuery({'username': request.form.get('username'), 'password': request.form.get('password')})) == 0:
        return jsonify({'status': 'error','message': 'Invalid username or password'})

    if os.path.isfile(f'tables/{tbl_name}.json'):
        return jsonify({'status': 'error','message': 'Table already exists'})
    else:
        getDb(f'tables/{tbl_name}.json')
        return jsonify({'status':'success','tbl_name':tbl_name})
    
    
app.run(host='0.0.0.0', port=3363, debug=debug)
