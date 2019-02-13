from google.cloud import pubsub_v1
import redis, json, time, os

class JSONObject:
     def __init__(self, d):
         self.__dict__ = d

r = redis.Redis(host='redis')
project_id     = os.environ.get('GCP_PROJECT_ID') or 'project id error'
apply_request  = os.environ.get('GCP_PUBSUB_REQUEST_NAME') or 'request name error'
apply_response = os.environ.get('GCP_PUBSUB_RESPONSE_NAME') or 'response name error'
hostname       = os.environ.get('HOSTNAME') or 'unknown'


subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, apply_request)

def read_redis(key):
    return json.loads(r.get(key), object_hook=JSONObject).data


def callback(message):
    message.ack()
    print('Received message: {}'.format(message))
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, apply_response)

    item=read_redis(message.data.decode("utf-8"))
    publisher.publish(topic_path
                      , data      = message.data
                      , client_id = message.attributes.get('client_id')
                      , item      = item)



subscriber.subscribe(subscription_path, callback=callback)

# The subscriber is non-blocking, so we must keep the main thread from
# exiting to allow it to process messages in the background.
print('Listening for messages on {}'.format(subscription_path))
while True:
    time.sleep(0.5)