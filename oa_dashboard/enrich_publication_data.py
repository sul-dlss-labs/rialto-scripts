import glob
import numpy as np
import pandas as pd

# helper functions
def filter_schools(schools, core_schools):
    """Filters out schools that are not core schools."""
    if not schools:
        return None
    else:
        schools = schools.split('|')
        return next(school for school in schools if school in core_schools)

def get_academic_council(sunet, ac_sunets):
    """Returns the academic council membership status for
    each row based on the sunet."""
    if sunet in ac_sunets:
        return 'yes'
    else:
        return 'no'

def get_federally_funded(publication_funders):
    """Retrieves the funder ids for each publication and checks
    to see if those ids are in the federal funders list."""
    if type(publication_funders) == str:
        publication_funders = eval(publication_funders)
        publication_funders_ids = []
        for funder in publication_funders:
            publication_funders_ids.append(funder.get('id'))
        if len(set(publication_funders_ids).intersection(federal_funders)) > 0:
            return 'yes'
        else:
            return 'no'

def get_first_value(cell_value):
    """Returns the first value of a list, or None. Used to simplfy
    the categorical data in some rows by reducing it to the first value."""
    if len(cell_value) == 0:
        value = None
    else:
        value = cell_value[0]
    return value


school_files = glob.glob('input/profiles/*') # read in org data from Profiles
assert len(school_files) == 7
school_df = pd.DataFrame()

for file in school_files:
    school_df = pd.concat([pd.read_csv(file), school_df]) # concatenate all school files into one dataframe

funders_df = pd.read_csv('input/shares_ostp/Funders.csv', skiprows=1) # read in funders data from OSTP report
federal_funders = list(set(funders_df.ID))

academic_council_sunets = list(set(pd.read_csv('input/academic_council/academic_council_11-15-2022.csv').SUNETID.to_list())) # read in academic council data

# contributions are not the same as publications; 3 co-authors = 3 contributions, but only 1 publication
contribution_files = glob.glob('input/dimensions/intermediate/*.csv')
assert len(contribution_files) == 4
contribution_count = 0
combined_contributions = pd.DataFrame()
for count, file in enumerate(contribution_files, start=1):
    contribution_df = pd.read_csv(file)
    contribution_df = contribution_df.drop_duplicates(subset=['sunet', 'doi']) # remove duplicate contributions
    contribution_df = contribution_df[contribution_df.iloc[:, 0] != contribution_df.columns[0]] # remove duplicate header rows
    contribution_df['pub_year'] = contribution_df['pub_year'].fillna(-1)
    contribution_df['pub_year'] = contribution_df['pub_year'].astype('int')
    contribution_df = contribution_df[contribution_df.pub_year > 2017] # remove pubs prior to 2018
    contribution_count += len(contribution_df)
    contribution_df.to_csv(f"input/dimensions/final/{file.split('/')[-1].split('.')[0]}_final.csv")
    combined_contributions = pd.concat([combined_contributions, contribution_df]) # concatenate all contribution files
    print(f'Finished loading contribution file {count} of {len(contribution_files)}.')

assert len(combined_contributions) == contribution_count # make sure dataframes were concatenated correctly

combined_contributions = combined_contributions.drop_duplicates(subset=['sunet', 'doi']) # we need to remove duplicate contributions again

expected_publication_count = combined_contributions.shape[0] # grab pubplication count for late test

expected_column_count = combined_contributions.shape[1] # grab pubplication count for late test

# add organization fields
combined_contributions['schools'] = ''
combined_contributions['departments'] = ''
combined_contributions['role'] = ''

for sunet in set(combined_contributions.sunet): # loop through sunets and add org data from schools_df
    schools = school_df['schools'][school_df['sunetid'] == sunet].tolist()
    schools_string = get_first_value(schools)

    combined_contributions['schools'] = np.where(combined_contributions['sunet'] == sunet, schools_string, combined_contributions['schools'])

    departments = school_df['departments'][school_df['sunetid'] == sunet].tolist()
    departments_string = get_first_value(departments)

    combined_contributions['departments'] = np.where(combined_contributions['sunet'] == sunet, departments_string, combined_contributions['departments'])

    roles = school_df['role'][school_df['sunetid'] == sunet].tolist()
    role_string = get_first_value(roles)

    combined_contributions['role'] = np.where(combined_contributions['sunet'] == sunet, role_string, combined_contributions['role'])

assert combined_contributions.shape[1] == expected_column_count +3 # make sure we added three columns successfully

# reformat open_access data in a new column for pie charts, removes the oa_all aggregate category
combined_contributions['open_access_cleaned'] = combined_contributions['open_access'].str.replace("'oa_all', ", '').str.replace("[", "").str.replace("]", "").str.replace("'", "")

# define the seven Stanford core schools so we can ignore the rest
core_schools = ["Graduate School of Business", "Graduate School of Education", "School of Engineering", "School of Humanities and Sciences", "School of Medicine", "Stanford Doerr School of Sustainability", "Stanford Law School"]

combined_contributions['core_schools'] = combined_contributions.apply(lambda row : filter_schools(row['schools'], core_schools), axis = 1)

combined_contributions['federally_funded'] = combined_contributions.apply(lambda row : get_federally_funded(row['funders']), axis = 1)

combined_contributions['academic_council'] = combined_contributions.apply(lambda row : get_academic_council(row['sunet'], academic_council_sunets), axis = 1)

assert combined_contributions.shape[1] == expected_column_count +7 # make sure we added three more columns successfully

assert combined_contributions.shape[0] == expected_publication_count # make sure we didn't lose any publications

combined_contributions.to_csv('input/dimensions/final/combined_contributions.csv')

print(f"The combined contributions dataframe has {combined_contributions.shape[0]} rows and {combined_contributions.shape[1]} columns. The columns are {combined_contributions.columns}")
