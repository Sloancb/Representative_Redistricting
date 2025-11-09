import pandas as pd
import json

# Omit Hawaii & Connecticut
state_abbreviations = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", 
    "CA": "California", "CO": "Colorado", 
    # "CT": "Connecticut", 
    "DE": "Delaware", 
    "FL": "Florida", "GA": "Georgia", 
    # "HI": "Hawaii", 
    "ID": "Idaho", 
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", 
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", 
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", 
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", 
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", 
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", 
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", 
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", 
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", 
    "WI": "Wisconsin", "WY": "Wyoming"
}

def clean_data():
    """
    Cleans and processes population data from a CSV file.

    This function performs the following operations:
    1. Reads population data from 'cc-est2024-alldata.csv'
    2. Filters data for a specific year (YEAR=6) and age group (AGEGRP=0)
    3. Removes data for District of Columbia, Hawaii, and Connecticut
    4. Drops unnecessary columns and renames remaining columns
    5. Saves the cleaned data to 'cleaned_population.csv'
    
    Side Effects:
    - Creates or overwrites '../clean_data/cleaned_population.csv' 
        with cleaned population data
    
    Returns:
        None\n
    """
    pop_df = pd.read_csv('../data/cc-est2024-alldata.csv', encoding='latin1')

    # Clean Year and Age Data:
    pop_df = pop_df[(pop_df['YEAR'] == 6) & (pop_df['AGEGRP'] == 0)]

    # Omit the following Data:
    # District of Columbia, Connecticut, and Hawaii
    pattern = '|'.join(['District of Columbia', "Hawaii", "Connecticut"])
    pop_df = pop_df[~(pop_df['STNAME'].str.contains(pattern, regex=True))].reset_index(drop=True)

    # Drop extra data columns
    pop_df = pop_df.drop(['SUMLEV', 'YEAR','AGEGRP','STATE','COUNTY'], axis=1)
    pop_df = pop_df.rename(columns={'STNAME':'STATE', 'CTYNAME':'COUNTY'})

    # Additional Data to be added to the embedding space. 
    # Unable to due to data mismatches on County naming convetions

    # sippy_df = pd.read_csv('./data/SippyMergedData-2.csv')
    # print(f"Sippy Dirty Shape:{sippy_df.shape}")
    # states = [
    #     "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    #     "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    #     "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    #     "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    #     "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    #     "New Hampshire", "New Jersey", "New Mexico", "New York",
    #     "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    #     "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    #     "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    #     "West Virginia", "Wisconsin", "Wyoming", "United States"
    # ]
    # pattern = '|'.join(states)
    # sippy_df = sippy_df[
    #     ~(
    #         (sippy_df["Area_Name"].str.contains(pattern, regex=True) ) & 
    #         ~(sippy_df["Area_Name"].str.endswith("County") ) &
    #         ~(sippy_df["Area_Name"].str.endswith("Parish") ) &
    #         ~(sippy_df["Area_Name"].str.endswith("Islands") )&
    #         ~(sippy_df["Area_Name"].str.endswith("city") )
    #     )]

    # print(f"Sippy Clean Shape:{sippy_df.shape}")
    # sippy_df.to_csv('./clean_data/economic_stats_2.csv', index=False)

    # counties = pd.read_csv("data/List_of_United_States_counties_and_county_equivalents_1.csv")
    # print(f"Counties:{counties.shape}")
    # county_list = counties["County"].to_list()

    pop_df.to_csv('../clean_data/cleaned_population.csv', index=False)

    countyAdjacency = pd.read_csv('../data/CountyAdjacencyFile.txt', delimiter='|')

    countyAdjacency[['County Name', 'State']] = countyAdjacency['County Name'].str.split(', ', expand=True)
    countyAdjacency[['Neighbor Name', 'Neighbor State']] = countyAdjacency['Neighbor Name'].str.split(', ', expand=True)

    countyAdjacency = countyAdjacency[['County Name', 'State', 'Neighbor Name', 'Neighbor State']]

    # Remove neighbors that are not in the same state
    countyAdjacency = countyAdjacency[countyAdjacency['State'] == countyAdjacency['Neighbor State']]

    # Create adjacency list dictionary
    adjacency_dict = {}
    for _, row in countyAdjacency.iterrows():
        county = f"{row['County Name']}, {row['State']}"
        neighbor = f"{row['Neighbor Name']}, {row['Neighbor State']}"
        if county not in adjacency_dict:
            adjacency_dict[county] = []
        adjacency_dict[county].append(neighbor)

    # Save adjacency dictionary to a file
    with open('../clean_data/county_adjacency.json', 'w') as f:
        json.dump(adjacency_dict, f, indent=4)


    
def create_embeddings(output_file_name="embeddings"):
    """
    Creates embeddings from congressional data and saves them to a JSON file.
    This function processes multiple data sources to create a comprehensive embedding structure:
    1. County adjacency data from a JSON file
    2. US Districts by State data from a CSV file
    3. Population data from a cleaned CSV file
    The resulting data structure contains:
    - Adjacency lists for counties within each state
    - Number of congressional districts per state
    - Normalized county demographic data
    - County population data
    Parameters:
    ----------
    output_file_name : str, optional
        The name of the output JSON file (default is "embeddings")
        File will be saved as "{output_file_name}.json"
    Returns:
    -------
    None
        Saves the processed data to a JSON file in the ../embeddings/ directory
    """
    data = {}
    adj_list = {}
    with open('../clean_data/county_adjacency.json', 'r', encoding='latin1') as file:
        adj_list = json.load(file)
    for abbreviation, state_name in state_abbreviations.items():
        for county_name in adj_list.keys():
            if abbreviation in county_name:
                if state_name not in data.keys():
                    data[state_name] = {"adjacency_list":{}}
                clean_counties = []
                for county in adj_list[county_name]:
                    clean_counties.append(county.split(",")[0])
                data[state_name]["adjacency_list"][county_name.split(",")[0]] = clean_counties

    df = pd.read_csv('../clean_data/US_Districts_by_State.csv', encoding='latin1')
    for num_district_by_state in df.values:
        if num_district_by_state[0] not in state_abbreviations:
            continue
        state_name = state_abbreviations[num_district_by_state[0]]
        data[state_name]["Num_Districts"] = num_district_by_state[1]

    df = pd.read_csv('../clean_data/cleaned_population.csv', encoding='latin1')
    states = list(df['STATE'].unique())
    for state in states:
        state_data = {}
        counties_df = df[df['STATE'] == state]
        county_data = counties_df.drop(["STATE", "COUNTY"], axis=1)
        county_embeddings = county_data.apply(lambda x: (x / x.max()), axis=0)

        county_data = pd.concat([counties_df["COUNTY"], county_embeddings], axis=1)
        for _, county_embedding in county_data.iterrows():
            state_data[str(county_embedding[0])] = list(county_embedding.values[1:])
        data[state]["County_Data"] = state_data
        
    for state in states:
        state_data = {}
        counties_df = df[df['STATE'] == state]
        county_data = counties_df[["COUNTY", "TOT_POP"]]
        for _, county_embedding in county_data.iterrows():
            state_data[str(county_embedding[0])] = int(county_embedding.values[1])
        data[state]["County_Population"] = state_data

    with open(f"../embeddings/{output_file_name}.json", 'w', encoding='latin1') as json_file:
        json.dump(data, json_file, indent=4)