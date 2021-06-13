# WeeklyTextRecap
This program analyzes an iMessage user's chat database for messages in a given group chat from the previous week. The user will be able to set the program to automatically send a weekly email, from a Gmail account, to all members of the group chat recapping the messages that were sent. To automate sending the email on a Mac, add a new task to Crontab:\ 
* * * * [DAY_OF_WEEK] python3 project_directory/WeeklyTextsDriver.py (Last updated 6/13)

# Required Files
- contacts.csv: A CSV file containing the contact info of the group chat members with the following columns filled in for each person: first_name, last_name, phone_number, email, chat_name
- login.env: USER_NAME=your.email@gmail.com\
             PASSWORD=yourPassword
