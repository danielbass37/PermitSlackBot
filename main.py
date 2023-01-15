import slack
import os
import logging
import random
import time
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
from slack.errors import SlackApiError
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

welcome_messages1 = ["Hey", "Hi", "Hello"]
welcome_messages2 = ["Welcome to the community!", "Welcome!",
                     "Good to have you with us!", "Good to see you here.", "Glad to have you here!"]
welcome_messages3 = ["Let me know if you have any questions", "Let me know if you need my help", "I’m available for anything you might need", "Happy to answer questions!",
                     "Let me know if there's anything I can help you with", "Let us know how we can help", "Feel free to ask us anything!", "Let me know if there’s anything I can do for you", "Ask me anything!"]
welcome_messages4 = [":blush:", ":wave:", ":muscle:", ":cherry_blossom:",
                     ":star:", ":check:", ":sparkles:", ":purple_heart:", ":v:"]

# Track last users we messaged
recent_users = []


def delay_message():
    delay = random.randint(40, 45)
    new_time = datetime.now() + timedelta(seconds=delay)
    unix_new_time = time.mktime(new_time.timetuple())
    print(unix_new_time)
    return unix_new_time

def pick_random(arr1, arr2, arr3, arr4):

    result1 = random.choice(arr1)
    result2 = random.choice(arr2)
    result3 = random.choice(arr3)
    result4 = random.choice(arr4)
    return (result1, result2, result3, result4)


def fetch_user_info(user_id):
    try:

        result = client.users_info(
            user=user_id
        )
        logger.info(result.data['user']['real_name'])

        return result.data['user']['name']

    except SlackApiError as e:
        logger.error("Error fetching conversations: {}".format(e))


@slack_event_adapter.on('member_joined_channel')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    global recent_users

    try:

        # avoid duplicate sends - by checking user didn't appear before
        if user_id not in recent_users:
            result = pick_random(welcome_messages1, welcome_messages2,
                                 welcome_messages3, welcome_messages4)
            custom_text = result[0] + ' <@' + fetch_user_info(
                user_id) + '>! ' + result[1] + ' ' + result[2] + ' ' + result[3]

            # Logging to see potential errors
            #logging.info(event, channel_id, user_id, custom_text)

            client.chat_scheduleMessage(
                channel=channel_id, text=custom_text, post_at=delay_message(), as_user=True, token=os.environ['SLACK_USER_TOKEN'])

            # remember user
            recent_users.append(user_id)

            # limit how far we remember to last ten
            if len(user_id) > 10:
                recent_users = recent_users[-10:]
                
    except Exception as e:
        raise e


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    # Enable to run locally using Ngrok
    # app.run(debug=True)
