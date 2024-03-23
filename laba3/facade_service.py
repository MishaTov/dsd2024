import requests
from flask import Flask, request
from uuid import uuid4
from random import choice

app = Flask(__name__)

msg_url = 'http://localhost:5001'
log_urls = ['http://localhost:5002', 'http://localhost:5003', 'http://localhost:5004']


def check_available_service():
    available_services = []
    try:
        requests.get(msg_url, timeout=0.2)
    except (requests.ConnectionError, requests.ReadTimeout):
        return []
    for url in log_urls:
        try:
            response = requests.get(url, timeout=0.2)
            if response.status_code == 200:
                available_services.append(url)
        except (requests.ConnectionError, requests.ReadTimeout):
            continue
    return available_services


@app.route('/', methods=['GET', 'POST'])
def handler():
    available_services = check_available_service()
    if not available_services:
        return '<h1>Services are not available</h1>', 503
    if request.method == 'GET':
        return f'{requests.get(choice(available_services)).text} ||| {requests.get(msg_url).text}'
    elif request.method == 'POST':
        msg = request.form['msg']
        data = {'uuid': str(uuid4()), 'msg': msg}
        return requests.post(choice(available_services), data=data).text
    else:
        return '<h1>That request method is not supported</h1>'


if __name__ == '__main__':
    app.run(debug=True, port=5000)
