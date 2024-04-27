from flask import Flask, jsonify, request
import sqlite3
import random

app = Flask(__name__)
#CORS(app, resources={r"/deletebyid/*": {"origins": "*", "methods": ["DELETE"]}})

# Database connection
DATABASE = 'tasks'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

# Route to retrieve all tasks
@app.route("/get_all_data", methods=["GET"])
def get_tasks():
    db = get_db()
    cursor = db.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    db.close()
    tasks_dict = [dict(i) for i in tasks]
    return jsonify(tasks_dict), 200

# Route to retrieve a single task by ID
@app.route("/retrievebyid", methods=["GET"])
def get_task():
    data = request.args.get("retrievebyid")
    db = get_db()
    cursor = db.execute("SELECT * FROM tasks WHERE id = ?", (data,))
    task = cursor.fetchone()
    db.close()
    if task:
        return jsonify(dict(task)), 200
    else:
        return "Task not found", 404

# Route to create a new task
@app.route("/submit", methods=["POST"])
def create_task():
    db = get_db()
    data = request.form
    property = get_property(data["property"])
    cursor = db.cursor()
    cursor.execute("INSERT INTO tasks (name, assignee, project, startTime, Property) VALUES (?, ?, ?, ?, ?)",                 (data["name"], data["assignee"], data["project"], data["startTime"], property))
    db.commit()
    task_id = cursor.lastrowid
    cursor.execute("select * from tasks where id = ?", (task_id,))
    task = cursor.fetchone()
    db.close()
    return jsonify(dict(task)), 201

# Route to delete a task by ID
@app.route("/deletebyid", methods=["POST"])

def delete_task():
    db = get_db()
    task_id = request.form.get("deletebyid")
    cursor = db.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    if cursor.rowcount == 1:
        db.close()
        return "Task deleted successfully", 200
    else:
        db.close()
        return "Task not found", 404

# Route to search tasks by name
@app.route("/searchbyname", methods=["GET"])
def search_tasks_by_name():
    name = request.args.get("searchbyname")
    db = get_db()
    cursor = db.execute("SELECT * FROM tasks WHERE name LIKE ?", ('%' + name + '%',))
    tasks = cursor.fetchall()
    db.close()
    if tasks:
        tasks_dict = [dict(i) for i in tasks]
        return jsonify(tasks_dict), 200
    else:
        return "No tasks found with the given name", 404

# Route to search tasks by assignee
@app.route("/tasks/searchbyassignee", methods=["GET"])
def search_tasks_by_assignee():
    data = request.args.get("searchbyassignee")
    db = get_db()
    cursor = db.execute("SELECT * FROM tasks WHERE assignee = ? ORDER BY startTime LIMIT 10", (data,))
    tasks = cursor.fetchall()
    db.close()
    if tasks:
        tasks_dict = [dict(i) for i in tasks]
        return jsonify(tasks_dict), 200
    else:
        return "No tasks found with the given assignee"+data, 404

# Function to generate a random string 
def get_property(s):
    property = "".join(random.choices(s.lower(), k=5))
    return property
    
if __name__ == "__main__":
    app.run(debug=True)