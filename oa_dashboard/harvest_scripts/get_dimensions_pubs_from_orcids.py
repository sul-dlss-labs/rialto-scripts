import csv, dimcli, json, math, sys
import pandas as pd
from datetime import datetime
# Need to add to the path to import config
sys.path.insert(1, '../../../')
import config

# Helper functions
def get_author_names(object):
    if isinstance(object, type(None)):
        pass
    else:
        names = ""
        for i in object:
            names += f"{i.get('last_name')}, {i.get('first_name')}; "
        return names[:-2]


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


def get_sub_fields_from_list(l, sub_field):
  if isinstance(l, type(None)):
        pass
  else:
    OUTPUT_CSV = []
    for i in l:
      OUTPUT_CSV.append(i.get(sub_field))

    return OUTPUT_CSV

def construct_query(orcid):
    print(orcid)
    return dsl.query("""search publications where researchers.orcid_id = \"{}\"
                    return publications [title + authors + id + doi + pmid + pmcid + arxiv_id + type + date + concepts + publisher + journal + volume + issue + year + funder_countries + funders + funding_section + open_access + research_orgs + supporting_grant_ids + category_for + category_bra]
                    limit 1000""".format(orcid))

# connect to the database
dimcli.login(config.username, config.password, config.endpoint)
dsl = dimcli.Dsl()

INPUT = pd.read_csv('../input/stanford_researcher_ids.csv')
SUNET_ORCID_DICT = pd.Series(INPUT.orcid.values,index=INPUT.sunet).to_dict()
OUTPUT_CSV = 'output/dimensions_pubs_from_orcids.csv'
OUTPUT_JSONL = 'output/dimensions_pubs_from_orcids.jsonl'
CSV_FIELDS = ["sunet", "title", "authors", "dimensions_id", "doi", "doi_url", "pmid", "pmcid", "arxiv_id", "type", "date", "concepts", "publisher", "journal", "volume", "issue", "pub_year", "funder_countries", "funders", "funding_section", "open_access", "research_orgs", "supporting_grant_ids", "category_for", "category_bra"]

with open(OUTPUT_CSV, 'a') as f:
    writer = csv.writer(f)
    writer.writerow(CSV_FIELDS)

    for count, (sunet, orcid) in enumerate(SUNET_ORCID_DICT.items(), start=1):
        print(f'Harvesting {count} of {len(SUNET_ORCID_DICT)}.')

        query = construct_query(orcid)

        for pub in query['publications']:
            with open(OUTPUT_JSONL, 'a') as the_file:
                the_file.write(f'{pub}\n')
            new_row = [sunet, pub['title'], get_author_names(pub.get('authors')), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('pmid'), pub.get('pmcid'), pub.get('arxiv_id'), pub.get('type'), pub.get('date'), pub.get('concepts'), pub.get('publisher'), get_sub_field(pub.get('journal'), 'title'), pub.get('volume'), pub.get('issue'), pub.get('year'), get_sub_fields_from_list(pub.get('funder_countries'), 'name'), pub.get('funders'), pub.get('funding_section'), pub.get('open_access'), pub.get('research_orgs'), pub.get('supporting_grant_ids'), get_sub_fields_from_list(pub.get('category_for'), 'name'), get_sub_fields_from_list(pub.get('category_bra'), 'name')]
            with open(OUTPUT_CSV, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(new_row)
