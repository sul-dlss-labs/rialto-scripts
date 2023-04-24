import pickle
import pandas as pd

dimensions_contributions = pd.read_csv('input/dimensions_full_data.csv')
dimensions_publications = dimensions_contributions.drop_duplicates(subset='doi')
sul_pub_publications = pd.read_csv('input/pubs_all_authors_03212023.csv').drop_duplicates(subset='doi')

# Clean open access data
dimensions_contributions['open_access_cleaned'] = dimensions_contributions['open_access'].str.replace("'oa_all', ", '').str.replace("[", "").str.replace("]", "").str.replace("'", "")
dimensions_publications['open_access_cleaned'] = dimensions_publications['open_access'].str.replace("'oa_all', ", '').str.replace("[", "").str.replace("]", "").str.replace("'", "")

publication_count_sul_pub = sul_pub_publications.shape[0]

publications_with_doi_count = len(sul_pub_publications[~sul_pub_publications['doi'].isna()])

publication_count_dimensions = dimensions_publications.shape[0]

publications_type = dimensions_publications.type.value_counts(normalize = True).mul(100).round(1).astype(str)

publications_pmcid_count = dimensions_publications[dimensions_publications.pmcid.notnull()].shape[0]

publications_arxiv_id_count = dimensions_publications[dimensions_publications.arxiv_id.notnull()].shape[0]

plot_two_data = dimensions_publications['open_access_cleaned'].value_counts().sort_values()

plot_two_labels = dimensions_publications['open_access_cleaned'].value_counts().sort_values().index

plot_three_data = dimensions_contributions.groupby(["School ", "open_access_cleaned"]).size().unstack()

publications_oa_pre_print_count = dimensions_publications[dimensions_publications.type == 'preprint'][dimensions_publications.open_access_cleaned != 'close'].shape[0]

publications_supporting_grants_count = dimensions_publications[dimensions_publications.supporting_grant_ids.notnull()].shape[0]

publications_federally_funded_count = dimensions_publications[dimensions_publications.federally_funded == 'yes'].shape[0]

publications_grant_and_federally_funded_count = dimensions_publications[dimensions_publications.federally_funded == 'yes'][dimensions_publications.supporting_grant_ids.notnull()].shape[0]

publications_federally_funded_dois = dimensions_publications[dimensions_publications.federally_funded == 'yes']['doi']

publications_supporting_grants_dois = dimensions_publications[dimensions_publications.supporting_grant_ids.notnull()]['doi']

publications_grant_and_federally_funded_2019 = dimensions_publications[dimensions_publications.federally_funded == 'yes'][dimensions_publications.supporting_grant_ids.notnull()][dimensions_publications.pub_year > 2019]

# Saving the objects:
with open('objs.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
    pickle.dump([publication_count_sul_pub,
                 publications_with_doi_count,
                 publication_count_dimensions,
                 publications_type,
                 publications_pmcid_count,
                 publications_arxiv_id_count,
                 plot_two_data,
                 plot_two_labels,
                 plot_three_data,
                 publications_supporting_grants_count,
                 publications_federally_funded_count,
                 publications_grant_and_federally_funded_count,
                 publications_federally_funded_dois,
                 publications_supporting_grants_dois,
                 publications_grant_and_federally_funded_2019], f)
