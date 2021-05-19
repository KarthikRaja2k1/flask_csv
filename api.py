from flask import Flask, render_template
import flask
from flask_restplus import Api, Resource, fields, reqparse
import sqlite3
import json
import datetime
import requests

app = Flask(__name__)
api = Api(app, version='1.0', title='TodoMVC API',
          description='A simple TodoMVC API',
          )

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readOnly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'dueby': fields.Date(required=True, description='The deadline ,when this task should be finished'),
    'status': fields.String(required=True, description='Status as "Finished" or "Not started" or "In progress"')
})

with sqlite3.connect("Todos.db") as  con:
    c = con.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS TODOS (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                  task  TEXT NOT NULL,
                  due_by date,
				  status  TEXT check(status in ("not started","in progress","finished"))) ''')


def insert_into_todos(Dictionary):
    try:
        with sqlite3.connect("Todos.db") as con:
            c = con.cursor()
            Dictionary['status'] = Dictionary['status'].lower()
            Dictionary['dueby'] = datetime.datetime.strptime(Dictionary['dueby'], '%Y%m%d').date()
            print(type(Dictionary['dueby']))
            c.execute("INSERT into TODOS(task,due_by,status) VALUES(?,?,?)",
                      (Dictionary["task"], Dictionary['dueby'], Dictionary["status"]))
    except Exception as e:
        print("ERROR!!", e)


def select_byall_fromtodos():
    result = None
    with sqlite3.connect("Todos.db") as con:
        c = con.cursor()
        result = c.execute("SELECT * FROM TODOS")
        result = [{'id': int(i[0]), 'task': i[1], 'dueby': datetime.datetime.strptime(str(i[2]), '%Y-%m-%d').date(),
                   'status': i[3]} for i in result]
    return result


def check_byid_fromtodos(id):
    result = None
    with sqlite3.connect("Todos.db") as con:
        c = con.cursor()
        result = c.execute("SELECT * FROM TODOS WHERE id=?", (str(id)))
        result = [{'id': int(i[0]), 'task': i[1], 'dueby': datetime.datetime.strptime(str(i[2]), '%Y-%m-%d').date(),
                   'status': i[3]} for i in result]
    return result


def update_todo_fromtodos(id, data):
    with sqlite3.connect("Todos.db") as con:
        c = con.cursor()
        result = c.execute("UPDATE TODOS SET status= ? WHERE id=? ", (data['status'], str(id),))
    print(result)
    return result


def delete_todo_fromtodos(id):
    with sqlite3.connect("Todos.db") as con:
        c = con.cursor()
        result = c.execute("DELETE FROM TODOS  WHERE id=? ", (str(id),))
    print(result)
    return result


def select_bystatus_fromtodos(status):
    result = None
    with sqlite3.connect("Todos.db") as con:
        c = con.cursor()
        # duedate=datetime.datetime.strptime(duedate,'%Y-%m-%d').date()
        result = c.execute("SELECT * FROM TODOS WHERE  status=?", (status,))
        result = [{'id': int(i[0]), 'task': i[1], 'dueby': datetime.datetime.strptime(str(i[2]), '%Y-%m-%d').date(),
                   'status': i[3]} for i in result]
    return result


def select_byduedate_fromtodos(duedate):
    result = None
    with sqlite3.connect("Todos.db") as con:
        c = con.cursor()
        # duedate=datetime.datetime.strptime(duedate,'%Y-%m-%d').date()
        result = c.execute("SELECT * FROM TODOS WHERE due_by=?  AND status<>'finished'", (duedate,))
        result = [{'id': int(i[0]), 'task': i[1], 'dueby': datetime.datetime.strptime(str(i[2]), '%Y-%m-%d').date(),
                   'status': i[3]} for i in result]
    return result


def select_overdue_fromtodos(duedate):
    result = None
    print(duedate)
    with sqlite3.connect("Todos.db") as con:
        c = con.cursor()
        # duedate=datetime.datetime.strptime(duedate,'%Y-%m-%d').date()
        result = c.execute("SELECT * FROM TODOS WHERE due_by<?  AND status<>'finished'", (duedate,))
        result = [{'id': int(i[0]), 'task': i[1], 'dueby': datetime.datetime.strptime(str(i[2]), '%Y-%m-%d').date(),
                   'status': i[3]} for i in result]
    return result


class TodoDAO(object):
    def __init__(self):
        self.counter = 0
        self.todos = []

    def get(self, id):
        for todo in check_byid_fromtodos(id):
            return todo
        api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self, data):
        todo = data
        insert_into_todos(todo)
        return todo

    def update(self, id, data):
        self.get(id)
        update_todo_fromtodos(id, data)
        return self.get(id)

    def delete(self, id):
        todo = self.get(id)
        delete_todo_fromtodos(id)
        return self.get(id)


DAO = TodoDAO()


@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''

    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return select_byall_fromtodos()

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''

    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload), 201


@ns.route('/due')
class DueList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''

    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('due_date')
        args = parser.parse_args()
        print("DUDEYDATE", args)
        '''List all tasks'''
        print(args["due_date"], type(args["due_date"]))
        return select_byduedate_fromtodos(args["due_date"])


@ns.route('/overdue')
class OvrdueList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''

    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return select_overdue_fromtodos(str(datetime.date.today()))


@ns.route('/finished')
class FinishedList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''

    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return select_bystatus_fromtodos("finished")


"""                            MAIN APP               """

with sqlite3.connect("User.db") as  con:
    c = con.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS LOGINS (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                  username  TEXT NOT NULL,
                  pswd  TEXT NOT NULL,
				  mode  Integer) ''')


def insert_into_Logins(name, pwd, mode):
    try:
        with sqlite3.connect("User.db") as con:
            c = con.cursor()
            c.execute("INSERT into LOGINS(username,pswd,mode) VALUES(?,?,?)", (name, pwd, mode))
    except Exception as e:
        print("ERROR!!", e)


def match_fromLogins(user, pswd):
    result = -1
    pswd1 = None
    with sqlite3.connect("User.db") as con:
        c = con.cursor()
        result = c.execute("SELECT * FROM LOGINS WHERE username=?", (user,))
        result = [{'psw': i[2], 'mode': i[3]} for i in result]
    if (result == []):
        return -1
    elif (result[0]['psw'] != pswd):
        return -3
    result = result[0]['mode']
    return result


Logged = False
Mode = -1
"""0-for unidentified 1-read 2-write and read """
UserName = None


@app.route('/home')
def home():
    return render_template("Home.html")


@app.route('/main')
def main():
    global Logged
    global Mode
    print("HJJEJEJEJE",Logged,Mode)
    if (Logged and Mode == 0):
        return render_template("main1.html")
    elif (Logged and Mode == 1):
        return render_template("main.html")
    else:
        return flask.redirect('/home') 


@app.route('/Logout')
def Logout():
    global Logged
    global Mode
    global UserName
    Logged = False
    Mode = -1
    UserName = None
    return flask.redirect('/home')


@app.route("/Login", methods=['GET', 'POST'])
def Login():
    global Logged
    global Mode
    global UserName
    if flask.request.method == 'POST':
        username = flask.request.values.get('username')  # Your form's
        password = flask.request.values.get('psw')  # input names
        result = match_fromLogins(username, password)
        if (result == -1 or result == -3):
            return "Invalid credentials,go back to login or signup"
        else:
            Mode = result
            Logged = True
            UserName = username
            return flask.redirect('/main')
    else:
        return render_template("Login.html")


@app.route("/Signup", methods=['GET', 'POST'])
def sign_up():
    if flask.request.method == 'POST':
        username = flask.request.values.get('username')
        password = flask.request.values.get('psw')
        Mode = flask.request.values.get('mode')
        if (match_fromLogins(username, password) != -1):
            return "Existing user with given username"
        else:
            insert_into_Logins(username, password, Mode)
            return "Signup Succesful!!, Login from Login Page to continue"
    else:
        return render_template("Signup.html")


@app.route("/Seeall", methods=['GET'])
def Seeall():
    global Logged
    global Mode
    print("LOVINGGLY logged",Logged)
    if(Logged):
        x = requests.get('http://127.0.0.1:5000/todos/')
        print(x.json(), type(x.json()))
        return render_template("List.html", Listy=x.json(), data="All Tasks	")
    else:
        flask.redirect('/main')



@app.route("/Create", methods=['GET', 'POST'])
def Create():
    global Logged
    global Mode
    if (Logged and Mode == 1):
        if flask.request.method == 'POST':
            print("piak?", flask.request.values)
            Dict = {}
            st = flask.request.values
            temp = str(datetime.datetime.strptime(st['dueby'], '%Y-%m-%d').date()).replace('-', '')
            Dict['dueby'] = temp
            Dict['task'] = st['task']
            Dict['status'] = st['status']
            Dict['Api'] = "TESTAPI"
            x = requests.post('http://127.0.0.1:5000/todos/', json=Dict)
            L = []
            L.append(x.json())
            return render_template("List.html", Listy=L, data="inserted")
        else:
            return render_template("Insert.html")
    else:
        flask.redirect('/main')


@app.route("/Dueby", methods=['GET', 'POST'])
def Due():
    global Logged
    global Mode
    if (Logged):
        if flask.request.method == 'POST':
            print("piak?", flask.request.values)
            Dict = {}
            st = flask.request.values
            temp = str(datetime.datetime.strptime(st["due_date"], '%Y-%m-%d').date())
            Dict["due_date"] = temp
            Dict['Api'] = "TESTAPI"
            x = requests.get('http://127.0.0.1:5000/todos/due', params=Dict)
            print("Create", x.json(), type(x.json()))
            return render_template("List.html", Listy=x.json(), data="Due Tasks")
        else:
            return render_template("dueby.html")
    else:
        flask.redirect('/main')


@app.route("/Overdue", methods=['GET'])
def OverDue():
    global Logged
    global Mode
    if (Logged):
        if flask.request.method == 'GET':
            print("piak?", flask.request.values)
            Dict = {}
            Dict['Api'] = "TESTAPI"
            x = requests.get('http://127.0.0.1:5000/todos/overdue')
            print("Create", x.json(), type(x.json()))
            return render_template("List.html", Listy=x.json(), data="Over Due Tasks")
    else:
        flask.redirect('/main')


@app.route("/Finished", methods=['GET'])
def Finished():
    global Logged
    global Mode
    if (Logged):
        if flask.request.method == 'GET':
            print("piak?", flask.request.values)
            Dict = {}
            Dict['Api'] = "TESTAPI"
            x = requests.get('http://127.0.0.1:5000/todos/finished')
            print("Create", x.json(), type(x.json()))
            return render_template("List.html", Listy=x.json(), data="Finished Tasks")
    else:
        flask.redirect('/main')

@app.route("/Update", methods=['GET', 'POST'])
def Update():
    global Logged
    global Mode
    if (Logged and Mode == 1):
        if flask.request.method == 'POST':
            Dict = {}
            st = flask.request.values
            Dict['status'] = st['status']
            print(Dict)
            Dict['Api'] = "TESTAPI"
            x = requests.put('http://127.0.0.1:5000/todos/' + st['taskid'], json=Dict)
            L = []
            L.append(x.json())
            return render_template("List.html", Listy=L, data="Updated Task")
        else:
            return render_template("update_status.html")
    else:
        flask.redirect('/main')


@app.route("/Delete", methods=['GET', 'POST'])
def Delete():
    global Logged
    global Mode
    if (Logged and Mode == 1):
        if flask.request.method == 'POST':
            Dict = {}
            st = flask.request.values
            Dict['Api']="TESTAPI"
            x = requests.delete('http://127.0.0.1:5000/todos/' + st['taskid'], json=Dict)
            return "Deleted if exists"
        else:
            return render_template("Delete.html")
    else:
        flask.redirect('/main')


if __name__ == '__main__':
    app.run(debug=True)