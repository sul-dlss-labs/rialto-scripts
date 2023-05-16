import pandas as pd
import seaborn as sns

# Set parameters.
START_YEAR = 2018
END_YEAR = 2022

# Initial data input
academic_council = pd.read_csv("input/academic_council_11-15-2022.csv")
# assert academic_council.SUNETID.unique().shape[0] == academic_council.shape[0], "There are duplicates in the academic council csv."
contributions_unfiltered = pd.read_csv("input/out.csv")
publications = contributions_unfiltered.drop_duplicates(subset='doi')
# .pub_year.between(START_YEAR, END_YEAR)

# Build totals_publications dataframe and add all university wide publication counts by year.
total_publications = publications.pub_year.value_counts().to_frame().rename(columns={"pub_year": "Publications (Total)"})

# totals_publications = totals_publications.sort_index(ascending=True)
