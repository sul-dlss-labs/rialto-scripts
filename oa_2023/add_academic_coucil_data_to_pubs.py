import pandas as pd
import numpy as np

pubs = pd.read_csv('input/dimensions_pubs_from_sul_pub_dois.csv').drop_duplicates(subset=['doi', 'sunet'])
academic_council = pd.read_csv('input/academic_council_11-15-2022.csv')
academic_council = academic_council.rename(columns = {'SUNETID':'sunet'})

# Get members of academic council
pubs['academic_council'] = pubs['sunet'].isin(academic_council['sunet'].unique())

# Get department and school
df_out = pd.merge(pubs, academic_council, how='left', left_on='sunet', right_on='sunet')

assert df_out.shape[0] == pubs.shape[0], "You lost some publications somewhere."
# Get data
df_out.to_csv('dimensions_full_data.csv')
