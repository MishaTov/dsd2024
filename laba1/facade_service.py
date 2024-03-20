import requests
from flask import Flask, request
from uuid import uuid4


app = Flask(__name__)


msg_url = 'http://localhost:5001'
log_url = 'http://localhost:5002'


@app.route('/', methods=['GET', 'POST'])
def handler():
    if request.method == 'GET':
        return f"{requests.get(log_url).text} ||| {requests.get(msg_url).text}"
    elif request.method == 'POST':
        msg = request.form['msg']
        data = {'uuid': str(uuid4()),  'msg': msg}
        return requests.post(log_url, data=data).text


if __name__ == '__main__':
    app.run(debug=True, port=5000)
