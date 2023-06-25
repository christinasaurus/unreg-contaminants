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


# GET ANALYTICAL DATA
analytical_dfs = []

# Glob is used for demonstration, but it is most useful when there are many 
# files to combine (in this case, there are only two)
for path in ANALYTICAL_PATHS:
    analytical_dfs.append(pd.read_csv(path, usecols=TARGET_COLS,
                                      sep='\t', lineterminator='\r'))

analytical_df = pd.concat(analytical_dfs, ignore_index=True)

# CLEAN DATA
analytical_df.PWSID = analytical_df.PWSID.str.strip()

# Some Tribal public water systems were assigned to EPA Region Codes (01-10), 
# but for the sake of demonstration we are interested in grouping this data
# across geographies. We will leave the Navajo Nation (NN) state as-is.
analytical_df.State = analytical_df.State.str.replace(
    r'[0-9]+', 'Tribal PWS', regex=True
    )

print(analytical_df.head(3))