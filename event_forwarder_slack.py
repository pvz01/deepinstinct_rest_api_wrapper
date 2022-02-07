# event_forwarder_slack.py
# Author: Patrick Van Zandt, Principal Professional Services Engineer
# February 2022

# This script provides an example of how to use the Deep Instinct REST API
# Wrapper published at https://github.com/pvz01/deepinstinct_rest_api_wrapper
# to forward new DI events to Slack using a Slack Incoming Webhook.

# This script is provided as-is and with no warranty. Use at your own risk, and
# please test in a non-production environment first.

# PREREQUISITES
# 1. Python 3.8 or later
# 2. Deep Instinct REST API Wrapper
# 3. Third-party libraries (strongly recommend to install Anaconda)
# 4. Network access to management server on port 443
# 5. API Key with minimum of Read Only access

# USAGE
# 1. Save the latest version of both this file (event_forwarder_slack.py) and
#    the DI API Wrapper (deepinstinct30.py) to the same folder on disk.
# 2. Review and adjust configuration in-line below, then save changes.
# 3. Execute the script with this command: python event_forwarder_slack.py


#---import required libraries---
import time, json, requests, datetime, deepinstinct30 as di


#---configuration---
di.fqdn = 'FOO.customers.deepinstinctweb.com'
di.key = 'BAR'

# When restarting script, set this to the previous highest event ID to avoid
# resending previously sent events. Otherwise set to 0.
max_event_processed_previously = 0

# Define sleep time between queries to server in seconds (default 5 minutes)
sleep_time_in_seconds = 300

# Define a webhook URL for sending event data to Slack
webhook_url = 'https://hooks.slack.com/workflows/REDACTED'

# Define a list of fields to remove from events before sending to Slack
fields_to_remove = ['msp_name', 'msp_id', 'tenant_name', 'tenant_id',
                    'mitre_classifications',
                    'recorded_device_info',
                    'file_status', 'sandbox_status']

# Define search parameters when querying DI server for new events
search_parameters = {}
#search_parameters['status'] = ['OPEN', 'CLOSED']
#search_parameters['type'] = ['STATIC_ANALYSIS', 'RANSOMWARE_FILE_ENCRYPTION']
#search_parameters['threat_severity'] = ['HIGH', 'VERY_HIGH']


#---define methods used at runtime---

# a method for forwarding a single event to Slack using the provided webhook_url
def send_event_to_slack(event):
    slack_data = {'event_data': json.dumps(event, indent=4)}
    response = requests.post(webhook_url, json=slack_data, headers={'Content-Type': 'application/json'})

# a method to remove a key from a dictionary if it is present
def remove_key(dict, key):
    if key in dict:
        dict.pop(key)

# a method to remove unwanted fields from event data
def sanitize_event(event):
    for field in fields_to_remove:
        remove_key(event, field)


#---runtime---
while True:
    print('Getting new events with id greater than', max_event_processed_previously)

    try:
        new_events = di.get_events(minimum_event_id=max_event_processed_previously, search=search_parameters)
    except:
        now = datetime.datetime.now()
        print(now.strftime("%H:%M"), 'ERROR:', e)
        new_events = []

    print(len(new_events), 'events were returned')

    if len(new_events) > 0:

        for event in new_events:
            sanitize_event(event)
            print('Sending event', event['id'], 'to Slack')
            try:
                send_event_to_slack(event)
            except requests.exceptions.RequestException as e:
                now = datetime.datetime.now()
                print(now.strftime("%H:%M"), 'ERROR:', e)
            if event['id'] > max_event_processed_previously:
                max_event_processed_previously = event['id']

    print('max_event_processed_previously is now', max_event_processed_previously)
    print('Sleeping for', sleep_time_in_seconds, 'seconds')
    time.sleep(sleep_time_in_seconds)