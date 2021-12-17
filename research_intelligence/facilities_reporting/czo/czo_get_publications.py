import csv, dimcli, itertools, json, requests, sys
import pandas as pd
from datetime import datetime
from dimcli.utils import *
from requests.auth import AuthBase
# Need to add to the path to import config
sys.path.insert(1, '../../../')
import config

input = pd.read_csv('data/award_numbers_input.csv', header=0)

# Search terms: put terms with high precision first, followed by terms with lower
# precision so that when duplicates are removed the publications with high precision terms
# written to the csv file will be preserved. This will make it easier to manually confirm
# relevance.
search_terms = ['Critical Zone Observatory', 'CZO']
awards = input['AwardNumber']
category_filter_terms = ['Boulder Creek', 'Santa Catalina Mountains', 'Jemez River Basin', 'Christina River Basin', 'Eel River', 'Intensively Managed Landscapes', 'Luquillo', 'Reynolds Creek', 'Susquehanna Shale Hills', 'Southern Sierra', 'Calhoun']

all_terms = list(itertools.chain(search_terms, awards, category_filter_terms))

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

# for count, i in enumerate(all_terms, start=1):
#
#     skip = 1000
#     iterations = 4
#
#     # Get publications by search term
#     query = dsl.query("""search publications in full_data for "\\"{}\\"" return publications [title + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for] limit 1000""".format(i))
#     for pub in query['publications']:
#         try:
#             new_row = [pub['title'], pub.get('authors'), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('publisher'), pub.get('journal'), pub.get('volume'), pub.get('issue'), pub.get('pages'), pub.get('year'), pub.get('concepts'), pub.get('concepts_scores'), pub.get('category_bra'), get_for_categories(pub.get('category_for')), 'dimensions', i, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
#             new_row_series = pd.Series(new_row, index = dimensions.columns)
#             dimensions = dimensions.append(new_row_series, ignore_index=True)
#         except:
#             print("Unexpected error:", sys.exc_info()[0])
#             raise
#     try:
#         if query.stats['total_count'] > 1000:
#             while iterations > 0:
#                 query = dsl.query("""search publications in full_data for "\\"{}\\"" return publications [title + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for] limit 1000 skip {} """.format(i, int(skip)))
#
#                 for pub in query['publications']:
#                     try:
#                         new_row = [pub['title'], pub.get('authors'), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('publisher'), pub.get('journal'), pub.get('volume'), pub.get('issue'), pub.get('pages'), pub.get('year'), pub.get('concepts'), pub.get('concepts_scores'), pub.get('category_bra'), get_for_categories(pub.get('category_for')), 'dimensions', i, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
#                         new_row_series = pd.Series(new_row, index = dimensions.columns)
#                         dimensions = dimensions.append(new_row_series, ignore_index=True)
#                     except:
#                         print("Unexpected error:", sys.exc_info()[0])
#                         raise
#
#                 skip += 1000
#                 iterations -= 1
#
#                 print('------Finished next page of term {} of {}: {}.'.format(count, len(list(itertools.chain(awards, search_terms))), i))
#     except:
#         pass
#
#     print('Finished term {} of {}: {}.'.format(count, len(list(itertools.chain(awards, search_terms))), i))
#     print('\n')
#
# dimensions.to_csv('data/search_results_without_categories.csv', index=False)

# Get publicaitons with and filter out those from outside categories
with open(r'data/search_results_with_categories.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(csv_fields)

for count, i in enumerate(all_terms, start=1):

    skip = 1000
    iterations = 21

    # Get publications by search term
    query = dsl.query(f"""
         search publications
           for "\\"{i}\\""
         return publications [title + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for]
         limit 1000""")

    # query = dsl.query("""search publications in full_data for "\\"{}\\"" where category_for.name=04 return publications [title + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for.name] limit 1000""".format(i, category))
    for pub in query['publications']:
        try:
            new_row = [pub['title'], pub.get('authors'), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('publisher'), pub.get('journal'), pub.get('volume'), pub.get('issue'), pub.get('pages'), pub.get('year'), pub.get('concepts'), pub.get('concepts_scores'), pub.get('category_bra'), get_for_categories(pub.get('category_for')), 'dimensions', i, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
            with open(r'data/search_results_with_categories.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(new_row)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
    try:
        if query.stats['total_count'] > 1000:
            while iterations > 0:
                query = dsl.query(f"""
                     search publications
                       for "\\"{i}\\""
                     return publications [title + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for]
                     limit 1000 skip {skip}""")
                # query = dsl.query("""search publications in full_data for "\\"{}\\"" where category_for.name in {} return publications [title + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for] limit 1000""".format(i, categories_of_interest))

                for pub in query['publications']:
                    try:
                        new_row = [pub['title'], pub.get('authors'), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('publisher'), pub.get('journal'), pub.get('volume'), pub.get('issue'), pub.get('pages'), pub.get('year'), pub.get('concepts'), pub.get('concepts_scores'), pub.get('category_bra'), get_for_categories(pub.get('category_for')), 'dimensions', i, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
                        with open(r'data/search_results_with_categories.csv', 'a') as f:
                            writer = csv.writer(f)
                            writer.writerow(new_row)
                    except:
                        print("Unexpected error:", sys.exc_info()[0])
                        raise

                skip += 1000
                iterations -= 1

                print('------Finished next page of term {} of {}: {}.'.format(count, len(list(itertools.chain(awards, search_terms))), i))
    except:
        pass

    print('Finished term {} of {}: {}.'.format(count, len(list(itertools.chain(awards, search_terms))), i))
    print('\n')

for count, i in enumerate(category_filter_terms, start=1):
    skip = 1000
    iterations = 21

    # Get publications by search term
    query = dsl.query(f"""
         search publications
           for "\\"{i}\\""
           where category_for.name in ["04 Earth Sciences", "05 Environmental Sciences", "06 Biological Sciences", "12 Built Environment and Design"]
         return publications [title + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for]
         limit 1000""")

    # query = dsl.query("""search publications in full_data for "\\"{}\\"" where category_for.name=04 return publications [title + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for.name] limit 1000""".format(i, category))
    for pub in query['publications']:
        try:
            new_row = [pub['title'], pub.get('authors'), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('publisher'), pub.get('journal'), pub.get('volume'), pub.get('issue'), pub.get('pages'), pub.get('year'), pub.get('concepts'), pub.get('concepts_scores'), pub.get('category_bra'), get_for_categories(pub.get('category_for')), 'dimensions', i, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
            with open(r'data/search_results_with_categories.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(new_row)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
    try:
        if query.stats['total_count'] > 1000:
            while iterations > 0:
                query = dsl.query(f"""
                     search publications
                       for "\\"{i}\\""
                       where category_for.name in ["04 Earth Sciences", "05 Environmental Sciences", "06 Biological Sciences", "12 Built Environment and Design"]
                     return publications [title + authors + id + doi + publisher + journal + volume + issue + pages + year + concepts + concepts_scores + category_bra + category_for]
                     limit 1000 skip {skip}""")

                for pub in query['publications']:
                    try:
                        new_row = [pub['title'], pub.get('authors'), pub['id'], pub.get('doi'), "https://doi.org/{}".format(pub.get('doi')), pub.get('publisher'), pub.get('journal'), pub.get('volume'), pub.get('issue'), pub.get('pages'), pub.get('year'), pub.get('concepts'), pub.get('concepts_scores'), pub.get('category_bra'), get_for_categories(pub.get('category_for')), 'dimensions', i, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
                        with open(r'data/search_results_with_categories.csv', 'a') as f:
                            writer = csv.writer(f)
                            writer.writerow(new_row)
                    except:
                        print("Unexpected error:", sys.exc_info()[0])
                        raise

                skip += 1000
                iterations -= 1

                print('------Finished next page of term {} of {}: {}.'.format(count, len(category_filter_terms), i))
    except:
        pass

    print('Finished term {} of {}: {}.'.format(count, len(category_filter_terms), i))
    print('\n')
