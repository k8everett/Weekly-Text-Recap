import os
import smtplib
from datetime import date, timedelta

import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv("login.env")
USER = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")

class Email:
    """Class to format and send Email.

    """

    def __init__(self, weekly_messages, contacts):
        """__init__ method for the Email class.

        Args:
            weekly_messages (DataFrame): DataFrame of current week's messages.
            contacts (DataFrame): DataFrame of contact info
        """
        self._weekly_messages = weekly_messages
        self._contacts = contacts
        self._num_contacts = self._contacts.email.nunique()

        # Dictionary of messages that received reactions ("Loved", "Liked", "Emphasized", "Disliked", "Laughed at",
        # "Questioned)
        self._reacted_messages = dict()
        self._email = MIMEMultipart()

    def _filter_for_reaction_messages(self):
        """Create a dictionary of messages that received reactions from more than 1/3 of the group.

        """
        reactions = self._weekly_messages["associated_message_type"] != 0
        reaction_msgs = self._weekly_messages[reactions]

        # Create a dictionary of messages with reactions and the people who reacted to them
        for message in reaction_msgs.itertuples(False):
            text = message.text

            # Filter out non-text based messages that were reacted to
            if "“" in text:
                reaction_end_index = text.index("“")

                # Format the message/sender and the reactor for HTML
                reaction_person_type = '<span style="color: DeepPink"> {}</span> {} this message'.format(
                    message.first_name,
                    text[:reaction_end_index - 1].lower())

                # Find associated message
                associated_message_id = message.associated_message_guid
                if associated_message_id.startswith("bp:"):
                    associated_message_id = associated_message_id[3:]
                else:
                    associated_message_id = associated_message_id[4:]

                original_msg_sender = self._weekly_messages.set_index("guid").xs(associated_message_id).first_name
                text = '<span style="color: BlueViolet"> {}</span>'.format(original_msg_sender) + ": " \
                       + text[reaction_end_index + 1:len(text) - 1].rstrip()

                if text in self._reacted_messages:

                    # Reaction was removed
                    if message.associated_message_type >= 3000:
                        self._reacted_messages[text].remove(reaction_person_type)
                    else:
                        self._reacted_messages[text].append(reaction_person_type)
                else:
                    self._reacted_messages[text] = [reaction_person_type]

        # Filter for messages with reactions from at least 1/3 of the group
        self._reacted_messages = {k: v for k, v in self._reacted_messages.items() if len(v) >= self._num_contacts / 3}

    def _format_reaction_message_text(self):
        """Format the text of messages with reactions for the email.

        Returns:
            String: formatted text or None if no messages had reactions from 1/3 of the group

        """
        self._filter_for_reaction_messages()
        messages = ""
        for k, v in self._reacted_messages.items():
            messages += "<p>" + k + "<br>" + ", ".join(v) + "</p>"

        if len(messages) > 0:
            text = """
            <html>
                <body>
                    <p style="color: BlueViolet; font-size:200%;"><b>Messages With the Most Reactions</b><br>
                    {}</p>
                </body>
            </html>
            """.format(messages)
            return text
        return None

    def _format_links(self):
        """Format the text of links in the group chat for the email

        Returns:
            object: formatted text or None if there were no links

        """
        messages = self._weekly_messages.query("associated_message_type == 0")
        links = ""

        for message in messages.itertuples(False):
            if "https://" in message.text or "www." in message.text:
                links += "<p><a href='url'>" + message.text + "</a></p>"

        if len(links) > 0:
            text = """
            <html>
                <body>
                    <p style="color: BlueViolet; font-size:200%;"><b>Links to Check Out</b><br>
                    {}</p>
                </body>
            </html>
            """.format(links)
            return text
        return None

    def _pyramid(self):
        """Create a ranking of group members from most to least texts.

        Returns:
            String: formatted text

        """
        messages = self._weekly_messages.query("associated_message_type == 0")
        count = dict()

        for message in messages.itertuples(False):
            name = message.first_name + " " + message.last_name
            if name in count:
                count[name] += 1
            else:
                count[name] = 1

        count = [k for k, v in sorted(count.items(), key=lambda item: item[1], reverse=True)]
        rank = ""

        for person in count:
            rank += "<p> {} </p>".format(person)

        text = """
        <html>
            <body>
                <p style="color: BlueViolet; font-size:200%;"><b>Pyramid</b></p>
                <p><img src=https://media1.popsugar-assets.com/files/thumbor/M00pIkZnSCFIA4eF4854Cep2DdE/fit-in/1024x1024/filters:format_auto-!!-:strip_icc-!!-/2017/03/17/725/n/1922283/6aa69e9cb414a8ab_phr9xgp7482qbwe/i/During-Opening-Credits-When-She-Looked-Feckin-Fierce-AF.gif alt='Do you wanna be on top?' 
                style="width:250px;height:140px;"><br>
                {}
                 <p><img src=https://media.giphy.com/media/VUwLU2HynqQkU/giphy.gif alt='Everybody's replacable' 
                 style="width:250px;height:140px;"><br>
            </body>
        </html>
        """.format(rank)
        return text

    def _format_email(self):
        """Format the body of the email.

        """
        reaction_msgs = self._format_reaction_message_text()
        links = self._format_links()
        pyramid = self._pyramid()

        if reaction_msgs:
            self._email.attach(MIMEText(reaction_msgs, "html"))
        if links:
            self._email.attach(MIMEText(links, "html"))
        self._email.attach(MIMEText(pyramid, "html"))

    def send_email(self):
        """Send the email.

        """
        self._format_email()

        group_name = self._contacts.at[0, "chat_name"]
        self._email['Subject'] = "{} Update, Week Of: {}".format(group_name, date.today() - timedelta(weeks=1))
        self._email['From'] = USER
        self._email['To'] = ", ".join(pd.unique(self._contacts["email"]))

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(USER, PASSWORD)
        server.send_message(self._email)
