"""Scipt for setting a webhook for a Viber bot."""
import os
import requests
import json
import django
from django.conf import settings
import os,sys,inspect


current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crewing.settings")
django.setup()


# Setting up webhook parameters
auth_token = settings.VIBER_TOKEN
print(auth_token)
URL = 'https://60caa1ca8453.ngrok.io/vbbot/' + auth_token
hook = 'https://chatapi.viber.com/pa/set_webhook'
headers = {'X-Viber-Auth-Token': auth_token}
body = dict(url=URL,
            event_types=['unsubscribed',
                         'conversation_started',
                         'message',
                         'seen',
                         'delivered'])

# Sending POST request to apply a webhook, and printing results
r = requests.post(hook, json.dumps(body), headers=headers)
print(r.json())
