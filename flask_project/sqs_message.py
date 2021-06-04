import boto3
import os

AWS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_ID = os.environ.get('AWS_KEY_ID')


def send_sqs_message():
    try:
        client = boto3.resource('sqs', region_name='us-east-2',
                                aws_access_key_id=AWS_ID,
                                aws_secret_access_key=AWS_KEY)
        queue = client.get_queue_by_name(QueueName='EmailQueue')
        response = queue.send_message(MessageBody='A-G')
        response1 = queue.send_message(MessageBody='H-Z')
    except Exception as e:
        print(e)


def receive_sqs_message():
    try:
        client = boto3.resource('sqs', region_name='us-east-2',
                                aws_access_key_id=AWS_ID,
                                aws_secret_access_key=AWS_KEY)
        QueueUrl = "https://us-east-2.queue.amazonaws.com/328370162946/EmailQueue"
        queue = client.get_queue_by_name(QueueName='EmailQueue')
        response = queue.receive_messages(MaxNumberOfMessages=1, VisibilityTimeout=120, WaitTimeSeconds=13)
        # response[0].delete()
        return response
    except Exception as e:
        print(e)


if __name__ == "__main__":
    send_sqs_message()
    res = receive_sqs_message()
    print(res[0].body)
    res[0].delete()