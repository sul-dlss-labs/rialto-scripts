import pickle
import pandas as pd
import json

# Read in csv data
combined_contributions = pd.read_csv('input/dimensions/final/combined_contributions.csv')
dimensions_contributions = pd.read_csv('input/dimensions/final/dimensions_pubs_from_orcids_final.csv')
dimensions_publications = dimensions_contributions.drop_duplicates(subset='doi')
openalex_dimensions_contributions = pd.read_csv('input/dimensions/final/openalex_pubs_from_dois_final.csv')
openalex_dimensions_publications = openalex_dimensions_contributions.drop_duplicates(subset='doi')
orcid_dimensions_contributions = pd.read_csv('input/dimensions/final/orcid_pubs_from_dois_final.csv')
orcid_dimensions_publications = orcid_dimensions_contributions.drop_duplicates(subset='doi')
sul_pub_dimensions_contributions = pd.read_csv('input/dimensions/final/sul_pub_pubs_from_dois_final.csv')
sul_pub_dimensions_publications = sul_pub_dimensions_contributions.drop_duplicates(subset='doi')
sul_pub_raw_publications = pd.read_csv('input/sul_pub/pubs_all_authors_03212023.csv').drop_duplicates(subset='doi')

# Get combined publications and count
combined_publications = combined_contributions.drop_duplicates(subset='doi') # delete duplicate publications
combined_publications_count = len(combined_publications)

# Get SUL Pub publications count and DOI count
sul_pub_raw_publications_count = sul_pub_raw_publications.shape[0]
sul_pub_raw_publications_doi_count = len(sul_pub_raw_publications[~sul_pub_raw_publications['doi'].isna()])

# Store DOIs in variables for Venn diagram
openalex_dimensions_publications_dois = openalex_dimensions_publications.doi
orcid_dimensions_publications_dois = orcid_dimensions_publications.doi
sul_pub_dimensions_publications_dois = sul_pub_dimensions_publications.doi
dimensions_publications_dois = dimensions_publications.doi

# Get table of publication types
publications_type = combined_publications.type.value_counts(normalize = True).mul(100)
publications_type = publications_type.rename_axis('Percentage').reset_index(name='Type')

# Get id counts to see if we can pivot to other data sources
publications_pmcid_count = combined_publications[combined_publications.pmcid.notnull()].shape[0]
publications_arxiv_id_count = combined_publications[combined_publications.arxiv_id.notnull()].shape[0]

# get data and labels for open access status of publications for pie chart
open_access_pie_data = combined_publications['open_access_cleaned'].value_counts().sort_values()
open_access_pie_labels = combined_publications['open_access_cleaned'].value_counts().sort_values().index

# See how many publications are preprints
publications_oa_pre_print = combined_publications[combined_publications.type == 'preprint']
publications_oa_pre_print_count = publications_oa_pre_print[publications_oa_pre_print.open_access_cleaned != 'close'].shape[0]

# get open access data by school
group_by_school = pd.DataFrame()
group_by_school['core_schools'] = combined_publications['core_schools']
group_by_school['Open access status'] = combined_publications['open_access_cleaned'].str.capitalize()
group_by_school_pie = group_by_school.groupby(['core_schools', 'Open access status']).size().unstack()

# open access by school view
open_access_percent_school = group_by_school.groupby(['core_schools', 'Open access status']).size().unstack()
open_access_percent_school['oa_all'] = open_access_percent_school['Bronze'] + open_access_percent_school['Gold'] + open_access_percent_school['Green'] + open_access_percent_school['Hybrid']
open_access_percent_school['Total Publications'] = open_access_percent_school['oa_all'] + open_access_percent_school['Closed']
open_access_percent_school['OA Bronze'] = ((open_access_percent_school['Bronze']/open_access_percent_school['Total Publications']).multiply(100).round(decimals=2)).astype(str)
open_access_percent_school['OA Gold'] = ((open_access_percent_school['Gold']/open_access_percent_school['Total Publications']).multiply(100).round(decimals=2)).astype(str)
open_access_percent_school['OA Green'] = ((open_access_percent_school['Green']/open_access_percent_school['Total Publications']).multiply(100).round(decimals=2)).astype(str)
open_access_percent_school['OA Hybrid'] = ((open_access_percent_school['Hybrid']/open_access_percent_school['Total Publications']).multiply(100).round(decimals=2)).astype(str)
open_access_percent_school['Closed'] = ((open_access_percent_school['Closed']/open_access_percent_school['Total Publications']).multiply(100).round(decimals=2)).astype(str)
open_access_percent_school['OA Combined'] = ((open_access_percent_school['oa_all']/open_access_percent_school['Total Publications']).multiply(100).round(decimals=2)).astype(str)
open_access_percent_school = open_access_percent_school.drop(columns=['oa_all', 'Bronze', 'Gold', 'Hybrid', 'Green', 'Total Publications'])

# Get articles from Academic Council members to check OA policy compliance
oa_policy_publications = combined_contributions[combined_contributions.academic_council == 'yes']
oa_policy_publications = oa_policy_publications[oa_policy_publications.type == 'article']
oa_policy_publications = oa_policy_publications[oa_policy_publications.pub_year > 2022].drop_duplicates(subset='doi').open_access_cleaned

oa_policy_publications_count = len(oa_policy_publications)
oa_policy_publications_value_counts = oa_policy_publications.value_counts().sort_values()
oa_policy_publications_labels = oa_policy_publications.value_counts().sort_values().index

# Publication data for researchers with 'faculty' role
faculty_publications = combined_contributions[combined_contributions.role == 'faculty']
faculty_publications = faculty_publications[faculty_publications.type == 'article']
faculty_publications = faculty_publications[faculty_publications.pub_year > 2022].drop_duplicates(subset='doi').open_access_cleaned
faculty_publications_count = len(faculty_publications)
faculty_publications_value_counts = faculty_publications.value_counts().sort_values()
faculty_publications_labels = faculty_publications.value_counts().sort_values().index
faculty_2023 = combined_publications[combined_publications.role == 'faculty']
faculty_2023 = set(faculty_2023[faculty_2023.pub_year > 2022].sunet.tolist())

# Get academic council and non academic council publication data
academic_council_2023 = set(combined_publications[combined_publications.academic_council == 'yes'].sunet.tolist())
non_academic_council_publishers = combined_contributions[combined_contributions.academic_council == 'no'].role.dropna().value_counts(normalize = True).mul(100).round(1)
non_academic_council_publishers = non_academic_council_publishers.to_frame()
non_academic_council_publishers.reset_index(inplace=True)
non_academic_council_publishers = non_academic_council_publishers.rename(columns={'index': 'Role', 'role': 'Percentage'})
non_academic_council_publishers['Percentage'] = non_academic_council_publishers['Percentage'].astype(str)
non_academic_council_publications_count = len(non_academic_council_publishers)

# 2023 publications for for calculating percent of ao_policy_publications are open access
combined_publications_2023_count = len(combined_publications[combined_publications.pub_year > 2022])

# publication academic_council_sunets
oa_hybrid_cost = (combined_publications[combined_publications.open_access_cleaned == 'hybrid'].shape[0] * 3000)
oa_gold_cost = (combined_publications[combined_publications.open_access_cleaned == 'gold'].shape[0] * 1000)
oa_combined_cost = oa_hybrid_cost + oa_gold_cost
stanford_cost_gold = combined_publications.shape[0] * 1000
stanford_cost_hybrid = combined_publications.shape[0] * 3000

# publication grant data
publications_supporting_grants_count = combined_publications[combined_publications.supporting_grant_ids.notnull()].shape[0]
publications_federally_funded_count = combined_publications[combined_publications.federally_funded == 'yes'].shape[0]
publications_grant_and_federally_funded_count = combined_publications[combined_publications.federally_funded == 'yes'][combined_publications.supporting_grant_ids.notnull()].shape[0]
publications_federally_funded_dois = combined_publications[combined_publications.federally_funded == 'yes']['doi']
publications_supporting_grants_dois = combined_publications[combined_publications.supporting_grant_ids.notnull()]['doi']
publications_grant_and_federally_funded_2019 = combined_publications[combined_publications.federally_funded == 'yes'][combined_publications.supporting_grant_ids.notnull()][combined_publications.pub_year > 2019]
publications_grant_and_federally_funded_2019_data = publications_grant_and_federally_funded_2019['open_access_cleaned'].value_counts().sort_values()
publications_grant_and_federally_funded_2019_labels = publications_grant_and_federally_funded_2019['open_access_cleaned'].value_counts().sort_values().index

# Saving the objects:
with open('input/dashboard_objs.pkl', 'wb') as f:
    pickle.dump([sul_pub_raw_publications_count,
                 sul_pub_raw_publications_doi_count,
                 openalex_dimensions_publications_dois,
                 orcid_dimensions_publications_dois,
                 sul_pub_dimensions_publications_dois,
                 dimensions_publications_dois,
                 combined_publications_count,
                 publications_type,
                 publications_pmcid_count,
                 publications_arxiv_id_count,
                 open_access_pie_data,
                 open_access_pie_labels,
                 publications_oa_pre_print_count,
                 group_by_school_pie,
                 open_access_percent_school,
                 oa_policy_publications_count,
                 oa_policy_publications_value_counts,
                 oa_policy_publications_labels,
                 faculty_publications_count,
                 faculty_publications_value_counts,
                 faculty_publications_labels,
                 faculty_2023,
                 academic_council_2023,
                 non_academic_council_publications_count,
                 non_academic_council_publishers,
                 combined_publications_2023_count,
                 oa_hybrid_cost,
                 oa_gold_cost,
                 oa_combined_cost,
                 stanford_cost_gold,
                 stanford_cost_hybrid,
                 publications_supporting_grants_count,
                 publications_federally_funded_count,
                 publications_grant_and_federally_funded_count,
                 publications_federally_funded_dois,
                 publications_supporting_grants_dois,
                 publications_grant_and_federally_funded_2019_data,
                 publications_grant_and_federally_funded_2019_labels], f)

# with open('input/objs_four.pkl', 'wb') as f:
#     pickle.dump([oa_hybrid_cost,
#                  oa_gold_cost,
#                  oa_combined_cost,
#                  stanford_cost_gold,
#                  stanford_cost_hybrid], f)
#
# with open('input/objs_five.pkl', 'wb') as f:
#     pickle.dump([publications_supporting_grants_count,
#                  publications_federally_funded_count,
#                  publications_grant_and_federally_funded_count,
#                  publications_federally_funded_dois,
#                  publications_supporting_grants_dois], f)
#
# with open('input/objs_six.pkl', 'wb') as f:
#     pickle.dump([publications_grant_and_federally_funded_2019], f)
