# Geolocate the phlebotomists

### Steps to Rerun

```bash
# Step 1: Clone the repository
git clone https://github.com/rpenmatc04/geolocate.git
cd geolocate

# Step 2: Set up your environment
pip install -r requirements.txt

# Step 3: Configure
# Fill in the .env file with the appropriate values (see env.example)

# Step 4: Run the script
python3 main.py
``` 

### Summary

This code deals with keeping track of multiple clinicians' current status and sending updates if they leave their corresponding boundary, when they return, and when the API fails. Additionally, this code can the send different levels of alerts depending on the distance (configurable), send the current human readabale location by reverse-location from their lattitude, longitude coordinates, and on failures display the most recent information. 

### Scaling Considerations: 

If the number of clinicians massively increase or the calculations become more complex it can be improved via Threading and Asynchronous Operations:

1. For threading, set the MULTI_THREADED flag to true. There will be NUM_THREAD worker threads that will run API get requests and send emails.
2. Async: Print and API polling can be done via async + await operations to not block the thread while waiting for response or sending emails.

Note: While I have implemented threading and functions/classes for async polling and sending emails, the current code does not utilize these features due to the small scale leading to no major improvements (6 endpoints).  

### Findings: 

The average time for making a GET request for the Clinician is 50-100ms. The average time for all geospatial calculations and decisions is 1 ms

The average time for converting (lattitude, longitude) to address is 100-300ms [Optional]. The average time spent sending an email is ~1000ms (sending an email is the bottleneck)

The average best case scenario (no emails sent) for six clinicians ~400-500ms. The average worst case scenario for seven clinicians is ~6000-7000ms, which easily meets current requirements.  

With Threading (3): 

The average best case scenario (no emails sent) for six clinicians ~200ms. The average worst case scenario for seven clinicians is ~3000ms, which easily meets current requirements.  

### Appendix 

Justification for Monitoring Interval Length (assuming endpoint is valid):

2-minute monitor interval implies an expected warning within 1 minute.

Through experimentation, I encountered a failure from the get request once in ~300 iterations. For the sake of generalization, let's assume that the error from the API occurs about once every 100-1000 times. We know that there are 525600 (60 min / hour * 24 hour / day * 365 day / year) minutes in a year, and assuming that these vans run for 12 hours a day we have 525600 * 1/5 * 1/2  = 52560 5-minute intervals. Considering the failure rate as 1/100 or 1/1000 if we run once every five minutes we have between ~50-500 intervals resulting in non-responses. Thus, the monitor interval rate should be lower and with a monitor interval rate of 2 minutes the expected amount of wait for the first poll is a minute later and we have another one guaranteed before the five-minute restriction ends (since processing for all is sub 10 seconds). Thus, we now have a failure rate as (1/100)^2 or (1/1000)^2 assuming independent reduces the number of failures to between ~0-5. 

This assumes that the errors are not persistent (that the endpoint is still valid)