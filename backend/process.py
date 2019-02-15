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
topic_path = subscriber.topic_path(project_id, apply_request)
subscription_path = subscriber.subscription_path(
    project_id, '{}-{}'.format(apply_request, hostname))

# 在服務啟動時建立訂閱
subscriber.create_subscription(subscription_path, topic_path)


def read_redis(key):
    print("Step 3: Backend query redis service. item: {}".format(key))
    return json.loads(r.get(key), object_hook=JSONObject).data


def callback(message):
    message.ack()
    print("Step 2: Backend received request from pubsub. ")
    publisher = pubsub_v1.PublisherClient()
    response_topic_path = publisher.topic_path(project_id, apply_response)

    # 由 Redis 讀出指定項目內容
    name=read_redis(message.data.decode("utf-8"))

    # 將 response 發佈至 pubsub
    publisher.publish(response_topic_path
                      , data      = message.data
                      , client_id = message.attributes.get('client_id')
                      , name      = name)
    print("Step 4: Backend sent response to pubsub. client: {}".format(
        message.attributes.get('client_id')
    ))


subscriber.subscribe(subscription_path, callback=callback)

# The subscriber is non-blocking, so we must keep the main thread from
# exiting to allow it to process messages in the background.
print('Listening for messages on {}'.format(subscription_path))
while True:
    time.sleep(0.5)