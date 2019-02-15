from google.cloud import pubsub_v1
import requests, time, os

project_id     = os.environ.get('GCP_PROJECT_ID') or 'project id error'
apply_request  = os.environ.get('GCP_PUBSUB_REQUEST_NAME') or 'request name error'
apply_response = os.environ.get('GCP_PUBSUB_RESPONSE_NAME') or 'response name error'
hostname       = os.environ.get('HOSTNAME') or 'unknown'

subscriber = pubsub_v1.SubscriberClient()
topic_path = subscriber.topic_path(project_id, apply_response)
subscription_path = subscriber.subscription_path(
    project_id, '{}-{}'.format(apply_response, hostname))

subscriber.create_subscription(subscription_path, topic_path)
subscription_path = subscriber.subscription_path(project_id,'{}-{}'.format(apply_response, hostname))

def callback(message):
    message.ack()
    print("Step 5: Response item name to client: {}, item: {}, name: {}".format(
        message.attributes.get('client_id')
        , message.data.decode("utf-8")
        , message.attributes.get('name')
    ))

    print('Received message: {}'.format(message))
    requests.get('http://127.0.0.1/refresh/{}/{}/{}'
                 .format(message.attributes.get('client_id')
                         , message.data.decode("utf-8")
                         , message.attributes.get('item')))


subscriber.subscribe(subscription_path, callback=callback)

# The subscriber is non-blocking, so we must keep the main thread from
# exiting to allow it to process messages in the background.
print('Listening for messages on {}'.format(subscription_path))
while True:
    time.sleep(0.5)