import pandas as pd

CONTACTS_CSV = "contacts.csv"

class Contacts:
    """This class updates the CSV containing contact information.

    """

    def __init__(self, chat_db):
        """__init__ method for Contacts class.

        Args:
            chat_db (Connection): Connection to chat.db
        """
        self._chat_db = chat_db
        self._contacts = pd.DataFrame(pd.read_csv(CONTACTS_CSV, header=0))

        if "handle_id" not in self._contacts.columns and "cache_roomnames" not in self._contacts.columns:
            self._update_contacts()

    def get_contacts_df(self):
        """Get contacts DataFrame.

        Returns:
            DataFrame: Contains contact info

        """
        return self._contacts

    def _update_contacts(self):
        """Attach the contacts' handle_id and group chat identifier to their CSV contact info.

        """
        self._handle_id()
        self._chat_name()
        self._contacts.to_csv(CONTACTS_CSV, index_label=False, index=False)

    def _handle_id(self):
        """Match contacts with their handle id.

        """
        handle_id_data = pd.read_sql_query('''SELECT ROWID, id, service 
                                              FROM handle''', self._chat_db).set_index(["id", "service"])

        # Phone number of the chat.db being searched
        owner = pd.read_sql_query("SELECT destination_caller_id FROM message", self._chat_db).dropna()
        unique_vals = owner.at[owner.size - 1, "destination_caller_id"]
        self._contacts.insert(len(self._contacts.columns), "handle_id", 0)

        # Iterate through all the contacts to find their handle id.
        for i, row in enumerate(self._contacts.itertuples(False)):
            phone_number = getattr(row, "phone_number")
            email_add = getattr(row, "email")

            # Check if phone number is an actual phone number or an email address being used
            if "@" not in phone_number:
                phone_number = "+" + phone_number

            phone_data = handle_id_data.xs((phone_number, "iMessage"))
            phone_rowid = phone_data["ROWID"]

            # Figure out which phone number's chat.db is being used, since their handle_id will be 0 in group chats
            if phone_number in unique_vals:
                self._contacts.at[i, "handle_id"] = 0
            else:
                self._contacts.at[i, "handle_id"] = phone_rowid

    def _chat_name(self):
        """Match the group chat name to its chat identifier in the database.

        """
        chat_id_data = pd.read_sql_query('''SELECT display_name, room_name 
                                            FROM chat''', self._chat_db).set_index("display_name")

        # Homogenize group chat name from CSV and chat database
        chat_id_data.index = chat_id_data.index.str.casefold()
        group_chat_name = self._contacts.get("chat_name")[0].casefold()

        chat_id = chat_id_data.at[group_chat_name, "room_name"]
        self._contacts.insert(len(self._contacts.columns), "cache_roomnames", chat_id)

