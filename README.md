# Geolocate the phlebotomists
Image_Diagram 

### Steps to Rerun

```bash
# Step 1: Clone the repository
git clone https://github.com/rpenmatc04/geolocate.git
cd geolocate

# Step 2: Set up your environment
pip install -r requirements.txt

# Step 3: Configure environment variables
# Fill in the .env file with the appropriate values

# Step 4: Run the script
python3 main.py
```

Summary: 

Features: 

Email Content: 
    - Option to differentiate Alerts depending on distance from nearest boundary
    - Includes current location and (lattitude, longitude), as well as nearest distance to the boundary
    - Phlebotomists that return back to the boundary contain the approximated duration spent outside of the boundary 
    - Option for Failed API requests include most recent stored status in the redis cache

Logging: Maintain a Log for better management, recovery, and debugging 

Considerations made due to possible Scaling: If the number of clinicians increases to 100 - 1000

1. Async: Print Statements are the bottleneck (see Findings) and can be done via async to not block until they finish as this will be a bottleneck if we have 100-1000 
2. Database: Persistent Storage with Redis Cache for keeping most up-to-date information. Easy to switch to keeping track of all information. 
3. ThreadPoolExecutor for API requests and sending Emails

Potential Future Developments: 

Lambda + Amazon SES for sending emails at scale rather than SMTP 
Include a static map screenshot in email with directions rather than simple haversine formula distance
Threading. Spawn Multiple Threads so that each thread corresponds to a set of phlebotomists or emails and implement different monitor intervals (exponential back-off) while utilizing multi-core parallelism

Appendix 

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
