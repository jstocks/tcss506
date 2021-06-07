from models import UserModel, WinnerModel
from datetime import date


class Database_access:
    def __init__(self, database1):
        self.db = database1

    def addUser(self, username, email, password):
        """
        Adds a new record to the database
        :param username: String
        :param email: String
        :param password: String
        :return: None
        """
        user = UserModel(username=username)
        user.set_password(password)
        user.email = email
        self.db.session.add(user)
        self.db.session.commit()

    def updateSubscription(self, username, subscription=False):
        """
         Updates the subscription status of the user
        :param username: String
        :param subscription: Boolean
        :return: None
        """
        user = UserModel.query.filter_by(username=username).first()
        user.subscription = subscription
        self.db.session.commit()

    @staticmethod
    def test_subscription_update(username):
        """
        Retrieves the current subscription status of the user
        :param username: String
        :return: Boolean
        """
        user = UserModel.query.filter_by(username=username).first()
        result = user.subscription
        return result

    def reset_password(self, username, password):
        """
        Resets the password of the user
        :param username: String
        :param password: String
        :return: None
        """
        user = UserModel.query.filter_by(username=username).first()
        user.set_password(password)
        self.db.session.commit()

    def delete_record(self, username):
        """
        Deletes the user from the database
        :param username: String
        :return: None
        """
        user = UserModel.query.filter_by(username=username).first()
        self.db.session.delete(user)
        self.db.session.commit()

    def can_queue_task(self):
        """
        Tries to Insert today's date into the winner table. If successful
        returns True else False.
        :return: Boolean
        """
        try:
            data1 = WinnerModel(date=date.today())
            self.db.session.add(data1)
            self.db.session.commit()
            # print("Added")
            return True
        except Exception as e:
            # print(e)
            return False

    @staticmethod
    def generate_subscriber_list(start, end):
        """
        Generates a list containing emails of the users with their
        subscription set to True, filters the list based on the input
        alphabet range and returns the filtered list containing emails.
        :param start: String (Alphabet range to filter)
        :param end: String (Alphabet range to filter)
        :return: List (containing emails)
        """
        subscribers = UserModel.query.filter_by(subscription=True).all()
        email_list = []
        for subscriber in subscribers:
            email_list.append(subscriber.email)
        result = [string1 for string1 in email_list if ord(start) <= ord(string1[0]) <= ord(end)]
        return result
