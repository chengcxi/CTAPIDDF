#CTAPIDDF v0.1
#Using Python 3.13.1 (2024-12-04), ClinicalTrials.gov REST API 2.0.3 (2024-12-20), Pandas 2.2.3 (2024-09-20), Requests 2.32.3 (2024-05-29)

#Credit to Bench Vue for the original code!
#Modified last by Cheng Xi, 9:55PM 12/25/2024

#Changelog:
#v0.1- Updated code & fixed minor errors regarding using lists as parameters, improved search accuracy, added location & status filters.

#TODO:
#Filter sponsors                                    //PRIORITY
#Filter trial types
#Prettify output                                    //OPTIONAL
#Make sheets & excel friendly
#Find sponsor company(ies)
#Optimize code
#Better formatting                                  //OPTIONAL
#Google/Yahoo finance integration
#Port to CPP or JS                                  //OPTIONAL
#GUI                                                //OPTIONAL
#More accurate results                              //IN-PROGRESS

import requests
import pandas as pd

url = "https://clinicaltrials.gov/api/v2/studies"
params = { #https://clinicaltrials.gov/api/oas/v2 <- Check here for list of usable parameters
    "query.titles": "COVID OR SARS", 
    "query.locn": "United States OR Germany OR France OR Denmark OR Norway OR Sweden", #Add more countries
    "filter.overallStatus": "RECRUITING,NOT_YET_RECRUITING,ENROLLING_BY_INVITATION,ACTIVE_NOT_RECRUITING,AVAILABLE,TEMPORARILY_NOT_AVAILABLE",
    #Figure out sponsors, etc.
    "pageSize": 100
}

# Initialize an empty list to store the data
dataList = []

# Loop until there is no nextPageToken
while True:
    # Print the current URL (for debugging purposes)
    print("Fetching data from:", url + '?' + '&'.join([f"{k}={v}" for k, v in params.items()]))
    
    # Send a GET request to the API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()  # Parse JSON response
        studies = data.get('studies', [])  # Extract the list of studies

        # Loop through each study and extract specific information
        for study in studies:
            # Safely access nested keys
            nctId = study['protocolSection']['identificationModule'].get('nctId', 'Unknown')
            overallStatus = study['protocolSection']['statusModule'].get('overallStatus', 'Unknown')
            startDate = study['protocolSection']['statusModule'].get('startDateStruct', {}).get('date', 'Unknown Date')
            conditions = ', '.join(study['protocolSection']['conditionsModule'].get('conditions', ['No conditions listed']))
            acronym = study['protocolSection']['identificationModule'].get('acronym', 'Unknown')

            # Extract interventions safely
            interventions_list = study['protocolSection'].get('armsInterventionsModule', {}).get('interventions', [])
            interventions = ', '.join([intervention.get('name', 'No intervention name listed') for intervention in interventions_list]) if interventions_list else "No interventions listed"
            
            # Extract locations safely
            locations_list = study['protocolSection'].get('contactsLocationsModule', {}).get('locations', [])
            locations = ', '.join([f"{location.get('city', 'No City')} - {location.get('country', 'No Country')}" for location in locations_list]) if locations_list else "No locations listed"
            
            # Extract dates and phases
            primaryCompletionDate = study['protocolSection']['statusModule'].get('primaryCompletionDateStruct', {}).get('date', 'Unknown Date')
            studyFirstPostDate = study['protocolSection']['statusModule'].get('studyFirstPostDateStruct', {}).get('date', 'Unknown Date')
            lastUpdatePostDate = study['protocolSection']['statusModule'].get('lastUpdatePostDateStruct', {}).get('date', 'Unknown Date')
            studyType = study['protocolSection']['designModule'].get('studyType', 'Unknown')
            phases = ', '.join(study['protocolSection']['designModule'].get('phases', ['Not Available']))

            # Append the data to the list as a dictionary
            dataList.append({
                "NCT ID": nctId,
                "Acronym": acronym,
                "Overall Status": overallStatus,
                "Start Date": startDate,
                "Conditions": conditions,
                "Interventions": interventions,
                "Locations": locations,
                "Primary Completion Date": primaryCompletionDate,
                "Study First Post Date": studyFirstPostDate,
                "Last Update Post Date": lastUpdatePostDate,
                "Study Type": studyType,
                "Phases": phases
            })

        # Check for nextPageToken and update the params or break the loop
        nextPageToken = data.get('nextPageToken')
        if nextPageToken:
            params['pageToken'] = nextPageToken  # Set the pageToken for the next request
        else:
            break  # Exit the loop if no nextPageToken is present
    else:
        print("Failed to fetch data. Status code:", response.status_code)
        break

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(dataList)

# Print the DataFrame
print(df)

# Optionally, save the DataFrame to a CSV file
df.to_csv("trials.csv", index=True)