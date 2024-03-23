import requests


url = 'http://localhost:5000'

data_ = {f'msg{i}': f'message {i}' for i in range(10)}
data = {}
for i in data_:
    data['msg'] = data_[i]
    response = requests.post(url, data=data)
    print(response.content.decode(), f'({response.status_code})')



