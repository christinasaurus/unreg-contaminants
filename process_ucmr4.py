"""
process_ucmr4.py: This script cleans and prepares the UCMR 4 dataset based 
on user-provided inputs:
    - Representation of non-detect results (0, half MRL, at MRL)
    - Spatial aggregation (none, by state, by EPA region)
    - Temporal aggregation (none, by month, by year)

A final CSV of the processed data is saved to a user-specified location.
"""

import pandas as pd
import glob


# ---------------------------------------------------------------------------- #
#                                   CONSTANTS                                  #
# ---------------------------------------------------------------------------- #
RELATIVE_PATH = r'Data\Raw'
ANALYTICAL_PATHS = glob.glob(RELATIVE_PATH + '/UCMR4_All_*.txt')
ZIPCODE_PATH = RELATIVE_PATH + '/UCMR4_ZipCodes.txt'

# Define the UCMR 4 columns we want to keep
# Excluded columns are generally empty, duplicative, or unecessary for our scope:
#   Size: All systems in this dataset are "Large" by definition
#   SamplePointName: Identify sample locations by standardized ID and type only
#   AssociatedFacilityID: NULL values for UCMR 4
#   AssociatedSamplePointID: NULL values for UCMR 4
#   Units: Duplicative info -- units are specified in value column (all in ug/L)
#   SampleEventCode: Scope is to evaluate by sample date only
#   MonitoringRequirement: Assessment Monitoring for all samples by definition
#   UCMR1SampleType: NULL values for UCMR 4
TARGET_COLS = [
    'PWSID', 'PWSName', 'FacilityID', 'FacilityName', 'FacilityWaterType', 
    'SamplePointID', 'SamplePointType', 'CollectionDate', 'SampleID', 
    'Contaminant', 'MRL', 'MethodID', 'AnalyticalResultsSign', 
    'AnalyticalResultValue(µg/L)', 'Region', 'State'
    ]

PROMPTS_DICT = {
    'non-detect representation': ['0', 'half', 'mdl'],
    'spatial aggregation': ['none', 'state', 'region'],
    'temporal aggregation': ['none', 'monthly', 'annual']
}


# ---------------------------------------------------------------------------- #
#                                   FUNCTIONS                                  #
# ---------------------------------------------------------------------------- #
def format_list(l):
    """
    Formats a list into a string with list values separated by a comma and space.
    E.g.: ['hi', 'hello'] --> 'hi, hello'

    Args:
        l (list): a list of values (non-string values will be converted)
    Returns:
        formatted_string: a string containing all list values separated by ', '
    """

    return ', '.join(map(str, l))


def get_response(prompt, accepted_responses):
    """
    Gets user input. If an invalid response is provided, continues prompting
    user for valid response.

    Args:
        prompt: text to display to user to request response
        accepted_responses: list of acceptable user responses
    Returns:
        result: validated user response for given prompt
    """

    while True:
        response = input(prompt).lower()
        try:
            accepted_responses.index(response)
        except:
            print('Unexpected value. Please enter a value from the prompt.')
            continue
        break
    
    return response


# ---------------------------------------------------------------------------- #
#                                 PROCESS DATA                                 #
# ---------------------------------------------------------------------------- #

# --------------------------------- Get Data --------------------------------- #
analytical_dfs = []

for path in ANALYTICAL_PATHS:
    analytical_dfs.append(pd.read_csv(path, usecols=TARGET_COLS,
                                      sep='\t', lineterminator='\r'))

analytical_df = pd.concat(analytical_dfs, ignore_index=True)

# -------------------------------- Clean Data -------------------------------- #
analytical_df.PWSID = analytical_df.PWSID.str.strip()

# Some Tribal PWSs are represented with an EPA Region Code for their state. 
# For the sake of demonstration, we are interested in grouping these together
# under a new "Tribal PWS" State.
analytical_df.State = analytical_df.State.str.replace(
    r'[0-9]+', 'Tribal PWS', regex=True
    )

# ---------------------------- Get User Decisions ---------------------------- #
user_decisions = {}
for prompt in PROMPTS_DICT:
    formatted_request = f'Select {prompt} ({format_list(PROMPTS_DICT[prompt])}):'
    user_decisions[prompt] = get_response(
        formatted_request,      # Request to print for user
        PROMPTS_DICT[prompt]    # List of user-selectable options
        )

print(
    '\nData will be processed using the following methods:\n',
    user_decisions
    )

