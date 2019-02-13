from flask import Flask
from flask import render_template, json
from flask_socketio import SocketIO
from google.cloud import pubsub_v1
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

project_id     = os.environ.get('GCP_PROJECT_ID') or 'project id error'
apply_request  = os.environ.get('GCP_PUBSUB_REQUEST_NAME') or 'request name error'
apply_response = os.environ.get('GCP_PUBSUB_RESPONSE_NAME') or 'response name error'
hostname       = os.environ.get('HOSTNAME') or 'unknown'

socketio = SocketIO(app)

# 連結首頁
@app.route("/")
def index():
    return render_template('index.html', title="Pub/Sub Connect")

@socketio.on('additem')
def send_message(jsonString):
    data = jsonString['item'].encode('utf-8')
    client_id = jsonString['client']

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, apply_request)

    publisher.publish(topic_path, data=data, client_id=client_id)

    return json.dumps({'errCde':'00','errMsg':''})

@app.route('/refresh/<client_id>/<msg>/<item>')
def refresh(client_id, msg, item):
    socketio.emit('for_private', {'msg': msg, 'item': item }, room=client_id)
    socketio.emit('for_broadcast', {'msg': msg, 'item': item })
    return json.dumps({'errCde':'00','errMsg':''})

@socketio.on('connected')
def connected(jsonString):
    socketio.emit('serverInfo', {'serverName': hostname}, room=jsonString['client'])

if __name__ == '__main__':
    app.debug = True
    socketio.run(app, host='0.0.0.0', port=80)
