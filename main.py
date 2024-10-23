import requests
import datetime
import json
import re
import time
import api_key
from scheduler import book_timeslot

api_key = api_key.api["api_key"]

def check_email(email):
    regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if re.search(regex, email):
        print("Valid Email")
        return True
    else:
        print("Invalid Email")
        return False

def getLastMessage(offset=None):
    url = f"https://api.telegram.org/bot{api_key}/getUpdates"
    if offset:
        url += f"?offset={offset}"
    response = requests.get(url)
    data = response.json()

    # Print the entire response for debugging
    print(f"Response from getUpdates: {json.dumps(data, indent=2)}")

    if 'result' not in data or not data['result']:
        print('No updates found')
        return None, None, None

    last_update = data['result'][-1]
    if 'message' not in last_update:
        print('No message in the last update')
        return None, None, None

    last_msg = last_update['message'].get('text', '')
    chat_id = last_update['message']['chat']['id']
    update_id = last_update['update_id']

    return last_msg, chat_id, update_id

def sendMessage(chat_id, text_message):
    url = f'https://api.telegram.org/bot{api_key}/sendMessage?text={text_message}&chat_id={chat_id}'
    response = requests.get(url)
    return response

def sendInlineMessageForService(chat_id):
    text_message = ('Hi! I am your Hair Stylist Bot!\n'
                    'I can help you book an appointment.\n\n'
                    'You can control me using these commands\n\n'
                    '/start - to start chatting with the bot\n'
                    '/cancel - to stop chatting with the bot.\n\n'
                    'For more information please contact wook.kim@rwth-aachen.de')
    keyboard = {'keyboard': [
                        [{'text':'Cut'}, {'text':'Dye'}]
                        ]}
    key = json.JSONEncoder().encode(keyboard)
    url = f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={text_message}&reply_markup={key}'
    response = requests.get(url)
    return response

def sendInlineMessageForBookingTime(chat_id):
    text_message = 'Please choose a time slot...'
    current_time = datetime.datetime.now()
    current_hour = current_time.hour
    print(f"Current hour: {current_hour}")
    available_slots = [
        
    ]

    if current_hour < 8:
        keyboard = {'keyboard':[
                            [{'text':'08:00'}], [{'text':'10:00'}],
                            [{'text':'12:00'}], [{'text':'14:00'}],
                            [{'text':'16:00'}], [{'text':'18:00'}],
                            ]}
    elif 8 <= current_hour < 10:
        keyboard = {'keyboard':[
                            [{'text':'10:00'}],
                            [{'text':'12:00'}], [{'text':'14:00'}],
                            [{'text':'16:00'}], [{'text':'18:00'}],
                            ]}
    elif 10 <= current_hour < 12:
        keyboard = {'keyboard':[
                            [{'text':'12:00'}], [{'text':'14:00'}],
                            [{'text':'16:00'}], [{'text':'18:00'}],
                            ]}
    elif 12 <= current_hour < 14:
        keyboard = {'keyboard':[
                            [{'text':'14:00'}],
                            [{'text':'16:00'}], [{'text':'18:00'}],
                            ]}
    elif 14 <= current_hour < 16:
        keyboard = {'keyboard':[
                            [{'text':'16:00'}], [{'text':'18:00'}],
                            ]}
    elif 16 <= current_hour < 24:
        keyboard = {'keyboard':[
                            [{'text':'18:00'}],
                            ]}
    else:
        return sendMessage(chat_id, 'Please try again tomorrow')
    
    key = json.JSONEncoder().encode(keyboard)
    url = f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={text_message}&reply_markup={key}'
    response = requests.get(url)
    return response

def run():
    update_id_for_booking_of_time_slot = ''
    prev_last_msg, chat_id, prev_update_id = getLastMessage()

    # Print initial state
    print(f"Initial state: {prev_last_msg}, {chat_id}, {prev_update_id}")

    while True:
        current_last_msg, chat_id, current_update_id = getLastMessage(prev_update_id + 1 if prev_update_id else None)
        
        # Print current state for debugging
        print(f"Current state: {current_last_msg}, {chat_id}, {current_update_id}")

        if current_last_msg is None and current_update_id is None:
            print('No new updates, waiting...')
            time.sleep(1) 
            continue

        if prev_last_msg == current_last_msg and current_update_id == prev_update_id:
            print('continue')
            time.sleep(1) 
            continue
        else:
            if current_last_msg == '/start':
                sendInlineMessageForService(chat_id)
            elif current_last_msg in ['Cut', 'Dye']:
                event_description = current_last_msg
                sendInlineMessageForBookingTime(chat_id)
            elif current_last_msg in ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00']:
                booking_time = current_last_msg
                update_id_for_booking_of_time_slot = current_update_id
                sendMessage(chat_id, "Please enter email address:")
            elif current_last_msg == '/cancel':
                update_id_for_booking_of_time_slot = ''
                continue
            elif update_id_for_booking_of_time_slot != current_update_id and update_id_for_booking_of_time_slot != '':
                if check_email(current_last_msg):
                    update_id_for_booking_of_time_slot = ''
                    sendMessage(chat_id, "Booking please wait.....")
                    input_email = current_last_msg
                    response = book_timeslot(event_description, booking_time, input_email)
                    if response:
                        sendMessage(chat_id, f"Appointment is booked. See you at {booking_time}")
                        continue
                    else:
                        update_id_for_booking_of_time_slot = ''
                        sendMessage(chat_id, "Please try another timeslot and try again tomorrow")
                        continue
                else:
                    sendMessage(chat_id, "Please enter a valid email.\nEnter /cancel to quit chatting with the bot\nThanks!")
          
        prev_last_msg = current_last_msg
        prev_update_id = current_update_id
        time.sleep(1)
        
if __name__ == "__main__":
    run()
