import getpass
from os import path
import os
import sqlite3
import sys
from sqlite3 import OperationalError

from Contacts import Contacts
from Email import Email
from WeeklyTexts import WeeklyTexts

# Path to the user's chat.db
CHAT_DB_PATH = "/Users/{}/Library/Messages/chat.db".format(getpass.getuser())

# Path to the user's weekly_messages.db
WEEKLY_MESSAGES_DB_PATH = path.join(os.getcwd(), "weekly_messages.db")


class Controller:
    """Controller class for this project.

    """

    def __init__(self):
        """__init__ method for the Controller class.

        """
        try:
            self._chat_db = sqlite3.connect(CHAT_DB_PATH)
        except OperationalError:
            print("Cannot access chat database.\nGo to Settings->Security and Privacy->Privacy->Full Disk Access.\n"
                  "Give access to the application you are running and restart the program.")
            sys.exit(1)

        self._contacts = Contacts(self._chat_db).get_contacts_df()

        try:
            self._message_db = sqlite3.connect(WEEKLY_MESSAGES_DB_PATH)
        except OperationalError:
            print("Could not connect to the database server.")
            sys.exit(1)

    def start(self):
        """Filter messages from the previous week and send the email update.

        """
        # Update weekly_messages database
        filtered_messages = WeeklyTexts(self._chat_db, self._message_db).filter_messages()

        # Format and send email with highlights from the week's messages
        email_msg = Email(filtered_messages, self._contacts)
        email_msg.send_email()





