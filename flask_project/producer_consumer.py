import time
from datetime import date

from sqs_message import send_sqs_message, receive_sqs_message
from email_generator import send_bulk_weekly


# Producer thread
def producer_thread(db):
    """
    Every hour checks for the desired day of the week and if so ensures
    to send the message to SQS only once by trying to insert
    the date in the date column(with the Unique constraint)
    of the winner table in the database.
    :param db: Object
    :return: None
    """
    while True:
        time.sleep(3600)
        # for debugging purpose
        # f = open("thread1.txt", "w")
        # f.write("daemon_thread1 in the bg!!")
        # f.close()
        # print("daemon_thread1 in the bg!!")
        if date.today().weekday() == 0:
            if db.can_queue_task() is True:
                send_sqs_message()
                # print("msg sent")


# Consumer thread
def consumer_thread(db, app, mail, sender_email):
    """
    Receives message from the SQS and depending on the message
    sends emails with the weekly updates to the subscribers.
    :param db: Object
    :param app: Object
    :param mail: Object
    :param sender_email: String
    :return: None
    """
    while True:
        time.sleep(3660)
        # print("daemon_thread2 in the bg!!")
        try:
            response = receive_sqs_message()
            if len(response) > 0:
                # print(f"response from consumer-sqs message received: {response[0].body}")
                sub_list = db.generate_subscriber_list(response[0].body[0].lower(), response[0].body[-1].lower())
                send_bulk_weekly(app, mail, sender_email, sub_list)
                response[0].delete()
                # print("printing from consumer after msg delete")
        except Exception as e:
            # print(e)
            pass
