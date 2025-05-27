
import logging 
import time
import requests
from config import DURATION, PHLEBOTOMISTS, SENDER, RECEPIENT, PASSWORD, REDIS_USED, REDIS_URL, ALERTS_USED, INTERVAL, MULTI_THREADED, NUM_THREADS
from api import poll_status, extract_information, poll_status_with_time
from calculations import covers, cover_information, generate_structures, calculate_level
from sender import Sender
from database import Database
from concurrent.futures import ThreadPoolExecutor

def monitor_simple_loop(): 
    
    t_end = time.time() + DURATION # 1 HOUR
    session = requests.Session() # reuse existing TCP connection
    distances = {key:0.0 for key in PHLEBOTOMISTS} # distances[key] = most recent distance
    boundary_changes_times = {key:-1 for key in PHLEBOTOMISTS} # time of most status change
    history = {key:"IN" for key in PHLEBOTOMISTS} # Most Recent State (IN, OUT, UNSAFE) - Unsafe = API failed

    if REDIS_USED: 
        database = Database(REDIS_URL) # Used for most recent info
    else: 
        database = None
    
    sender = Sender(SENDER, RECEPIENT, PASSWORD, database)


    while time.time() < t_end:

        # print("Taking Track of Timestamps")

        # start_time = time.time()
        statuses = [] 
        times = [] 

        for id in PHLEBOTOMISTS:
            current_time = time.time()
            times.append(current_time) # Time of API request 
            statuses.append(poll_status(session, id)) # API result

        # temp_end_time = time.time()
        # print(f"API results took: {temp_end_time - start_time} seconds")


        for itr, (id, status) in enumerate(zip(PHLEBOTOMISTS, statuses)):
            curr_time = times[itr]
            if (status == -1): # Alert due to exception raised during GET request
                sender.generate_failure(id)
                continue

            pointVals, polygonVals = extract_information(status)
            if pointVals == -1: # Alert due to exception raised with the JSON returned
                sender.generate_failure(id)
                continue 
            
            try: 
                polygon, point = generate_structures(pointVals, polygonVals)
            except Exception as e:
                logger.error(f"Failed to generate points or polygons for Clinician {id} data: {e}, {status}")
                sender.generate_failure(id)# Alert due to issue with Data itsself
                continue
                
            
            decision, distance, closest_point = cover_information(point, polygon) # (IN / OUT, distance in miles, closest point) - (IN, 0.0, current_point) when inside

            if ALERTS_USED: # Uses the distance to send the most up-to-date warning (Low -> High)
                different_level = (decision == "OUT" and calculate_level(distance) != calculate_level(distances[id])) # Can use this for more informative email responses
            else: 
                different_level = False
            
            if decision != covers(point, polygon): 
                status = str(status).replace("'", '"')
                logger.error(f"floating point rounding error: {distance}")

            # Send an email if the Clinician changes their status (Out -> In, In -> Out, Unsafe State -> Either)
            # Optional flag to send an alert if change in level outside 

            if history[id] != decision or different_level: 
                if decision == "IN":
                    sender.generate_return(id, curr_time, boundary_changes_times[id])
                    logger.debug(f"Client {id} has returned to their boundary")
                else:
                    sender.generate_exit(id, point, closest_point, distance, curr_time)
                    logger.debug(f"Client {id} has exited their boundary")

                history[id] = decision
                boundary_changes_times[id] = curr_time

                # Uncomment to Debug
            status = str(status).replace("'", '"')
            # print(status)
            logging.debug(status)
            
            
            distances[id] = distance

            # Persistent Storage of Most Recent Result for each Client.
            if database: 
                database.update_recent(id, decision, curr_time, status)

        # end_time = time.time()
        # print(f"The calculations and email sending took: {end_time - temp_end_time} seconds")
        # total_time = end_time - start_time
        # print(f"The total time: {total_time} seconds")

        time.sleep(INTERVAL)

    sender.mailserver.quit()
    session.close()


# executor: [process_1, process_2, process_3, send_email_1, send_email_2, send_email_3] 
# Multi-Threaded Approach

def multi_monitor_simple_loop():
    t_end = time.time() + DURATION # 1 HOUR
    session = requests.Session() # Reuse existing TCP connection
    distances = {key:0.0 for key in PHLEBOTOMISTS} # Most recent distance change
    boundary_changes_times = {key:-1 for key in PHLEBOTOMISTS} # Time of most recent status change
    history = {key:"IN" for key in PHLEBOTOMISTS} # Most Recent State (IN, OUT, UNSAFE)  - Unsafe State means API or data failed

    if REDIS_USED: 
        database = Database(REDIS_URL) # Used for most recent info
    else: 
        database = None
    
    sender = Sender(SENDER, RECEPIENT, PASSWORD, database, MULTI_THREADED)
    # Multi-Threaded
    executor = ThreadPoolExecutor(NUM_THREADS) 

    while time.time() < t_end:

        # print("Taking Track of Time")
        # start_time = time.time()
        statuses = [] 
        times = [] 

        # Multiple Threads to Process 
        results = list(executor.map(poll_status_with_time, [(session, id) for id in PHLEBOTOMISTS])) 

        for current_time, api_result in results: 
            times.append(current_time) # Time of API result
            statuses.append(api_result) # API result
            

        # temp_end_time = time.time()
        # print(f"API results took: {temp_end_time - start_time} seconds")

        for itr, (id, status) in enumerate(zip(PHLEBOTOMISTS, statuses)):
            curr_time = times[itr]
            if (status == -1): # Alert due to exception raised during GET request
                executor.submit(sender.generate_failure, id)
                # history[id] = "UNSAFE"
                continue

            pointVals, polygonVals = extract_information(status)
            if pointVals == -1: # Alert due to exception raised with the JSON returned
                executor.submit(sender.generate_failure, id)
                # history[id] = "UNSAFE" 
                continue 
            
            try: 
                polygon, point = generate_structures(pointVals, polygonVals)
            except Exception as e:
                logger.error(f"Failed to generate points or polygons for Clinician {id} data: {e}")
                executor.submit(sender.generate_failure, id) # Alert due to issue with Data itsself
                # history[id] = "UNSAFE" 
                continue
                
            
            decision, distance, closest_point = cover_information(point, polygon) # (IN / OUT, distance in miles, closest point) - (IN, 0.0, current_point) when inside

            if ALERTS_USED: # Uses the distance to send the most up-to-date warning (Low -> High)
                different_level = (decision == "OUT" and calculate_level(distance) != calculate_level(distances[id])) # Can use this for more informative email responses
            else: 
                different_level = False
            
            if decision != covers(point, polygon): 
                status = str(status).replace("'", '"')
                logger.error(f"floating point rounding error: {distance}")

            # Send an email if the Clinician changes their status (Out -> In, In -> Out, Unsafe State -> Either) or with a change in the alert status if levels are activated
            if history[id] != decision or different_level: 
                if decision == "IN":
                    executor.submit(sender.generate_return, id, curr_time, boundary_changes_times[id])
                    logger.debug(f"Client {id} has returned to their boundary")

                else:
                    executor.submit(sender.generate_exit, id, point, closest_point, distance, curr_time)
                    logger.debug(f"Client {id} has exited their boundary")

                history[id] = decision
                boundary_changes_times[id] = curr_time

                # Uncomment to Debug
                # status = str(status).replace("'", '"')
                # print(status)
            
            
            distances[id] = distance

            # Persistent Storage of Most Recent Result for each Client.
            if database: 
                database.update_recent(id, decision, curr_time, status)

        # end_time = time.time()
        # print(f"Calculation took: {end_time - temp_end_time}")
        # total_time = end_time - start_time
        # print(f"Total Time: {total_time}")
        time.sleep(120)

    sender.mailserver.quit()
    session.close()

    
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='monitor.log', encoding='utf-8', level=logging.DEBUG)
    logger.info('STARTING_MAIN_1_HOUR')

    if MULTI_THREADED: 
        multi_monitor_simple_loop()
    else:
        monitor_simple_loop()

    logging.info('END MAIN')