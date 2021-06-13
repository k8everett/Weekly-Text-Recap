from datetime import datetime, timedelta, timezone, date

from Contacts import CONTACTS_CSV

import pandas as pd

# Timestamp for today and previous week
TODAY = datetime.utcnow().timestamp()
PREVIOUS_WEEK = TODAY - timedelta(weeks=1).total_seconds()

# Constants to convert Unix time to Mac time in UTC
ONE_BILLION = 1000000000
JAN_1 = datetime(2001, 1, 1, tzinfo=timezone.utc).timestamp()


class WeeklyTexts:
    """This class updates the weekly_messages.db with data from the previous week's texts.

    """

    def __init__(self, chat_db, message_db):
        """WeeklyTexts __init__ method

        Args:
            chat_db (Connection): Connection to chat.db
            message_db (Connection): Connection to weekly_messages.db
        """
        self._chat_db = chat_db
        self._message_db = message_db
        self._messages = pd.read_sql_query('''SELECT text, handle_id, guid, date, cache_roomnames, 
                                                    associated_message_guid, associated_message_type
                                                    FROM message''', self._chat_db)

    def filter_messages(self):
        """Filter the chat database for messages from the past week in the given group chat and update
        weekly_messages.db.

        Returns:
            DataFrame containing the current week's messages

        """
        contact_df = pd.DataFrame(pd.read_csv(CONTACTS_CSV))
        group_name = contact_df.at[0, "cache_roomnames"]
        converted_today = self._convert_time(TODAY)
        converted_prev_week = self._convert_time(PREVIOUS_WEEK)

        # Filter messages for the group chat and current week
        current_messages_df = self._messages.query("cache_roomnames == @group_name & @converted_prev_week <= date "
                                                     "& date <= @converted_today & text.notnull()", False)

        # Attach contact info to the messages
        current_week_df = current_messages_df.join(contact_df.set_index("handle_id"), on="handle_id", lsuffix="_l",
                                                   how="left")

        # Update message database with new table for this week's messages
        current_week_df.to_sql("week_of_{}".format(date.today() - timedelta(weeks=1)), self._message_db, if_exists="replace")

        return current_week_df.copy()

    def _convert_time(self, time):
        """Convert Unix time to Mac time.

        Args:
            time (float): Time to be converted

        Returns:
            float: Converted time

        """
        return (time - JAN_1) * ONE_BILLION
