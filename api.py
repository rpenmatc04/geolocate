from config import API_URL
import time

import logging 
logger = logging.getLogger(__name__)

# Make single end-point API call
def poll_status(session, id): 
    url = f"{API_URL}/{id}"
    try: 
        response = session.get(url) 
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API failed to respond correctly for Clinician {id}: {e}")
        return -1 

# Threading Example
def poll_status_with_time(args): 
    session, id = args
    start = time.time() 
    status = poll_status(session, id)
    return start, status

# Extract the current location from the json output 
def extract_point(status): 
    try: 
        point = status["features"][0]["geometry"]["coordinates"]
        return point
    except Exception as e:
        logger.error(f"Failed to extract required point information: {e}")
        return -1

# Convert the JSON output to point coordinates, polygon coordinates: return [point], [[polygon_1], [polygon_2]]
def extract_information(status): 
    try: 
        point = status["features"][0]["geometry"]["coordinates"]
        polygon = status["features"][1]["geometry"]["coordinates"]
        for count in range(2, len(status["features"])): 
            polygon.extend(status["features"][count]["geometry"]["coordinates"])
    except Exception as e:
        logger.error(f"Failed to extract required point or polygon information: {e}, {status}")
        return -1, -1


    return point, polygon

# Async Polling
async def async_poll(session, id): 
    url = f"{API_URL}/{id}"
    try: 
        async with session.get(url) as response:
            response.raise_for_status() 
            return id, await response.json()
    except Exception as e:
        logger.error(f"API failed to respond correctly for Clinician {id}: {e}")
        return -1, -1 
