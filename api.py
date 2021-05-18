from flask import Flask
from flask_restplus import Api, Resource, fields,reqparse
import sqlite3
import json
import datetime

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


with sqlite3.connect("test.db") as  con:

    c = con.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS TODOS (id INTEGER  PRIMARY KEY AUTOINCREMENT,
                  task  TEXT NOT NULL,
                  due_by date,
				  status  TEXT check(status in ("not started","in progress","finished"))) ''')
  
def insert_into_todos(Dictionary):
    try:
       with sqlite3.connect("test.db") as con:
          c = con.cursor()
          Dictionary['status']=Dictionary['status'].lower()
          Dictionary['dueby']=datetime.datetime.strptime(Dictionary['dueby'],'%Y%m%d').date()
          print(type(Dictionary['dueby']))
          c.execute("INSERT into TODOS(task,due_by,status) VALUES(?,?,?)",(Dictionary["task"],Dictionary['dueby'],Dictionary["status"]))
    except Exception as e:
        print("ERROR!!",e)

	   
def select_byall_fromtodos():
    result=None
    with sqlite3.connect("test.db") as con:
       c = con.cursor()
       result=c.execute("SELECT * FROM TODOS")
       result=[{'id':int(i[0]),'task':i[1],'dueby':datetime.datetime.strptime(str(i[2]),'%Y-%m-%d').date(),'status':i[3]} for i in result]
    return result

	
	
	
def check_byid_fromtodos(id):
    result=None
    with sqlite3.connect("test.db") as con:
       c = con.cursor()
       result=c.execute("SELECT * FROM TODOS WHERE id=?",(str(id)))
       result=[{'id':int(i[0]),'task':i[1],'dueby':datetime.datetime.strptime(str(i[2]),'%Y-%m-%d').date(),'status':i[3]} for i in result]
    return result

def update_todo_fromtodos(id,data):
    with sqlite3.connect("test.db") as con:
       c = con.cursor()
       result=c.execute("UPDATE TODOS SET status= ? WHERE id=? ",(data['status'],str(id)))
    print(result)
    return result


def select_bystatus_fromtodos(status):
    result=None
    with sqlite3.connect("test.db") as con:
       c = con.cursor()
       #duedate=datetime.datetime.strptime(duedate,'%Y-%m-%d').date()
       result=c.execute("SELECT * FROM TODOS WHERE  status=?",(status,))
       result=[{'id':int(i[0]),'task':i[1],'dueby':datetime.datetime.strptime(str(i[2]),'%Y-%m-%d').date(),'status':i[3]} for i in result]
    return result 

def select_byduedate_fromtodos(duedate):
    result=None
    with sqlite3.connect("test.db") as con:
       c = con.cursor()
       #duedate=datetime.datetime.strptime(duedate,'%Y-%m-%d').date()
       result=c.execute("SELECT * FROM TODOS WHERE due_by=?  AND status<>'finished'",(duedate,))
       result=[{'id':int(i[0]),'task':i[1],'dueby':datetime.datetime.strptime(str(i[2]),'%Y-%m-%d').date(),'status':i[3]} for i in result]
    return result 
	
def select_overdue_fromtodos(duedate):
    result=None
    print(duedate)
    with sqlite3.connect("test.db") as con:
       c = con.cursor()
       #duedate=datetime.datetime.strptime(duedate,'%Y-%m-%d').date()
       result=c.execute("SELECT * FROM TODOS WHERE due_by<?  AND status<>'finished'",(duedate,))
       result=[{'id':int(i[0]),'task':i[1],'dueby':datetime.datetime.strptime(str(i[2]),'%Y-%m-%d').date(),'status':i[3]} for i in result]
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
        update_todo_fromtodos(id,data)
        return self.get(id)

    def delete(self, id):
        todo = self.get(id)
        self.todos.remove(todo)


DAO = TodoDAO()
DAO.create({'task': 'Build an API','dueby':'20190102','status':'in progress'})
DAO.create({'task': '?????','dueby':'20190102','status':'in progress'})
DAO.create({'task': 'profit!','dueby':'20190102','status':'in progress'})


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
        return DAO.update(id, api.payload),201

		

@ns.route('/due')
class DueList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('due_date')
        args = parser.parse_args()
        '''List all tasks'''
        print(args["due_date"],type(args["due_date"]))
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



	


if __name__ == '__main__':
    app.run(debug=True)
