#6D/19090003/AgungIswanto
#6D/19090125/RamdonBaehakiNurFaiz
#6D/19090130/NovitaFitriaPutri
#6D/19098001/SaksonoBayuAjieSumantri

from datetime import datetime
from flask import Flask, jsonify, request,make_response
import os, random, string
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "uts.db"))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    token = db.Column(db.String(225))
    created_at = db.Column(db.DateTime, default=datetime.now())

class events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_creator = db.Column(db.String(20), unique=False, nullable=False)
    event_name = db.Column(db.String(20), unique=True, nullable=False)
    event_start_time = db.Column(db.DateTime)
    event_end_time = db.Column(db.DateTime)
    event_start_lat = db.Column(db.String(20), unique=False, nullable=False)
    event_start_lng = db.Column(db.String(20), unique=False, nullable=False)
    event_finish_lat = db.Column(db.String(20), unique=False, nullable=False)
    event_finish_lng = db.Column(db.String(20), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

class logs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    event_name = db.Column(db.String(20))
    log_lat = db.Column(db.String(20))
    log_lng = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now())
db.create_all()

@app.route('/api/v1/users/create', methods=['POST'])
def registrasi():
    username = request.json['username']
    password = request.json['password']
    
    if username and password:
        model = users(username=username, password=password)
        db.session.add(model)
        db.session.commit()
        return make_response(jsonify({"msg ":"registrasi sukses"}), 200)
    return jsonify({"msg ":"username / password harus diisi"})

@app.route('/api/v1/users/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    akun = users.query.filter_by(username=username, password=password).first()
    if akun:
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
        users.query.filter_by(username=username, password=password).update({'token': token})
        db.session.commit()
        return make_response(jsonify({"msg":"login sukses", "token":token}),200)
    return jsonify({"msg":"login / mengambil info token gagal"}) 

@app.route('/api/v1/events/create', methods=['POST'])
def create_events():
    token =  request.json['token']
    event_name = request.json['event_name']
    event_start_time = request.json['event_start_time']
    event_end_time = request.json['event_end_time']
    event_start_lat = request.json['event_start_lat']
    event_start_lng = request.json['event_start_lng']
    event_finish_lat = request.json['event_finish_lat']
    event_finish_lng = request.json['event_finish_lng']
    event_start_time = datetime.strptime(event_start_time, '%Y-%m-%d %H:%M:%S') 
    event_end_time = datetime.strptime(event_end_time, '%Y-%m-%d %H:%M:%S')
    
    cekakun=users.query.filter_by(token=token).first()
    
    
    
    if cekakun:
        event_creator = cekakun.username
        try:
            data = events(event_creator=event_creator, event_name=event_name, event_start_time=event_start_time, event_end_time=event_end_time,
                          event_start_lat=event_start_lat, event_start_lng=event_start_lng, event_finish_lat=event_finish_lat, event_finish_lng=event_finish_lng)
            db.session.add(data)
            db.session.commit()
            result = jsonify(({'msg': 'membuat event sukses'}), 200)
        except:
            result = jsonify(({'msg': 'membuat event gagal'}), 400)
    else:
        result = jsonify(({'msg': 'token salah'}), 401)
    return result

@app.route('/api/v1/events/log', methods=['POST'])
def events_log():
    token = request.json['token']
    event_name = request.json['event_name']
    log_lat = request.json['log_lat']
    log_lng = request.json['log_lng']
    cekusername=users.query.filter_by(token=token).first()
    if cekusername:
        username = cekusername.username
        try:
            datalog = logs(username=username, event_name=event_name,
                        log_lat=log_lat, log_lng=log_lng)
            db.session.add(datalog)
            db.session.commit()
            result = jsonify(({'msg': 'sukses mencatat posisi terbaru'}), 200)
        except:
            result = jsonify(({'msg': 'gagal mencatat posisi terbaru'}), 400)
    else:
        result = jsonify(({'msg': 'token salah'}), 401)
    return result

@app.route('/api/v1/events/logs', methods=['GET'])
def events_logs():
    token = request.json['token']
    event_name = request.json['event_name']
    username=users.query.filter_by(token=token).first()
    if username:
        data = logs.query.filter_by(event_name=event_name).all()
        if data:
            array_logs = []
            for dt in data:
                log = {"username": dt.username, "event_name": dt.event_name,
                       "log_lat": dt.log_lat, "log_lng": dt.log_lng, "created_at": dt.created_at}
                array_logs.append(log)
            return make_response(jsonify(array_logs), 200)
    return jsonify({"msg ":"data tidak ditemukan"})
        
if __name__ == '__main__':
    app.run(debug=True, port=4000)