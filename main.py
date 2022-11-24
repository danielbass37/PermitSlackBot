import slack
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
from slack.errors import SlackApiError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
#BOT_ID = client.api_call(auth.test)['user_id']


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
    custom_text = 'Welcome <@' + fetch_user_info(user_id) + '>'

    # if BOT_ID != user_id

    client.chat_postMessage(channel=channel_id, text=custom_text)


if __name__ == "__main__":
    #app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    app.run(debug=True)
