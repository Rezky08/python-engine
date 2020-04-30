from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from handle import handle
import tasks
import copy
import json
import time
from celery.result import AsyncResult

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://127.0.0.1:6379/0',
    CELERY_RESULT_BACKEND='redis://127.0.0.1:6379/0'
)
headers = {
    'Host': 'server.api'
}
url = "http://192.168.1.11/"

celery = tasks.make_celery(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    response = {
        'status': 200,
        'message' : "OK"
    }
    return jsonify(response)


@app.route('/kelompok', methods=['POST'])
def kelompok():
    hd = handle(request.get_json())
    response_json = jsonify(hd.kelompok())
    return response_json


@app.route('/dosen', methods=['POST'])
def dosen():
    req_dict = copy.deepcopy(request.get_json())
    task = kelompok_dosen_process.delay(req_dict)

    response = {
        'status': 200,
        'message': "on Progress",
        'celery_id': task.id
    }
    response_json = jsonify(response)
    return response_json, 200


@app.route('/jadwal', methods=['POST'])
def jadwal():
    req_dict = copy.deepcopy(request.get_json())
    task = jadwal_process.delay(req_dict)
    response = {
        'status': 200,
        'message': "on Progress",
        'celery_id': task.id
    }
    response_json = jsonify(response)
    return response_json, 200


@app.route('/jadwal/result', methods=['GET'])
def jadwal_result():
    json_data = copy.deepcopy(request.get_json())
    task_id = json_data['celery_id']
    task = jadwal_process.AsyncResult(task_id)
    if task.status == "SUCCESS":
        response = {
            'status': task.status,
            'result': task.result
        }
        return jsonify(response), 200
    response = {
        'status': task.status
    }
    return jsonify(response), 200


@app.route('/dosen/result', methods=['GET'])
def dosen_result():
    json_data = copy.deepcopy(request.get_json())
    task_id = json_data['celery_id']
    task = kelompok_dosen_process.AsyncResult(task_id)
    if task.status == "SUCCESS":
        response = {
            'status': task.status,
            'result': task.result
        }
        return jsonify(response), 200
    response = {
        'status': task.status
    }
    return jsonify(response), 200


@celery.task()
def kelompok_dosen_process(req_dict):
    hd = handle(req_dict)
    result = hd.dosen()
    return result


@celery.task()
def jadwal_process(req_dict):
    hd = handle(req_dict)
    result = hd.jadwal()
    return result


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
