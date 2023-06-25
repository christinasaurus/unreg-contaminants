# Unregulated Contaminant Monitoring Rule Analysis

## Purpose
This repo contains a brief analysis of the US EPA's Unregulated Contaminant Monitoring Rule (UCMR) 4 dataset. It is intended as a generalized work sample only and should not be used for decision-making.

## About the Dataset
UCMR 4 contains drinking water analytical results for contaminants that were unregulated by the Safe Drinking Water Act at the time of sample collection. UCMR 4 samples were collected from large public water systems serving more than 10,000 people across the United States between 2018 and 2020. The data is publicly available from the [US EPA](https://www.epa.gov/dwucmr/occurrence-data-unregulated-contaminant-monitoring-rule#4) and unzipped copies are available in the __Data/Raw__ folder of this repo. Due to GitHub file size limitations, the Occurrence Data By State version of the dataset was used (where the data is split across two files). Further details about the dataset and definitions for each field are provided in the [UCMR 4 Data Summary](https://www.epa.gov/sites/default/files/2018-10/documents/ucmr4-data-summary.pdf).

## Frequently Used Analysis Techniques
My goal is to demonstrate many of the steps I often take during a typical data analysis project, even if they do not make perfect sense for the UCMR 4 dataset. These techniques include:
- Handling and manipulating files that are too big to inspect with Excel
- Concatenating (appending rows) and merging (appending columns)
- Validating user inputs or values
- Data cleaning and selecting appropriate data types (although this dataset was cleaner than most to begin with)
- Value mapping (like changing IDs to human-friendly names) and data transformations (like representing non-detect results as half of the detection limit instead of U-flags)
- Filtering rows and columns
- Temporal and spatial aggregation with basic summary statistics
- Modularizing code (creating functions) for ease of readability, maintainability, and reusability
- Separating and preserving raw vs processed data

I also plan to add examples of the following to this repo in the near future:
- Handling NULL and blank values (need to find another messier public dataset)
- Normalizing data (compared to background levels or cleanup criteria, for example)
- Querying other relevant data from a SQL database or API (this will likely be [US Census population data](https://www.census.gov/data/developers/data-sets/popest-popproj/popest.html)) and executing a spatial join
- Creating a Power BI dashboard of analytical results
- (And doing some edge case testing and debugging, if needed, because this was created quickly!)