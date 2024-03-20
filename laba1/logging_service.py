from flask import Flask, request


app = Flask(__name__)


messages = {}


@app.route('/', methods=['GET', 'POST'])
def response():
    if request.method == 'GET':
        return ', '.join(messages.values())
    elif request.method == 'POST':
        uuid, msg = request.form['uuid'], request.form['msg']
        messages[uuid] = msg
        print(f'New record:\n\tuuid: {uuid}\n\ttext: {msg}')
        return 'Success'


if __name__ == '__main__':
    app.run(debug=True, port=5002)
