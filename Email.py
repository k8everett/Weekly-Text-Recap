from email.message import EmailMessage
import smtplib


class Email:
    def __init__(self, weekly_messages, contacts):
        self._weekly_messages = weekly_messages
        self._contacts = contacts
        self._num_contacts = self._contacts.email.nunique()

        # Dictionary of messages that received reactions ("Loved", "Liked", "Emphasized", "Disliked", "Laughed at",
        # "Questioned)
        self._reacted_messages = {}
        self._email = EmailMessage()
        self._filter_for_reaction_messages()

    def _filter_for_reaction_messages(self):
        reactions = self._weekly_messages["associated_message_type"] != 0
        reaction_msgs = self._weekly_messages[reactions]

        # Create a dictionary of messages with reactions and the people who reacted to them
        for message in reaction_msgs.itertuples(False):
            text = message.text

            # Filter out non-text based messages that were reacted to
            if "“" in text:
                reaction_end_index = text.index("“")
                reaction_person_type = "{} {} this message".format(message.first_name,
                                                                   text[:reaction_end_index - 1].lower())
                text = text[reaction_end_index + 1:len(text) - 1].rstrip()

                if text in self._reacted_messages:
                    # Reaction was removed
                    if message.associated_message_type >= 3000:
                        self._reacted_messages[text].remove(reaction_person_type)
                    else:
                        self._reacted_messages[text].append(reaction_person_type)
                else:
                    self._reacted_messages[text] = [reaction_person_type]

    def _format_reaction_message_text(self):
        self._email.set_content()





