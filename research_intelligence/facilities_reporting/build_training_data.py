import csv, dimcli, itertools, json, requests, sys
import os.path
from argparse import ArgumentParser
import numpy as np
import pandas as pd
from datetime import datetime
from dimcli.utils import *
from requests.auth import AuthBase
# Need to add to the path to import config
sys.path.insert(1, '../../../')
import config

def get_for_categories(category_object):
    '''Extracts category_for name from object when present, else replace NoneType with None string.'''
    if isinstance(category_object, type(None)):
        return 'None'
    else:
        return [d['name'] for d in category_object]

def write_example(out, field_one, field_two):
    '''Writes label and features for one training instance .'''
    out.write('__label__{} {}\n'.format(field_one, str(field_two).replace("['", "'").replace("']", "'").replace(", ", " ")))

def training_data_from_df(df, out_file):
    '''Takes dataframe and writes label and features to text file in fastText format.'''
    df['concepts'].replace('', np.nan, inplace=True)
    df.dropna(subset=['concepts'], inplace=True)
    with open(f'{args.o}/train.txt', 'w') as train:
        df.apply(lambda row : write_example(train, row['label'], row['concepts']), axis=1)

CATEGORIES = ["07 AGRICULTURAL AND VETERINARY SCIENCES", "12 BUILT ENVIRONMENT AND DESIGN",
              "13 EDUCATION", "14 ECONOMICS", "15 COMMERCE, MANAGEMENT, TOURISM AND SERVICES",
              "16 STUDIES IN HUMAN SOCIETY", "18 LAW AND LEGAL STUDIES", "19 STUDIES IN CREATIVE ARTS AND WRITING",
              "20 LANGUAGE, COMMUNICATION AND CULTURE", "21 HISTORY AND ARCHAEOLOGY",
              "22 PHILOSOPHY AND RELIGIOUS STUDIES"]

def main():
    if len(sys.argv) < 4:
        # Get Dimesnions publications
        # connect to the database
        dimcli.login(config.username, config.password, config.endpoint)
        dsl = dimcli.Dsl()

        OUT_PATH = f'{args.o}/not_relevant_publication.csv'
        assert os.path.isfile(OUT_PATH) == False, 'Not-relevant file already exists. Remove it or load it.'

        # Grab the first 1000 publications per category and assign not_relevant to them
        CSV_FIELDS = ["label", "title", "authors", "dimensions_id", "doi", "doi_url", "publisher", "journal", "volume", "issue", "pages", "pub_year", "concepts", "concepts_scores", "category_bra", "category_for", "provenance", "pub_harvested_date"]
        not_relevant = pd.DataFrame(columns=CSV_FIELDS)
        not_relevant.to_csv(OUT_PATH, mode='a')

        for category in CATEGORIES:
            query = dsl.query(f"""
                 search publications
                   where category_for.name = \"{category}"
                 return publications [title + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for]
                 limit 1000""")

            for pub in query['publications']:
                try:
                    new_row = ['non-relevant', pub['title'], pub.get('authors'), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('publisher'), pub.get('journal'), pub.get('volume'), pub.get('issue'), pub.get('pages'), pub.get('year'), pub.get('concepts'), pub.get('concepts_scores'), pub.get('category_bra'), get_for_categories(pub.get('category_for')), 'dimensions', datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
                    new_row_series = pd.Series(new_row, index = not_relevant.columns)
                    not_relevant = not_relevant.append(new_row_series, ignore_index=True)
                    new_row_df = pd.DataFrame(new_row_series).T
                    new_row_df.to_csv(OUT_PATH, mode='a', header=False)
                except:
                    print("Unexpected error:", sys.exc_info()[0])

            not_relevant_from_csv = pd.read_csv(OUT_PATH, header=0)
            print(f'Finished category: {category}. {not_relevant_from_csv.shape[0]} records in dataframe.\n')

        assert not_relevant.shape[0] == not_relevant_from_csv.shape[0], 'Wrong number of records in dataframe.'
        assert len(CSV_FIELDS) == not_relevant.shape[1], 'CSV out file has different number of columns than expected.'

    else:
        # Load the non-relevant publicaitons
        assert os.path.isfile(args.n)
        not_relevant = pd.read_csv(f'{args.n}', header=0)
        print(f'READ DF: {not_relevant.shape[0]} records in dataframe.\n')
        not_relevant['label'] = 'not-relevant'

    print(f'ADD LABEL: {not_relevant.shape[0]} records in dataframe.\n')
    # assert len(CATEGORIES) * 1000 == not_relevant.shape[0], 'CSV out file has different number of rows than expected.'

    # Load the relevant publicaitons
    relevant = pd.read_csv(f'{args.r}')
    relevant['label'] = 'relevant'

    # Drop all unneeded columns
    relevant.drop(relevant.columns.difference(['doi','label','concepts']), 1, inplace=True)
    not_relevant.drop(not_relevant.columns.difference(['doi','label','concepts']), 1, inplace=True)
    print(f'DROP COL: {not_relevant.shape[0]} records in dataframe.\n')
    assert not_relevant.shape[1] == relevant.shape[1], 'Not-relevant dataframe and relevant dataframe have different number of columns.'

    # Remove rows with no data in concepts
    not_relevant['concepts'].replace('', np.nan, inplace=True)
    print(f'REPLACE CONCEPTS: {not_relevant.shape[0]} records in dataframe.\n')

    not_relevant.dropna(subset=['concepts'], inplace=True)
    print(f'DROP NA: {not_relevant.shape[0]} records in dataframe.\n')

    relevant['concepts'].replace('', np.nan, inplace=True)
    relevant.dropna(subset=['concepts'], inplace=True)

    # Combine and drop duplicates
    full_training = pd.concat([relevant, not_relevant])
    assert relevant.shape[0] + not_relevant.shape[0] == full_training.shape[0], 'Dataframes did not concatenate properly.'
    full_training.drop_duplicates(subset=['doi'], keep='first', inplace=True)
    print(f"{relevant.shape[0] + not_relevant.shape[0] - full_training.shape[0]} duplicates removed.")
    # assert full_training[full_training.label == 'relevant'].shape[0] == relevant.shape[0], 'Some relevant examples were dropped by mistake.'
    print(f"There are {full_training[full_training.label == 'relevant'].shape[0]} relevant examples remaining in the training set.")

    # Randomize examples
    training_data_random = full_training.sample(n=full_training.shape[0])

    # Export training data to text files
    training_data_from_df(training_data_random, 'data/train/train.txt')

if __name__ == "__main__":
    # CLI client options.
    parser = ArgumentParser()
    parser.add_argument(
        "r",
        help="What is the path to the relevant publicaitons?")
    parser.add_argument(
        "o",
        nargs="?",
        help="What is the output directory you want to save the non-relevant publicaitons to?")
    parser.add_argument(
        "n",
        nargs="?",
        help="What is the path to the non-relevant publicaitons?")
    args = parser.parse_args()
    main()
