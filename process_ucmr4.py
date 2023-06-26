"""
process_ucmr4.py: This script cleans and prepares the UCMR 4 dataset based 
on user-provided inputs. A final CSV of the processed data is saved to the 
Data/Processed folder.
"""

import pandas as pd
import glob


# ---------------------------------------------------------------------------- #
#                                   CONSTANTS                                  #
# ---------------------------------------------------------------------------- #
RAW_PATH = 'Data/Raw'
PROCESSED_PATH = 'Data/Processed'
ANALYTICAL_PATHS = glob.glob(RAW_PATH + '/UCMR4_All_*.txt')

# Some UCMR 4 columns are empty, duplicative, or unecessary for our scope:
#   Size: All public water systems in this dataset are "Large" by definition
#   SamplePointName: We will identify locations by standardized ID and type
#   AssociatedFacilityID: NULL values for UCMR 4
#   AssociatedSamplePointID: NULL values for UCMR 4
#   Units: Duplicative info, units are specified in value column (all in µg/L)
#   SampleEventCode: Scope is to evaluate by sample date only
#   MonitoringRequirement: "Assessment Monitoring" for all samples by definition
#   UCMR1SampleType: NULL values for UCMR 4
TARGET_COLS = [
    'PWSID', 'PWSName', 'FacilityID', 'FacilityName', 'FacilityWaterType', 
    'SamplePointID', 'SamplePointType', 'CollectionDate', 'SampleID', 
    'Contaminant', 'MRL', 'MethodID', 'AnalyticalResultsSign', 
    'AnalyticalResultValue(µg/L)', 'Region', 'State'
    ]

PROMPTS_DICT = {
    'non-detect representation': ['0', 'half', 'mrl'],
    'spatial aggregation': ['none', 'state', 'region']
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
        [unnamed]: a string containing all list values separated by ', '
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
        response: validated user response for given prompt
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


def process_nondetects(row, assumption='half'):
    """
    Applies assumption of non-detects being zero, half of the MRL, or at the MRL
    as specified in the function call.

    Args:
        row (DataFrame): DataFrame containing a single row of data (one sample)
        assumption: how to represent non-detect results (defaults to half MRL)
    Returns:
        [unnamed]: DataFrame of revised analytical result with assumption applied
    """

    # Estimate value according to ND assumption if result is non-detect
    if row['AnalyticalResultsSign'] == '<':
        if assumption == '0':
            return 0
        if assumption == 'half':
            return row['MRL'] / 2
        if assumption == 'mrl':
            return row['MRL']
    else:
        # Otherwise return reported detection
        return row['AnalyticalResultValue(µg/L)']


def get_aggregated_df(df, agg_value):
    """
    Aggregates analytical results according to user selection (State or EPA 
    Region) and returns the min, average, and max for each contaminant.

    Args:
        df (DataFrame): analytical results after applying ND value assumption
        agg_value (string): aggregate by 'State' or 'Region'
    Returns:
        agg_df (DataFrame): aggregated analytical results
    """
    agg_df = pd.DataFrame()

    agg_df['Min (µg/L)'] = df.groupby([agg_value, 'Contaminant']
                                      )['Processed Result (µg/L)'].min()
    agg_df['Average (µg/L)'] = df.groupby([agg_value, 'Contaminant']
                                          )['Processed Result (µg/L)'].mean()
    agg_df['Max (µg/L)'] = df.groupby([agg_value, 'Contaminant']
                                      )['Processed Result (µg/L)'].max()
    
    agg_df.reset_index(drop=False, inplace=True)
    
    return agg_df


# ---------------------------------------------------------------------------- #
#                                 PROCESS DATA                                 #
# ---------------------------------------------------------------------------- #
analytical_dfs = []
user_decisions = {}

print('Reading in dataset ...\n')

for path in ANALYTICAL_PATHS:
    analytical_dfs.append(pd.read_csv(path, usecols=TARGET_COLS,
                                      sep='\t', lineterminator='\r'))

analytical_df = pd.concat(analytical_dfs, ignore_index=True)

# Clean Data
analytical_df['PWSID'] = analytical_df['PWSID'].str.strip()
analytical_df.sort_values(by=['PWSID'])

# Some Tribal PWSs are represented with an EPA Region Code for their state. 
# For the sake of demonstration, we are interested in grouping these together
# under a new "Tribal PWS" state.
analytical_df['State'] = analytical_df.State.str.replace(
    r'[0-9]+', 'Tribal PWS', regex=True
    )

# Prompt user for decisions about how to prepare dataset
for prompt in PROMPTS_DICT:
    formatted_request = f'Select {prompt} ({format_list(PROMPTS_DICT[prompt])}): '
    
    user_decisions[prompt] = get_response(
        formatted_request,      # Request to show to user
        PROMPTS_DICT[prompt]    # List of allowable options
        )

print(
    '\nData is being processed using the following methods:\n',
    user_decisions
    )

# Handle non-detects (some cleanup could be done here with sig figs)
nd_value = user_decisions['non-detect representation']

analytical_df['Processed Result (µg/L)'] = analytical_df.apply(
    lambda row: process_nondetects(row, nd_value),
    axis=1
    )

# Aggregate and get basic statistics (min, average, max), if requested
# These calculations are building on assumptions about the value of ND results
agg_value = user_decisions['spatial aggregation']

if agg_value != 'none':
    analytical_df = get_aggregated_df(analytical_df, agg_value.capitalize())

# Save final processed CSV
filename = f'UCMR4_NDs-as-{nd_value}_Agg-by-{agg_value}'
analytical_df.to_csv(PROCESSED_PATH + '/' + filename, index=False)
print(f'\nFile saved at {PROCESSED_PATH} as {filename}')
