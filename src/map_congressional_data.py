import pandas
import json
import random
import pandas as pd
import numpy as np
from scipy.spatial import distance
from pprint import pprint
import os

global countiesByState
countiesByState = pd.DataFrame([], columns=['STNAME','CTYNAME','CDID'])
global current_state
global state_congression_county_list
global save_states
save_states = 1

def getMaxDisimilarity(county_embedding, county_list, embeddings):
    """
    Find the county with the maximum dissimilarity to the given county based on cosine distance.

    Args:
        county_embedding (numpy.ndarray): The embedding vector for the reference county
        county_list (list): List of county names to compare against
        embeddings (dict): Dictionary mapping county names to their embedding vectors

    Returns:
        str: Name of the county with maximum cosine distance from the reference county
    """
    max_distance = -1
    furthest_county = ""
    for other_county in county_list:
        other_county_embedding = embeddings[other_county]
        dist = distance.cosine(county_embedding, other_county_embedding)
        if dist > max_distance:
            furthest_county = other_county
    return furthest_county

def getMaxSimilarity(county_embedding, county_list, embeddings):
    """
    Get the county with the maximum similarity to a given county embedding.

    Parameters:
        county_embedding (list or array): The embedding vector of the target county.
        county_list (list): A list of county names to compare against.
        embeddings (dict): A dictionary mapping county names to their corresponding embedding vectors.

    Returns:
        str: The name of the closest county based on cosine distance, or an empty string if no county is found within the max distance.
    """
    max_distance = 2
    closet_county = ""
    for other_county in county_list:
        other_county_embedding = embeddings[other_county]
        dist = distance.cosine(county_embedding, other_county_embedding)
        if dist < max_distance:
            closet_county = other_county
    return closet_county

def getSmallestCongressionalCountyIndex(Congressional_Counties):
    sorted_list = sorted(Congressional_Counties)
    index = Congressional_Counties.index(sorted(Congressional_Counties)[0])
    return index

def getAdjacencyList(county_list, adjacency_list, current_county_list):
    """
    Generate a new adjacency list of counties that are adjacent to the counties
    in the provided county_list and are also present in the current_county_list.

    Parameters:
    county_list (list): A list of counties for which to find adjacent counties.
    adjacency_list (dict): A dictionary where keys are counties and values are lists
                           of adjacent counties.
    current_county_list (list): A list of counties that are currently considered.

    Returns:
    list: A list of counties that are adjacent to the counties in county_list
          and are also present in current_county_list.
    """
    new_adjacency_list = []
    for county in county_list:
        for potential_county in adjacency_list[county]:
            if (potential_county not in new_adjacency_list and potential_county in current_county_list):
                new_adjacency_list.append(potential_county)
    return new_adjacency_list

def exportCongressional_Counties(Congressional_Counties, timelape):
    """
    Exports congressional county data to a CSV file.
    This function processes a list of congressional counties, extracts relevant
    information, and saves it to a CSV file. The function uses global variables
    to track the current state and the number of states processed. It also
    removes specific suffixes from county names to standardize the naming
    convention.
    Parameters:
        Congressional_Counties (list): A list of tuples, where each tuple contains
        the congressional district ID and a list of counties associated with that
        district.
        timelape (bool): A boolean to determine if the congressional districts should be saved
        individually or all at once
    Global Variables:
        countiesByState (DataFrame): A pandas DataFrame that holds the processed
        county data.
        save_states (int): A counter for the number of states processed.
        current_state (str): The name of the current state being processed.
    Output:
        A CSV file named 'Districts_<save_states>.txt' is created in the
        '../output' directory, containing the state name, county name, and
        congressional district ID.
    """
    # Get current global states
    global countiesByState
    global save_states
    global current_state

    data = []
    for i, congressional_county in enumerate(Congressional_Counties):
        for county in congressional_county[1]:
            data.append([current_state,county,i])
    if timelape:
        countiesByState = pd.DataFrame(data, columns=['STNAME','CTYNAME','CDID'])
    else:
        new_counties = pd.DataFrame(data, columns=['STNAME','CTYNAME','CDID'])
        countiesByState = pd.concat([new_counties, countiesByState])
    # Remove " County" from CTYNAME
    countiesByState['CTYNAME'] = countiesByState['CTYNAME'].str.replace(' County', '', regex=False)
    countiesByState['CTYNAME'] = countiesByState['CTYNAME'].str.replace(' Parish', '', regex=False)
    countiesByState['CTYNAME'] = countiesByState['CTYNAME'].str.replace(' city', '', regex=False)
    countiesByState['CTYNAME'] = countiesByState['CTYNAME'].str.replace(' Island', '', regex=False)
    countiesByState['CTYNAME'] = countiesByState['CTYNAME'].str.replace(' Census Area', '', regex=False)
    countiesByState['CTYNAME'] = countiesByState['CTYNAME'].str.replace(' Borough', '', regex=False)
    
    os.makedirs("../output", exist_ok=True)
    if timelape:
        countiesByState.to_csv(f'../output/Districts_{save_states}.txt', index=False)
        save_states += 1
    else:
        countiesByState.to_csv(f'../output/US_Congressional_Districts.txt', index=False)

def build_congressional_districts( timelape=False, embeddings_file_name="embeddings", specfic_state_map=None):
    """
    Builds congressional districts for one or more U.S. states using county-level embeddings,
    adjacency lists, and population data loaded from a JSON file.
    This function implements a seeded, greedy clustering process that attempts to form
    Num_Districts groups of counties per state such that:
    - Each group (district) grows by repeatedly adding adjacent counties whose county
        embedding best matches the district's current average embedding (similarity-based
        agglomeration).
    - Initial seeds are chosen by randomly shuffling counties and selecting a seed
        for each district using a max-dissimilarity heuristic so initial seeds are spread
        in embedding space.
    Behavior / side effects
    - Reads embeddings and state data from ../embeddings/{embeddings_file_name}.json
        using latin1 encoding. The JSON is expected to map state names to a dict containing
        at least these keys: "adjacency_list", "County_Data", "County_Population", "Num_Districts".
        - adjacency_list: mapping county_id -> list of adjacent county_ids
        - County_Data: mapping county_id -> embedding (array-like)
        - County_Population: mapping county_id -> integer population
        - Num_Districts: integer number of districts to build for that state
    - Optionally exports intermediate and final districtings by calling
        exportCongressional_Counties(...) when timelape is True (or at the end).
    - Raises a warning if the number of counties in adjacency lists and
        embeddings differ for any state.
    Parameters
    - timelape (bool, default=False):
            If True, exportCongressional_Counties(...) is invoked at each intermediate step
            so an animation/timelapse of district growth can be produced. If False, only the
            final districting is exported at the end.
    - embeddings_file_name (str, default="embeddings"):
            Base filename (without .json) to load from the ../embeddings/ directory.
            Example: embeddings_file_name="embeddings_v2" reads "../embeddings/embeddings_v2.json".
    - specfic_state_map (str or None, default=None):
            If provided, only the specified state key from the JSON is processed; otherwise
            all states in the file are processed.
    Returns
    - None
    Exceptions / failure modes
    - FileNotFoundError if the embeddings JSON cannot be found at the expected path.
    - json.JSONDecodeError if the JSON file is malformed.
    - KeyError / TypeError if the expected keys or data shapes are not present in the JSON
        (e.g., missing "adjacency_list" or non-dict County_Data).
    - The algorithm assumes embeddings are numeric array-like objects compatible with numpy
        operations (np.mean) and that population_by_county entries are numeric.
    """
    Congressional_Data = {}
    embeddings = {}

    with open(f'../embeddings/{embeddings_file_name}.json', 'r', encoding='latin1') as file:
        Congressional_Data = json.load(file)

    # Validate counties match for both embeddings and adjacency lists
    for state in Congressional_Data.keys():
        adjacency_list = Congressional_Data[state]["adjacency_list"]
        embeddings = Congressional_Data[state]["County_Data"]
        if len(adjacency_list.keys()) != len(embeddings.keys()):
            print(f"{state} is bad!")
            print( len(adjacency_list.keys()), len(embeddings.keys()))
            raise Warning("Data is Inconsistent!")

    state_congression_county_list = {}
    for state in Congressional_Data.keys():
        global current_state
        if specfic_state_map != None and state != specfic_state_map:
                continue
        current_state = state
        state_data = Congressional_Data[state]
        adjacency_list = state_data["adjacency_list"]
        embeddings = state_data["County_Data"]
        population_by_county = state_data["County_Population"]
        Num_Counties = state_data['Num_Districts']

        county_list = list(adjacency_list.keys())
        random.shuffle(county_list)
        Congressional_Counties = []
        for i in range (0, Num_Counties):
            Congressional_Counties.append([0,[]])
        first_county = county_list.pop()
        Congressional_Counties[0][0] += population_by_county[first_county]
        Congressional_Counties[0][1].append(first_county)
        if(timelape):
            exportCongressional_Counties(Congressional_Counties, timelape)
        
        avg_county_embedding = embeddings[first_county]
        for i in range(1, Num_Counties):
            county = getMaxDisimilarity(avg_county_embedding, county_list, embeddings)
            county_list.remove(county)
            Congressional_Counties[i][0] += population_by_county[county]
            Congressional_Counties[i][1].append(county)
            if(timelape):
                exportCongressional_Counties(Congressional_Counties, timelape)
            avg_county_embedding = np.mean(np.array([avg_county_embedding, embeddings[county]]), axis=0)

        while len(county_list) != 0:
            county_index = getSmallestCongressionalCountyIndex(Congressional_Counties)
            current_counties = Congressional_Counties[county_index][1]
            current_embeddings = []
            for get_county in current_counties:
                current_embeddings.append(embeddings[get_county])
            average_congressional_county = np.mean(np.array(current_embeddings), axis=0)
            # Search through adjacecy list;
            new_adjacency_list = getAdjacencyList(current_counties, adjacency_list, county_list)
            # If nothing is adjacent, the county is landlocked and cannot have any other counties
            if len(new_adjacency_list) == 0:
                Congressional_Counties[county_index][0] = np.inf
                continue
            county = getMaxSimilarity(average_congressional_county, new_adjacency_list, embeddings)
            county_list.remove(county)
            Congressional_Counties[county_index][0] += population_by_county[county]
            Congressional_Counties[county_index][1].append(county)
            if(timelape):
                exportCongressional_Counties(Congressional_Counties, timelape)

        exportCongressional_Counties(Congressional_Counties, timelape)
