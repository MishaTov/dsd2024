import requests
from flask import Flask, request
from uuid import uuid4
from random import choice
from hazelcast import HazelcastClient


app = Flask(__name__)

log_urls = ['http://localhost:5001', 'http://localhost:5002', 'http://localhost:5003']
msg_urls = ['http://localhost:5004', 'http://localhost:5005']


def check_available_service():
    available_log_services, available_msg_services = [], []
    for url in log_urls:
        try:
            response = requests.get(url, timeout=0.2)
            if response.status_code == 200:
                available_log_services.append(url)
        except (requests.ConnectionError, requests.ReadTimeout):
            continue
    for url in msg_urls:
        try:
            response = requests.get(url, timeout=0.5)
            if response.status_code == 200:
                available_msg_services.append(url)
        except (requests.ConnectionError, requests.ReadTimeout):
            continue
    return available_log_services, available_msg_services


@app.route('/', methods=['GET', 'POST'])
def handler():
    log_services, msg_services = check_available_service()
    if not log_services or not msg_services:
        return '<h1>Services are not available</h1>', 503
    if request.method == 'GET':
        return f'from logging service: {requests.get(choice(log_services)).text} <p>' \
               f'from messages service: {requests.get(choice(msg_services)).text}'
    elif request.method == 'POST':
        msg = request.form['msg']
        data = {'uuid': str(uuid4()), 'msg': msg}
        client = HazelcastClient()
        msg_queue = client.get_queue('messages').blocking()
        msg_queue.offer(msg)
        return requests.post(choice(log_services), data=data).text


if __name__ == '__main__':
    app.run(debug=True, port=5000)
