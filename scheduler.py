from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

def book_timeslot(event_description,booking_time,input_email):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    
    current_date = datetime.datetime.now().date().isoformat()
    start_time = f'{current_date}T{booking_time}:00+02:00'  # Adjust +02:00 to your actual time zone if needed
    end_time_hour = str(int(booking_time[:2]) + 1).zfill(2)
    end_time = f'{current_date}T{end_time_hour}{booking_time[2:]}:00+02:00'  # Adjust +02:00 to your actual time zone if needed


    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Booking a time slot....')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])       
    if not events:
        event = {
        'summary': 'Hair Cut Appointment',
        'location': 'Germany',
        'description': str(event_description) + 'with AutomationFeed',
        'start': {
        'dateTime': start_time,
        'timeZone': 'Europe/Berlin',
        },
        'end': {
        'dateTime': end_time,
        'timeZone': 'Europe/Berlin',
        },
        'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=1'
        ],
        'attendees': [
        {'email': 'automationfeed@gmail.com'},
        {'email': str(input_email)},
        ],
        'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
        ],
        },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"start event {start}")
        print ('Event created: %s' % (event.get('htmlLink')))
        return True

    else:
        # --------------------- Check if there are any similar start time --------------------- 
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            if start==start_time:
                print('Already book....')
                return False
        # -------------------- Break out of for loop if there are no apppointment that has the same time ----------
        event = {
        'summary': 'Hair Cut Appointment',
        'location': 'Germany',
        'description': str(event_description) + 'with AutomationFeed',
        'start': {
        'dateTime': start_time,
        'timeZone': 'Europe/Berlin',
        },
        'end': {
        'dateTime': end_time,
        'timeZone': 'Europe/Berlin',
        },
        'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=1'
        ],
        'attendees': [
        {'email': 'automationfeed@gmail.com'},
        {'email': str(input_email)},
        ],
        'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
        ],
        },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print ('Event created: %s' % (event.get('htmlLink')))
        return True
    


if __name__ == '__main__': 
    input_email='test@gmail.com'
    booking_time='14:00' 
    result=book_timeslot('Dye',booking_time,input_email)