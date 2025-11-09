import prep_congressional_data
import map_congressional_data
import random

def main():
    random.seed(10)
    print('Cleaning data...')
    prep_congressional_data.clean_data()
    print('Creating Embeddings...')
    prep_congressional_data.create_embeddings("embeddings")
    print('Building Congressional Maps...')
    map_congressional_data.build_congressional_districts()
    # map_congressional_data.build_congressional_districts(timelape=True, embeddings_file_name="embeddings", specfic_state_map="Ohio")
    print("Done building! Check output directory")

if __name__ == "__main__":
    main()