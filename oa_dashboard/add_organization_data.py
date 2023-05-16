import glob
import numpy as np
import pandas as pd


school_files = glob.glob('input/profiles/*')
publication_df = pd.read_csv('input/dimensions/intermediate/orcid_pubs_from_dois.csv')

# Delete accidentaly harvested duplicates
publication_df = publication_df.drop_duplicates(subset=['sunet', 'doi'])
# Delete duplicate header rows
publication_df = publication_df[publication_df.iloc[:, 0] != publication_df.columns[0]]

school_df = pd.DataFrame()

for file in school_files:
    school_df = pd.concat([pd.read_csv(file), school_df])

publication_df['schools'] = ''
publication_df['departments'] = ''
for sunet in set(publication_df.sunet):
    schools = school_df['schools'][school_df['sunetid'] == sunet].tolist()
    if len(schools) == 0:
        schools_string = None
    else:
        schools_string = schools[0]

    publication_df['schools'] = np.where(publication_df['sunet'] == sunet, schools_string, publication_df['schools'])

    departments = school_df['departments'][school_df['sunetid'] == sunet].tolist()
    if len(departments) == 0:
        departments_string = None
    else:
        departments_string = departments[0]

    publication_df['departments'] = np.where(publication_df['sunet'] == sunet, departments_string, publication_df['departments'])

publication_df.to_csv('input/dimensions/final/orcid_pubs_from_dois_final.csv')
