## Inspiration
As students who go to the University of Cincinnati and have lived in Ohio for our whole lives, we are very tied to Ohio and its politics.  Something that has been in the news recently has been Ohio's redistricting efforts(along with other efforts across the country).  Seeing these political redistricting efforts is what inspired us to create this project to remove the political effort and instead create districts by grouping similar demographics to create a more representative map.

## What it does
This project creates new congressional district maps for most states in the United States.  These maps are designed to cluster similar counties together, with the idea that similar counties will have similar interests in their representatives, so ultimately, more people will have a representative who matches their wishes.  

## How we built it
There are three main sections of how we built this project: Data Preparation, District Construction Algorithm, and District Visualization.

### Data Preparation:
The first step of this project was to acquire and prepare the data.  We utilized US census [data](https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/totals/co-est2024-alldata.csv), containing demographic information by county from 2020-2024.  After loading this data into a Pandas DataFrame, we made a copy of the total population information to be used later, then normalized all the data on a per-state basis.  Once we had all the features normalized, we created a 74-dimensional embedding space to embed vectors representing each of the counties, which will be used in the next section to calculate the similarity between counties.

We also utilized this [dataset](https://www.census.gov/geographies/reference-files/time-series/geo/county-adjacency.html) to identify which counties are adjacent to each other.  This data is very important because congressional districts must be continuous, so counties in them must be adjacent to each other.  To prep this data, we first split the columns to separate the county name from its state, then we removed any adjacency connections between counties in different states.  This is because congressional districts cannot cross state lines.  After this, we created an adjacency list dictionary with entries for each county, and then saved that dictionary as a JSON file to be used later.

### District Construction Algorithm
The next step of the project was the actual algorithm to construct the districts.  <COREY FILL IN>

### District Visualization
The final part of the project was to visualize our new maps.  We achieved this by utilizing Tableau's mapping functionality.  We started with a shapefile, which can be found [here](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html), containing the geospatial data for every US county.  Once we loaded this data into Tableau, we joined the county data with our new congressional districts, which allowed us to easily visualize the districts using Tableau's built-in mapping support. 

## Challenges we ran into
Throughout this project, the number one issue that we ran into was simply finding good data that was easy to work with.  We had originally intended to use a wider range of attributes in our embedding space, including economic and education data.  We had found datasets for these metrics at a county level provided by the USDA [here](https://www.ers.usda.gov/data-products/county-level-data-sets/county-level-data-sets-download-data).  However, there were a number of inconsistencies between these datasets themselves and with the population metric dataset from the Census Bureau.  We had spent multiple hours attempting to sanitize this data so that it could all be joined together, but ultimately, we decided that it was a better use of our time to focus on the actual algorithm and visualization over spending more time cleaning data. 

We also ran into the issue of not being able to split counties into two districts in our visualization.  Because we use a predefined shapefile for the counties, visualizing split counties would require editing the shapefile every time we generate a set of districts, which is not feasible in a hackathon time frame, but could be a good extension of the project for the future.

## Accomplishments that we're proud of
We are both very proud that our algorithm worked and that it worked well.  It was something that we had devised ourselves, no pre-planning, no use of AI, so seeing it work to generate districts was very rewarding.  It especially felt good to see the visualization and look at our generated district map for Ohio, then compare it against the actual congressional map and see that our map was relatively similar to what is actually in use.  You can also view our congressional district map [here](https://public.tableau.com/views/USCongressionalRepresentativeRedistrictingMap/RepresentativeRedistriction?:language=en-US&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link).

## What we learned
Throughout this project, we gained a wide variety of experience and knowledge.  We got lots of first-hand experience in searching through and then cleaning messy data, along with a refresher on working with data using Pandas.  We also furthered our knowledge on embedding spaces, which is something that had been covered in classes, but we had never had hands-on experience with.  Another important item that we learned was the importance of planning your program ahead and creating pseudocode before implementation.  This was something that we implemented in our project timeline that was EXTREMELY beneficial to us.  Finally, we got more experience in data visualizations and Tableau.

## What's next for Representative Redistricting
There are several clear areas of improvement for this project.  The first one is expanding the dataset and embedding space.  Adding more forms of data, such as economic, family, or education data, could lead to a more accurate similarity metric and better districts.  We also see future use for this project as a way to evaluate current district maps against our impartial maps, as a way to evaluate the bias of a given congressional district map.

