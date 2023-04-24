import pickle
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib_venn import venn2, venn2_circles

sns.set(style="darkgrid")

# Getting back the objects:
with open('objs.pkl', 'rb') as f:
    publication_count_sul_pub, publications_with_doi_count, publication_count_dimensions, publications_type, publications_pmcid_count, publications_arxiv_id_count, plot_two_data, plot_two_labels, plot_three_data, publications_supporting_grants_count, publications_federally_funded_count, publications_grant_and_federally_funded_count, publications_federally_funded_dois, publications_supporting_grants_dois, publications_grant_and_federally_funded_2019 = pickle.load(f)

# Open access colors
blue = '#01a7ee'
bronze = '#ffb13c'
gold = '#ffcf3c'
gray = '#ccd1db'
green = '#31caa8'
purple = '#9f29ff'
red = '#ff412c'

colours = {'bronze': bronze,
        'gold': gold,
       'closed': red,
       'green': green,
       'hybrid': gray}


# Helper functions
def plot_venn(array_one, array_two, label_one, label_two):
    set1 = set(array_one)
    set2 = set(array_two)

    total = len(set1.difference(set2)) + len(set2.difference(set1)) + len(set1.intersection(set2))
    print(f"Total: {total}")

    plot = plt.figure(figsize=(6,4))

    v = venn2(subsets = (len(set1.difference(set2)),
                         len(set2.difference(set1)),
                         len(set1.intersection(set2))), set_labels = (label_one, label_two),
                         alpha=1)

    c = venn2_circles(subsets = (len(set1.difference(set2)),
                                 len(set2.difference(set1)),
                                 len(set1.intersection(set2))), linestyle='solid', alpha=1)

    v.get_patch_by_id('10').set_color(blue)
    v.get_patch_by_id('11').set_color(green)
    v.get_patch_by_id('01').set_color(gold)

    v.get_label_by_id("10").set_x(-0.66)
    v.get_label_by_id("01").set_x(0.69)


    return plot

# Plotting functions
def plot_one():
    st.title("Publications by Stanford Researchers")
    st.subheader("Publications data context")
    st.write("The publications presented in this report were harvested from Web of Science and Pubmed initially and reviewed by each researcher for accuracy. All approved publications containing a doi were then re-harvested from Dimensions in order to enrich the data available for each publication.")
    st.write(f"There were {publication_count_sul_pub} publications exported from SUL-Pub. {publications_with_doi_count} of them had a doi. We were able to find {publication_count_dimensions} of them in Dimensions ({round(100*(publication_count_dimensions/publications_with_doi_count))}%) by queying their doi.")

    st.subheader("Publications by type")
    st.write(publications_type + '%')

def plot_two():
    st.title("Open Access Publication Trends")
    st.subheader("Publications data context")
    st.write("The publications presented in this report were harvested from Web of Science and Pubmed initially and reviewed by each researcher for accuracy. All approved publications containing a doi were then re-harvested from Dimensions in order to enrich the data available for each publication.")

    st.subheader("Available Identifiers")
    st.write(f"{publications_pmcid_count} ({round((publications_pmcid_count/publication_count_dimensions)*100)}%) publications had pmcid values. {publications_arxiv_id_count} ({round((publications_arxiv_id_count/publication_count_dimensions)*100)}%) publications had arxiv_id values.")

    st.subheader("Publications by Open Access Category")
    plt.pie(plot_two_data, labels = plot_two_labels, colors=[colours[key] for key in plot_two_labels], autopct='%.0f%%')
    st.pyplot(plt)

    st.subheader("Open Access Preprints")
    st.write(f"There are {publications_oa_pre_print_count} open access preprints.")

def plot_three():
    st.title("Opportunities for Increasning Open Access Publications")
    st.subheader("Publications data context")
    st.write("The publications presented in this report were harvested from Web of Science and Pubmed initially and reviewed by each researcher for accuracy. All approved publications containing a doi were then re-harvested from Dimensions in order to enrich the data available for each publication. This data set was then merged with an academic council data set containing school and department information. Stanford researchers that are not members of the academic council have been filtered of this set.")

    st.subheader("Open Access Status by School")
    plot = plot_three_data.plot(kind='bar', stacked=True, color=[bronze, red, gold, green, gray])
    plot.set(xlabel='School', ylabel='Publications')

    st.pyplot(plt)

def plot_five():
    st.title("Funding Trends")
    st.subheader("Publications data context")
    st.write("The publications presented in this report were harvested from Web of Science and Pubmed initially and reviewed by each researcher for accuracy. All approved publications containing a doi were then re-harvested from Dimensions in order to enrich the data available for each publication.")

    st.subheader("Grant Data in Dimensions")
    st.write(f"{publications_supporting_grants_count} ({round((publications_supporting_grants_count/publication_count_dimensions)*100)}%) publications had supporting_grant_ids values.")
    st.write(f"There is no field in the Dimensions organization entity that identifies it as a U.S. federal funding agency. We can identify federal funding agencies by combining the country and organization type–if the country equals 'United States' and the organization type equals 'government', we assume it to be a federal funding agency. {publications_federally_funded_count} ({round((publications_federally_funded_count/publication_count_dimensions)*100)}%) publications were federally funded. {publications_grant_and_federally_funded_count} publications were both federally funded and have values in the supporting_grant_ids column.")
    st.pyplot(plot_venn(publications_supporting_grants_dois, publications_federally_funded_dois, 'Has Associated Grant', 'Federally Funded'))

    # clears cache
    plt.figure()
    st.subheader("Open Access Status of Federally Funded Publications")
    df = publications_grant_and_federally_funded_2019
    data = df['open_access_cleaned'].value_counts().sort_values()
    labels = df['open_access_cleaned'].value_counts().sort_values().index
    plt.pie(data, labels = labels, colors=[colours[key] for key in labels], autopct='%.0f%%')

    st.pyplot(plt)

def main():

    page = st.sidebar.selectbox(
        "Select a Page",
        [
            "Publications by Stanford Researchers",
            "Open Access Publications Trends",
            "Opportunities for Increasning Open Access Publications",
            "Decreasing the Cost of Open Access Publishing",
            "Funder & Publisher Research Access Policies"

        ]
    )
    if page == "Publications by Stanford Researchers":
        plot_one()
    elif page == "Open Access Publications Trends":
        plot_two()
    elif page == "Opportunities for Increasning Open Access Publications":
        plot_three()
    elif page == "Funder & Publisher Research Access Policies":
        plot_five()

if __name__ == "__main__":
    main()
