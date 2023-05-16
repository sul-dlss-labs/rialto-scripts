import pandas as pd

in_df = pd.read_csv('input/dimensions_full_data.csv')

funders = []

us_gov_funded = in_df[in_df.federally_funded == 'yes']

for i in us_gov_funded.funders:
    funders.extend(i.strip('][').split(', '))

unique_funders = list(set(funders))

for i in unique_funders:
    print(i)

us_gov_funded.to_csv('out.csv')
