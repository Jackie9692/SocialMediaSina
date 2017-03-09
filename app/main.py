#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, session, json
#from flask.ext.bcrypt import Bcrypt
from requestHandler import handleRequest
from dataCleaning import getTasks, addTask

app = Flask(__name__)
app.secret_key = '1)/;M[&U|uevca3kz~{#o9!78X]08-!oZaf8k"p6LfT)xZo48Q?AH=()~2+0A]'


'''@app.before_request
def connection():
    print "event"'''
@app.route("/")
def layout():
    print '；'==';'
    session['logged_in'] = False #here
    return render_template('layout.html')

@app.route('/login', methods=['POST'])
def login():
    print "New user loggin in"
    json_data = request.json
    '''user = User.query.filter_by(email=json_data['email']).first()
    if user and bcrypt.check_password_hash(
            user.password, json_data['password']):'''
    with open('login.json') as infile:
        loginData = json.load(infile)
    if json_data['email'] in loginData:
        if loginData[json_data['email']] == json_data['password']:
            print loginData[json_data['email']] + ' logged in'
            session['logged_in'] = True
            status = True
        else:
            status = False
    else:
        status = False
    return jsonify({'result': status})

@app.route('/logout')
def logout():
    print "User log out"
    session['logged_in'] = False
    return jsonify({'result': 'success'})

@app.route('/status')
def status():
    if session.get('logged_in'):
        if session['logged_in']:
            return jsonify({'status': True})
    else:
        return jsonify({'status': False})

@app.route('/search_request', methods=['GET'])
def search_request():
    return handleRequest(request, session['logged_in'])

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/monitor_cleaning_tasks', methods=['GET'])
def monitor_tasks():
    return getTasks()

@app.route('/add_cleaning_task', methods=['GET'])
def add_task():
    task = request.args.get('task')
    if task != None:
        return addTask(json.loads(task))
    else:
        return "404", 404

@app.route('/<string:page_name>/')
def static_page(page_name):
    print "User render new page"
    if session['logged_in']:
        return render_template('%s.html' % page_name)
    else:
        return "404", 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
