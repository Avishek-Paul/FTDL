import logging
from logging import FileHandler, Formatter

import requests
import json
import time
import pymongo
from flask import Flask, render_template, request, jsonify, redirect, url_for
from conf.settings import Config
from forms import LoginForm, CreateTask

app = Flask(__name__)
app.config.from_object(Config)

client = pymongo.MongoClient("mongodb+srv://apaul18:mypassword@cluster0-3mne1.mongodb.net")
db = client.ToDoList
all_tasks = db.Tasks

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()

    if form.validate_on_submit():
        return redirect(url_for('main'))

    return render_template("login.html", title='Sign In', form=form)

@app.route('/newtask/', methods=['GET'])
def newtask():
    
    data = request.args.to_dict()

    if 'title' in data and 'author' in data and 'content' in data and 'assignees' in data:
        post_data = {
            'id' : str(time.time()).split('.')[0],
            'title': data['title'],
            'author': data['author'],
            'content': data['content'],
            'assignees': data['assignees']
        }
        try:
            all_tasks.insert(post_data)
            return json.dumps({"success": True, "id": post_data['id']}), 200, {"ContentType":"application/json"} 
        except Exception as e:
            return json.dumps({"success":False, "reason": e}), 400, {"ContentType":"application/json"}

    else:
        return json.dumps({"success":False, "reason": 'Missing Required Information'}), 400, {"ContentType":"application/json"}

@app.route('/findtask/', methods=['GET'])
def findtask():
    data = request.args.to_dict()

    if 'id' in data:
        try:
            task = all_tasks.find_one({'id': data['id']})
            if task:
                data = {
                    'id': task['id'],
                    'title': task['title'],
                    'author': task['author'],
                    'content': task['content'],
                    'assignees': task['assignees']
                }
                return json.dumps({"success":True, "data": data}), 200, {"ContentType":"application/json"}
            else:
                return json.dumps({"success":False, "reason": "No such task found"}), 400, {"ContentType":"application/json"}

        except Exception as e:
            return json.dumps({"success":False, "reason": e}), 400, {"ContentType":"application/json"}
 
    elif 'author' in data:
        try:
            task = all_tasks.find_one({'author': data['author']})
            return str(task)
        except Exception as e:
            return json.dumps({"success":False, "reason": e}), 400, {"ContentType":"application/json"}

    else:
        return json.dumps({"success":False, "reason": "Improper Inputs"}), 400, {"ContentType":"application/json"}

@app.route('/deletetask/', methods=['GET'])
def deletetask():
    data = request.args.to_dict()

    if 'id' in data:
        try:
            task = all_tasks.delete_one({'id': data['id']})
            return str(task)
        except Exception as e:
            return json.dumps({"success":False, "reason": e}), 400, {"ContentType":"application/json"}
 
    else:
        return json.dumps({"success":False, "reason": "ID not found"}), 400, {"ContentType":"application/json"}

@app.route('/main', methods=['GET', 'POST'])
def main():

    form = CreateTask()
    
    if form.validate_on_submit():

        params = {
            'title' : form.title.data,
            'author' : form.author.data,
            'content' : form.content.data,
            'assignees' : form.assignees.data
        }

        raw_response = requests.get('http://127.0.0.1:5000/newtask/', params=params)
        response = json.loads(raw_response.text)

        if response['success'] and 'id' in response:
            id_ = response['id']
            raw_results = requests.get('http://127.0.0.1:5000/findtask/', params={'id':id_})
            results = json.loads(raw_results.text)

            if results['success']:
                data = results['data']
        else:
            results = raw_response.text

        return render_template("main.html", page_title='To Do List', form=form, show_results=True, **data)

    return render_template("main.html", page_title='To Do List', form=form, show_results=False, data=None)

if __name__ == "__main__":
    app.run(threaded=True)