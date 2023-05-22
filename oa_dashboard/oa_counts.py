import pickle
import pandas as pd
import json

def get_federally_funded(funders):
    if type(funders) == str:
        funders = eval(funders)
        combo = []
        for funder in funders:
            country = False
            government = False
            if funder.get('country_name') == 'United States':
                country = True
            if 'Government' in funder.get('types'):
                government = True
            combo.append([country, government])
        if [True, True] in combo:
            return 'yes'
        else:
            return 'no'

def get_federal_agencies(funders):
    if type(funders) == str:
        funders = eval(funders)
        for funder in funders:
            return f"{funder.get('name')}: {funder.get('linkout')[0]}"

def get_academic_council(s, ac_sunets):
    if s in ac_sunets:
        return 'yes'
    else:
        return 'no'

# Read in csv data
openalex_dimensions_contributions = pd.read_csv('input/dimensions/final/openalex_pubs_from_dois_final.csv')
openalex_dimensions_publications = openalex_dimensions_contributions.drop_duplicates(subset='doi')
orcid_dimensions_contributions = pd.read_csv('input/dimensions/final/orcid_pubs_from_dois_final.csv')

# Delete non-relevant years
orcid_dimensions_contributions = orcid_dimensions_contributions[orcid_dimensions_contributions.pub_year > 2017]
orcid_dimensions_publications = orcid_dimensions_contributions.drop_duplicates(subset='doi')
sul_pub_dimensions_contributions = pd.read_csv('input/dimensions/final/sul_pub_pubs_from_dois_final.csv')
sul_pub_dimensions_publications = sul_pub_dimensions_contributions.drop_duplicates(subset='doi')

# Get academic council sunets
academic_council_sunets = list(set(pd.read_csv('input/academic_council/academic_council_11-15-2022.csv').SUNETID.to_list()))

openalex_dimensions_publications_dois = openalex_dimensions_publications.doi
orcid_dimensions_publications_dois = orcid_dimensions_publications.doi
sul_pub_dimensions_publications_dois = sul_pub_dimensions_publications.doi

sul_pub_raw_publications = pd.read_csv('input/sul_pub/pubs_all_authors_03212023.csv').drop_duplicates(subset='doi')

combined_contributions = pd.concat([openalex_dimensions_contributions, orcid_dimensions_contributions, sul_pub_dimensions_contributions], axis=0, ignore_index=True).drop_duplicates(subset=['doi', 'sunet'])

combined_contributions['federally_funded'] = combined_contributions.apply(lambda row : get_federally_funded(row['funders']), axis = 1)

# Clean open access data
combined_contributions['open_access_cleaned'] = combined_contributions['open_access'].str.replace("'oa_all', ", '').str.replace("[", "").str.replace("]", "").str.replace("'", "")

combined_contributions['academic_council'] = combined_contributions.apply(lambda row : get_academic_council(row['sunet'], academic_council_sunets), axis = 1)

combined_contributions = combined_contributions.sort_values('academic_council')

combined_publications = combined_contributions.drop_duplicates(subset='doi')

oa_policy_publications = combined_contributions[combined_contributions.academic_council == 'yes']
oa_policy_publications = oa_policy_publications[oa_policy_publications.type == 'article']
oa_policy_publications = oa_policy_publications[oa_policy_publications.pub_year > 2020].drop_duplicates(subset='doi').open_access_cleaned

oa_policy_publications_count = len(oa_policy_publications)
oa_policy_publications_value_counts = oa_policy_publications.value_counts().sort_values()
oa_policy_publications_labels = oa_policy_publications.value_counts().sort_values().index

non_academic_council_publications_count = len(combined_contributions[combined_contributions.academic_council == 'no'].drop_duplicates(subset='doi'))

combined_publications = combined_contributions.drop_duplicates(subset='doi')
combined_publications_count = combined_publications.shape[0]
combined_publications_2021_count = len(combined_publications[combined_publications.pub_year > 2020])

sul_pub_raw_publications_count = sul_pub_raw_publications.shape[0]

sul_pub_raw_publications_doi_count = len(sul_pub_raw_publications[~sul_pub_raw_publications['doi'].isna()])

openalex_dimensions_publications = openalex_dimensions_publications[openalex_dimensions_publications.pub_year > 2017]

orcid_dimensions_publications = orcid_dimensions_publications[orcid_dimensions_publications.pub_year > 2017]

publications_type = combined_publications.type.value_counts(normalize = True).mul(100).round(1).astype(str)

publications_pmcid_count = combined_publications[combined_publications.pmcid.notnull()].shape[0]

publications_arxiv_id_count = combined_publications[combined_publications.arxiv_id.notnull()].shape[0]

plot_two_data = combined_publications['open_access_cleaned'].value_counts().sort_values()

plot_two_labels = combined_publications['open_access_cleaned'].value_counts().sort_values().index

publications_oa_pre_print = combined_publications[combined_publications.type == 'preprint']
publications_oa_pre_print_count = publications_oa_pre_print[publications_oa_pre_print.open_access_cleaned != 'close'].shape[0]
# combined_contributions['contribution_id'] = f"{combined_contributions['sunet']}-{combined_contributions['doi']}"
core_schools = ["Graduate School of Business", "Graduate School of Education", "School of Engineering", "School of Humanities and Sciences", "School of Medicine", "Stanford Doerr School of Sustainability", "Stanford Law School"]
schools_required = combined_contributions.dropna(subset='schools') #.iloc[:4]
org_df = pd.DataFrame(columns=['schools', 'open_access_cleaned'])
for index, row in schools_required.iterrows():
    schools = row.schools.split('|')
    for school in schools:
        if school in core_schools:
            org_df = pd.concat([org_df, pd.DataFrame({'schools': [school], 'open_access_cleaned': [row.open_access_cleaned]})], axis=0, ignore_index=True)
            print(f"Finished row {index+1} of {101210}")

org_df = org_df.astype({'schools':'string', 'open_access_cleaned': 'string'})
org_df.to_csv('org_df.csv')

plot_three_data = org_df.groupby(["schools", "open_access_cleaned"]).size().unstack()

oa_cost = (combined_publications[combined_publications.open_access_cleaned == 'hybrid'].shape[0] * 3000) + combined_publications[combined_publications.open_access_cleaned == 'gold'].shape[0] * 1000
stanford_cost_gold = combined_publications.shape[0] * 1000
stanford_cost_hybrid = combined_publications.shape[0] * 3000

publications_supporting_grants_count = combined_publications[combined_publications.supporting_grant_ids.notnull()].shape[0]

publications_federally_funded_count = combined_publications[combined_publications.federally_funded == 'yes'].shape[0]

publications_grant_and_federally_funded_count = combined_publications[combined_publications.federally_funded == 'yes'][combined_publications.supporting_grant_ids.notnull()].shape[0]

publications_federally_funded_dois = combined_publications[combined_publications.federally_funded == 'yes']['doi']

publications_supporting_grants_dois = combined_publications[combined_publications.supporting_grant_ids.notnull()]['doi']

publications_grant_and_federally_funded_2019 = combined_publications[combined_publications.federally_funded == 'yes'][combined_publications.supporting_grant_ids.notnull()][combined_publications.pub_year > 2019]

federal_agencies = publications_grant_and_federally_funded_2019.apply(lambda row : get_federal_agencies(row['funders']), axis = 1).value_counts(normalize = True).mul(100).round(1).astype(str)

combined_publications.to_csv('input/dimensions/final/combined_publications.csv')

# Saving the objects:
with open('input/objs_one.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
    pickle.dump([sul_pub_raw_publications_count,
                 sul_pub_raw_publications_doi_count,
                 openalex_dimensions_publications_dois,
                 orcid_dimensions_publications_dois,
                 sul_pub_dimensions_publications_dois,
                 combined_publications_count], f)

with open('input/objs_two.pkl', 'wb') as f:
    pickle.dump([publications_type,
                 publications_pmcid_count,
                 publications_arxiv_id_count,
                 plot_two_data,
                 plot_two_labels,
                 publications_oa_pre_print_count], f)

with open('input/objs_three.pkl', 'wb') as f:
    pickle.dump([plot_three_data,
                 oa_policy_publications_count,
                 oa_policy_publications_value_counts,
                 oa_policy_publications_labels,
                 non_academic_council_publications_count,
                 combined_publications_2021_count], f)

with open('input/objs_four.pkl', 'wb') as f:
    pickle.dump([oa_cost,
                 stanford_cost_gold,
                 stanford_cost_hybrid,
                 publications_supporting_grants_count,
                 publications_federally_funded_count,
                 publications_grant_and_federally_funded_count,
                 publications_federally_funded_dois,
                 publications_supporting_grants_dois,
                 publications_grant_and_federally_funded_2019,
                 federal_agencies], f)
