# Geolocate the phlebotomists

Image_Diagram 

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

Consideration for Scaling: 

If the number of clinicians it can be improved via Threading and Asynchronous Operations 

1. Threading: Spawn Multiple Threads so that each thread corresponds to a set or an individual phlebotomists and can implement different monitor intervals based on status
2. Async: Print Statements can be done via async to not block until they finish as this will be a bottleneck if we have 100-1000 

#Appendix 

Justification for Monitoring Interval Length:

2-minute monitor interval implies an expected warning within 1 minute.

Through experimentation, I encountered a failure from the get request once in ~300 iterations. For the sake of generalization, let's assume that the error from the API occurs about once every 100-1000 times. We know that there are 525600 (60 min / hour * 24 hour / day * 365 day / year) minutes in a year, and assuming that these vans run for 12 hours a day we have 525600 * 1/5 * 1/2  = 52560 5-minute intervals. Considering the failure rate as 1/100 or 1/1000 if we run every five minutes we have between ~50-500 intervals resulting in non-responses. Thus, the monitor interval rate should be lower and with a monitor interval rate of 2 minutes the expected amount of wait for the first poll is a minute later and we have another one guaranteed before the five-minute restriction ends. Thus, we now have a failure rate as (1/100)^2 or (1/1000)^2 assuming independent which massively reduces the number of failures to between ~0-5. Finally, this is a good choice because it does not overload the API too much. 

Findings: 

Without Async: 

The average time for making a GET request for the Clinician is ~0.05 - 0.1 seconds
The average time for all geospatial calculations and decisions is ~0.001 seconds

The average time for converting (lattitude, longitude) to address is 0.1-0.3 seconds [Optional]
The average time spent sending an email is ~1 second (sending an email is the bottleneck)

The average best case scenario (no emails sent) for six clinicians ~0.4-0.5 seconds
The average worst case scenario (all emails sent) for six clinicians ~6 - 7 seconds

With Async: 

The average best case scenario (no emails sent) for six clinicians ~0.4-0.5 seconds
The average worst case scenario (all emails sent) for six clinicians ~[Tested] seconds
