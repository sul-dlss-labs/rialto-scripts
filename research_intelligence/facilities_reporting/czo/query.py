import dimcli, itertools, json, requests, sys
import pandas as pd
from datetime import datetime
from dimcli.utils import *
from requests.auth import AuthBase
# Need to add to the path to import config
sys.path.insert(1, '../../../')
import config

input = pd.read_csv('data/award_numbers_input.csv', header=0)

terms = ['Critical Zone Observatory']

# Get Dimesnions publications
# connect to the database
dimcli.login(config.username, config.password, config.endpoint)
dsl = dimcli.Dsl()

csv_fields = ["title", "authors", "dimensions_id", "doi", "doi_url", "publisher", "journal", "volume", "issue", "pages", "pub_year", "concepts", "concepts_scores", "category_bra", "category_for", "provenance", "query_term", "pub_harvested_date"]
dimensions = pd.DataFrame(columns=csv_fields)

def get_for_categories(category_object):
    if isinstance(category_object, type(None)):
        return 'None'
    else:
        return [d['name'] for d in category_object]

categories_of_interest = ['04 Earth Sciences', '05 Environmental Sciences', '06 Biological Sciences', '12 Built Environment and Design']
CATEGORY = '04 Earth Sciences'
subject_area_q = f""" where category_for.name="{CATEGORY}" """

# Get publicaitons with and filter out those from outside categories
for count, i in enumerate(terms, start=1):

    query = dsl.query(f"""
         search publications
           for "\\"{i}\\""
           where category_for.name in ["04 Earth Sciences", "05 Environmental Sciences", "06 Biological Sciences", "12 Built Environment and Design"]
         return publications[all]
         limit 30""")

    skip = 1000
    iterations = 19

    # Get publications by search term

    for pub in query['publications']:
        print(pub)
