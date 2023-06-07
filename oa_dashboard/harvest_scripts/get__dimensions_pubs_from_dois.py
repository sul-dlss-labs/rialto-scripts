import csv, dimcli, json, math, sys
import pandas as pd
from datetime import datetime
# Need to add to the path to import config
sys.path.insert(1, '../../')
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


def stringify_list(l):
  stringified_list = '['
  for i in l:
    i = str(i).replace('https://doi.org/', '')
    stringified_list+=f'"{i}", '
  stringified_list=stringified_list[:-2] # remove the final comma and space
  stringified_list+=']'
  return stringified_list.replace('\n', '')

def construct_query(chunk_of_dois):
    return dsl.query(f"""search publications where doi in {chunk_of_dois}
                    return publications [title + authors + id + doi + pmid + pmcid + arxiv_id + type + date + concepts + publisher + journal + volume + issue + year + funder_countries + funders + funding_section + open_access + research_orgs + supporting_grant_ids + category_for + category_bra]
                    limit 1000""")

# connect to the database
dimcli.login(config.username, config.password, config.endpoint)
dsl = dimcli.Dsl()

CHUNK_SIZE = 400
INPUT = pd.read_csv('/Users/jtim/Dropbox/DLSS/rialto/research-intelligence/reports/oa_2023/input/orcid/orcid_sul_pub_publication_report_sulpub_dois.csv', header=0)
OUTPUT_CSV = 'output/orcid_pubs_from_dois.csv'
OUTPUT_JSONL = 'output/orcid_pubs_from_dois.jsonl'
CSV_FIELDS = ["sunet", "title", "authors", "dimensions_id", "doi", "doi_url", "pmid", "pmcid", "arxiv_id", "type", "date", "concepts", "publisher", "journal", "volume", "issue", "pub_year", "funder_countries", "funders", "funding_section", "open_access", "research_orgs", "supporting_grant_ids", "category_for", "category_bra"]

with open(OUTPUT_CSV, 'a') as f:
    writer = csv.writer(f)
    writer.writerow(CSV_FIELDS)

# chunks = int(math.floor(len(INPUT)/CHUNK_SIZE))
# remainder = len(INPUT) % CHUNK_SIZE

# Harvest chunks
# for i in range(chunks-1):
    # end_index = CHUNK_SIZE + (i*CHUNK_SIZE)
    # start_index = i*CHUNK_SIZE
    # print(f'Harvesting chunk {i+1} of {chunks+1} range [{start_index}:{end_index}]')
sunets = list(set(INPUT.sunetid.to_list()))[4518:]
for count, sunet in enumerate(sunets, start=4518):
    print(f'Harvesting {count} of {len(sunets)+4518}.')

    chunk_of_dois = stringify_list(INPUT[INPUT.sunetid == sunet].doi)

    query = construct_query(chunk_of_dois)

    for pub in query['publications']:
        with open(OUTPUT_JSONL, 'a') as the_file:
            the_file.write(f'{pub}\n')
        new_row = [sunet, pub['title'], get_author_names(pub.get('authors')), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('pmid'), pub.get('pmcid'), pub.get('arxiv_id'), pub.get('type'), pub.get('date'), pub.get('concepts'), pub.get('publisher'), get_sub_field(pub.get('journal'), 'title'), pub.get('volume'), pub.get('issue'), pub.get('year'), get_sub_fields_from_list(pub.get('funder_countries'), 'name'), pub.get('funders'), pub.get('funding_section'), pub.get('open_access'), pub.get('research_orgs'), pub.get('supporting_grant_ids'), get_sub_fields_from_list(pub.get('category_for'), 'name'), get_sub_fields_from_list(pub.get('category_bra'), 'name')]
        with open(OUTPUT_CSV, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(new_row)


# Harvest remainder
# end_index = remainder + ((chunks-1)*CHUNK_SIZE)
# start_index = (chunks-1)*CHUNK_SIZE
# print(f'Harvesting chunk {chunks} of {chunks+1} range [{start_index}:{end_index}]')
# query = construct_query(chunk_of_dois)
#
# for pub in query['publications']:
#     new_row = [pub['title'], get_author_names(pub.get('authors')), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('pmid'), pub.get('pmcid'), pub.get('arxiv_id'), pub.get('type'), pub.get('date'), pub.get('concepts'), pub.get('publisher'), get_sub_field(pub.get('journal'), 'title'), pub.get('volume'), pub.get('issue'), pub.get('year'), get_sub_fields_from_list(pub.get('funder_countries'), 'name'), get_sub_fields_from_list(pub.get('funders'), 'name'), pub.get('funding_section'), pub.get('open_access'), get_sub_fields_from_list(pub.get('research_orgs'), 'name'), pub.get('supporting_grant_ids'), get_sub_fields_from_list(pub.get('category_for'), 'name'), get_sub_fields_from_list(pub.get('category_bra'), 'name')]
#     with open(OUTPUT_CSV, 'a') as f:
#         writer = csv.writer(f)
#         writer.writerow(new_row)
