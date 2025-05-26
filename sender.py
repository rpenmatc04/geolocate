from EmailSender import EmailSender
from config import ALERTS_USED
import datetime
import math
import logging 
from calculations import calculate_level

logger = logging.getLogger(__name__)

class Sender: 

    def __init__(self, sender, recepient, password, db): 
        self.mailserver = EmailSender(sender, password, recepient)
        self.db = db

    def generate_time_fields(curr_time): 
        data = datetime.datetime.fromtimestamp(curr_time)
        return data.strftime('%-I:%M:%S %p'), data.strftime('%B %-d, %Y')
    

    def most_recent_information(self, id): 
        body = ""
        if not self.db: 
            return body
        key = f"Client{id}"
        value = self.db.get_recent(key)
        if value: 
            time_str, date = Sender.generate_time_fields(float(value['time_stamp']))
            body = f"The most recent information for Client {id} is that they were {value['decision']} the boundary on {date} at {time_str} with the GeoJSON data listed below: \n {value['geojson']}"
        return body
        
    def generate_failure(self, id):
        subject = f"Alert - API failed for Client {id}"
        body = f"The API call failed or returned invalid data for Client {id}. \n \n {self.most_recent_information(id)}"
        self.generate_email(subject, body)

    def generate_return(self, id, time_stamp, past_time): 
        subject = f"Alert - Client {id} has returned to their boundary"
        time_str, date = Sender.generate_time_fields(time_stamp)
        body = f"The Client {id} has returned to their boundary on {date} at {time_str}, within {math.ceil((time_stamp - past_time) / 60)} minutes"
        self.generate_email(subject, body)
    
    def generate_exit_header(alert_used, id, distance): # Warnings based on distance to boundary!
        if not alert_used: 
            body = f"Alert - Client {id} is OUTSIDE their boundary!" 
        else: 
            level = calculate_level(distance) 
            body = f"[{level} level Alert] - Client {id} is OUTSIDE their boundary!"
        return body 

    def generate_exit(self, id, point, closest_boundary, distance, time_stamp):
        # print("LOCATION CALCULATION:")
        # start_temp_time = time.time()
        # location = app.reverse({point.y, point.x})
        # end_temp_time = time.time() 
        # print(end_temp_time - start_temp_time)

        time_str, date = Sender.generate_time_fields(time_stamp)
        body = f"The Client {id}'s location on {date} at {time_str} is {point.y, point.x}. \n \nThe nearest boundary point is at {closest_boundary.y, closest_boundary.x}, an estimated distance of {round(distance, 2)} miles away." 
        subject = Sender.generate_exit_header(ALERTS_USED, id, distance)
        self.generate_email(subject, body)

    def generate_email(self, subject, body):
        # Single-Threaded
        try: 
            self.mailserver.send_synch_message(subject, body)
        except Exception as e:
            logger.error(f"failed to send email: {e}")
        # Multi-Threaded
        # executor.submit(mailserver.send_synch_message, subject, body)