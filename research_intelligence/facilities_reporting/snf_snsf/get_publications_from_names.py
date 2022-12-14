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

# get organization ids for organizations associated with Stanford University
# returns a json object
def get_grids_by_name(name):
    grids = []
    name_query = dsl.query("""search organizations where name~"\\"{}\\"" return organizations[id]""".format(name)).data
    for org in name_query['organizations']:
        grids.append(org.get('id'))
    return json.dumps(grids)

# Constants
YEAR_START = 2021
YEAR_END = 2021

snf = pd.read_csv('data/sul-pub_pubs.csv', header=0)
snf['full_names'] = snf[['pub_associated_author_last_name', 'pub_associated_author_first_name']].apply(lambda x: ', '.join(x[x.notnull()]), axis = 1)
snf_users = list(set(snf['full_names'].tolist()))

snsf = pd.read_csv('data/snsf_names.csv', header=0)
snsf['full_names'] = snsf[['last_name', 'first_name']].apply(lambda x: ', '.join(x[x.notnull()]), axis = 1)
snsf_users = list(set(snsf['full_names'].tolist()))

all_users = list(itertools.chain(snf_users, snsf_users))

# Get Dimesnions publications
# connect to the database
dimcli.login(config.username, config.password, config.endpoint)
dsl = dimcli.Dsl()

stanford_grids = get_grids_by_name('Stanford')

csv_fields = ["title", "acknowledgements", "authors", "dimensions_id", "doi", "doi_url", "publisher", "journal", "volume", "issue", "pages", "pub_year", "concepts", "concepts_scores", "category_bra", "category_for", "provenance", "query_term", "pub_harvested_date"]
with open(r'data/name_search_results_2021.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(csv_fields)

for count, i in enumerate(all_users, start=1):

    query = dsl.query(f"""
         search publications
         in authors for "\\"{i}\\""
         where research_orgs.id in {stanford_grids}
         and year in [{YEAR_START}:{YEAR_END}]
         return publications [title + acknowledgements + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for]
         limit 1000""")


    for pub in query['publications']:
        try:
            new_row = [pub['title'], pub.get('acknowledgements'), get_author_names(pub.get('authors')), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('publisher'), get_sub_field(pub.get('journal'), 'title'), pub.get('volume'), pub.get('issue'), pub.get('pages'), pub.get('year'), pub.get('concepts'), pub.get('concepts_scores'), pub.get('category_bra'), get_for_categories(pub.get('category_for')), 'dimensions', i, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
            with open(r'data/name_search_results_2021.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(new_row)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    print('------Finished term {} of {}: {}.'.format(count, len(list(itertools.chain(all_users))), i))
