import csv, dimcli, json, math, pandas, sys
from datetime import datetime
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

# connect to the database
dimcli.login(config.username, config.password, config.endpoint)
dsl = dimcli.Dsl()

# input = pandas.read_csv('CZOpubs_scrape.csv', header=0)
input = pandas.read_csv('data/final_2021.csv', header=0)

csv_fields = ["title", "acknowledgments", "authors", "dimensions_id", "doi", "doi_url", "publisher", "journal", "volume", "issue", "pages", "pub_year", "concepts", "concepts_scores", "category_bra", "category_for", "provenance", "query_term", "pub_harvested_date"]
with open(r'data/2021_final_full.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(csv_fields)

string_list = '['
for i in input['doi'].tolist():
    print(i)
    string_list+=f'"{i}", '
string_list=string_list[:-2]
string_list+=']'
string_list=string_list.replace('\n', '')

query = dsl.query(f"""search publications where doi in {string_list}
                    return publications [title + acknowledgements + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for]
                    limit 1000""")

for pub in query['publications']:
    new_row = [pub['title'], pub.get('acknowledgements'), get_author_names(pub.get('authors')), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('publisher'), get_sub_field(pub.get('journal'), 'title'), pub.get('volume'), pub.get('issue'), pub.get('pages'), pub.get('year'), pub.get('concepts'), pub.get('concepts_scores'), pub.get('category_bra'), get_for_categories(pub.get('category_for')), 'dimensions', i, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
    with open(r'data/2021_final_full.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(new_row)
