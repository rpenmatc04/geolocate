from config import API_URL
import time

import logging 
logger = logging.getLogger(__name__)

def poll_status(session, id): # Make API call
    url = f"{API_URL}/{id}"
    try: 
        response = session.get(url) 
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API failed to respond correctly for Clinician {id}: {e}")
        return -1 

def poll_status_with_time(parameters): # API call used in Threading Example
    session, id = parameters
    start = time.time() 
    status = poll_status(session, id)
    return start, status

def extract_point(status): # Convert JSON output from API result to point
    try: 
        point = status["features"][0]["geometry"]["coordinates"]
        return point
    except Exception as e:
        logger.error(f"Failed to extract required point information: {e}")
        return -1

def extract_information(status): # Convert the JSON output to point coordinates, polygon coordinates ([point], [[polygon_1], [polygon_2]])
    try: 
        point = status["features"][0]["geometry"]["coordinates"]
        polygon = status["features"][1]["geometry"]["coordinates"]
        for count in range(2, len(status["features"])): 
            polygon.extend(status["features"][count]["geometry"]["coordinates"])
    except Exception as e:
        logger.error(f"Failed to extract required point or polygon information: {e}")
        return -1, -1


    return point, polygon

