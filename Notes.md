
# Initial Notes:

Goal:
- Create Congressional Districts per State such that each district is geographically contiguous

- Create a high-deminsional embedding of each county capturing demographic information



- Found Data:
    - cc-est2024-alldata.csv : County-level population estimates.
        [cc-est2024-alldata](https://www.census.gov/data/datasets/time-series/demo/popest/2020s-counties-detail.html)
    - List_of_United_State_counties_and_county_equivalents : County adjacency information.
    - 

# Example JSON embeddeding
```json
{
    "STATE_N" :
    {
        "Num_Districts": 10,
        "Counties":[
            {"County_1": "embeddings"},
            {"County_N": "embeddings"}
        ],
        "adjacency_List" :
        {
            "County_1" :["County_2"],
        }
    }
}
```

# Pseudo code:
```text
used_counties = []
county_list = [List of counties in State]
Congressional_Counties = range(0,k)

Congressional_Counties[0].append(county_list.shuffle().pop())

# Instantiate Congressional Counties
for i range (1,k):
    average_embedding_of_Cong_Count = get_avg_embedding(Congressional_Counties)
    farthest_county = getMaxDistance(average_embedding_of_Cong_County, county_list)
    delete farthest_county from county_list
    Congrssional_Counties[i].append(farthest_county)

# Build Congressional Counties:
while len(county_list) != 0:
    for district in congressional_district:
        avg_cong_embeddding = get_avg_embedding(district)
        county = getMinAdjacentCounty(avg_cong_embeddding, district, adjacency_list)
        if county exists:
            district.append(county)
            delete farthest_county from county_list
```