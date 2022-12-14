import csv, dimcli, itertools, json, math, requests, sys
import pandas as pd
from datetime import datetime
from dimcli.utils import *
from requests.auth import AuthBase
# Need to add to the path to import config
sys.path.insert(1, '../../../')
import config

# Helper functions
def get_for_categories(category_object):
    if isinstance(category_object, type(None)):
        return 'None'
    else:
        return [d['name'] for d in category_object]

def get_sub_field(object, sub_field):
    if isinstance(object, type(None)):
        pass
    else:
        return object.get(sub_field)

def get_author_names(object):
    if isinstance(object, type(None)):
        pass
    else:
        names = ""
        for i in object:
            names += f"{i.get('last_name')}, {i.get('first_name')}; "
        return names[:-2]

# Constants
YEAR_START = 2021
YEAR_END = 2021

# Search terms: put terms with high precision first, followed by terms with lower
# precision so that when duplicates are removed the publications with high precision terms
# written to the csv file will be preserved. This will make it easier to manually confirm
# relevance.
search_terms = ['ECCS-2026822', 'ECCS-1542152', 'Stanford Nanofabrication Facility', 'Stanford Nano Shared Facilities']

all_terms = list(itertools.chain(search_terms))

# Get Dimesnions publications
# connect to the database
dimcli.login(config.username, config.password, config.endpoint)
dsl = dimcli.Dsl()

csv_fields = ["title", "acknowledgements", "authors", "dimensions_id", "doi", "doi_url", "publisher", "journal", "volume", "issue", "pages", "pub_year", "concepts", "concepts_scores", "category_bra", "category_for", "provenance", "query_term", "pub_harvested_date"]
with open(r'data/search_results_2021.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(csv_fields)

for count, i in enumerate(all_terms, start=1):
    skip = 0

    query = dsl.query(f"""
         search publications
           for "\\"{i}\\""
         where year in [{YEAR_START}:{YEAR_END}]
         return publications [title + acknowledgements + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for]
         limit 1000 skip {skip}""")

    iterations = math.ceil(query.stats['total_count']/1000)
    while iterations > 0:
        query = dsl.query(f"""
             search publications
               for "\\"{i}\\""
             where year in [{YEAR_START}:{YEAR_END}]
             return publications [title + acknowledgements + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for]
             limit 1000 skip {skip}""")

        for pub in query['publications']:
            try:
                new_row = [pub['title'], pub.get('acknowledgements'), get_author_names(pub.get('authors')), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('publisher'), get_sub_field(pub.get('journal'), 'title'), pub.get('volume'), pub.get('issue'), pub.get('pages'), pub.get('year'), pub.get('concepts'), pub.get('concepts_scores'), pub.get('category_bra'), get_for_categories(pub.get('category_for')), 'dimensions', i, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
                with open(r'data/search_results_2021.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(new_row)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

        skip += 1000
        iterations -= 1

        print('------Finished next page of term {} of {}: {}.'.format(count, len(list(itertools.chain(search_terms))), i))

    print('Finished term {} of {}: {}.'.format(count, len(list(itertools.chain(search_terms))), i))
    print('\n')
