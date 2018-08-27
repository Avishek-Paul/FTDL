import logging
from logging import FileHandler, Formatter

import requests
import json
import time
import pymongo
from flask import Flask, render_template, request, jsonify, redirect, url_for
from conf.settings import Config
from forms import LoginForm, CreateTask, SearchTask, updateTask

app = Flask(__name__)
app.config.from_object(Config)

client = pymongo.MongoClient("mongodb+srv://apaul18:{}@cluster0-3mne1.mongodb.net".format(Config.password))
db = client.ToDoList
all_tasks = db.Tasks

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()

    if form.validate_on_submit():
        return redirect(url_for('main'))

    return render_template("login.html", title='Sign In', form=form)

@app.route('/newtask/', methods=['POST'])
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

@app.route('/deletetask/', methods=['POST'])
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
    search = SearchTask()
    update = updateTask()
    
    show_results = False
    initial = True
    data = {}

    if search.validate_on_submit():
        initial = False
        raw_results = requests.get('http://127.0.0.1:5000/findtask/', params={'id':search.id_.data.strip()})
        results = json.loads(raw_results.text)
        if results['success']:
            data = results['data']
            update.title.data = data['title']
            update.author.data = data['author']
            update.content.data = data['content']
            update.assignees.data = data['assignees']
            show_results = True

    if form.validate_on_submit():

        initial = True
        params = {
            'title' : form.title.data,
            'author' : form.author.data,
            'content' : form.content.data,
            'assignees' : form.assignees.data
        }

        raw_response = requests.post('http://127.0.0.1:5000/newtask/', params=params)
        response = json.loads(raw_response.text)

        if response['success'] and 'id' in response:
            id_ = response['id']
            raw_results = requests.get('http://127.0.0.1:5000/findtask/', params={'id':id_})
            results = json.loads(raw_results.text)

            if results['success']:
                data = results['data']
                show_results = True

    return render_template("main.html", page_title='To Do List', form=form, search=search, 
                            update=update,
                            show_results=show_results,
                            initial=initial, **data)

if __name__ == "__main__":
    app.run(threaded=True)
