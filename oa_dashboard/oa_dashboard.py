import pathlib

import pickle
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib_venn import venn2, venn2_circles
from matplotlib_venn import venn3, venn3_circles

sns.set(style="darkgrid")

font = {'family' : 'sans'}
plt.rc('font', **font)

root = pathlib.Path(__file__).parent

# Getting back the objects:
publication_count_sul_pub,\
publications_with_doi_count,\
openalex_dimensions_publications_dois,\
orcid_dimensions_publications_dois,\
sul_pub_dimensions_publications_dois,\
combined_publications_count = pd.read_pickle(root / 'input/objs_one.pkl')

publications_type,\
publications_pmcid_count,\
publications_arxiv_id_count,\
plot_two_data,\
plot_two_labels,\
publications_oa_pre_print_count = pd.read_pickle(root /  'input/objs_two.pkl')

plot_three_data,\
oa_policy_publications_count,\
oa_policy_publications_value_counts,\
oa_policy_publications_labels,\
oa_percent_school,\
non_academic_council_publications_count,\
non_academic_council_publishers,\
non_academic_council_publishers_labels,\
combined_publications_2021_count = pd.read_pickle(root / 'input/objs_three.pkl')

oa_hybrid_cost,\
oa_gold_cost,\
oa_combined_cost,\
stanford_cost_gold,\
stanford_cost_hybrid,\
publications_supporting_grants_count,\
publications_federally_funded_count,\
publications_grant_and_federally_funded_count,\
publications_federally_funded_dois,\
publications_supporting_grants_dois,\
publications_grant_and_federally_funded_2019 = pd.read_pickle(root / 'input/objs_four.pkl')

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

role_colours = {'students, fellows, and residents': red,
                'registry': blue,
                'staff': bronze,
                'phdstudent': gray,
                'postdoc': green,
                'faculty': gold}


# Helper functions
def plot_venn2(array_one, array_two, label_one, label_two):
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

def plot_venn3(array_one, array_two, array_three, label_one, label_two, label_three):
    set1 = set(array_one)
    set2 = set(array_two)
    set3 = set(array_three)

    fig, ax = plt.subplots()

    ax = venn3(subsets = (set1, set2, set3), set_labels = (label_one, label_two, label_three), alpha=1)

    ax.get_patch_by_id('001').set_color(blue)
    ax.get_patch_by_id('010').set_color(red)
    ax.get_patch_by_id('011').set_color(purple)
    ax.get_patch_by_id('100').set_color(gold)
    ax.get_patch_by_id('101').set_color(green)
    ax.get_patch_by_id('110').set_color(bronze)

    return fig

# Plotting functions
def plot_one():
    st.title("Publications by Stanford Researchers")
    st.header("Publications data context")
    st.write("The publications presented in this report are from Openalex, ORCID, and SUL-Pub; SUL-Pub publications are harvested from Web of Science and Pubmed. The ORCID and Openalex publicatins were harvested based on the ORCID id of each researcher. The SUL-Pub publications were harvested from Web of Science and Pubmed initially using a name and institution query, then they were reviewed by each researcher for accuracy. All publications containing a doi were then re-harvested from Dimensions in order to enrich the data available for each publication.")
    st.write(f"There were {publication_count_sul_pub:,} publications exported from SUL-Pub. {publications_with_doi_count:,} of them had a doi. We were able to find {sul_pub_dimensions_publications_dois.shape[0]:,} of them in Dimensions ({round(100*(sul_pub_dimensions_publications_dois.shape[0]/publications_with_doi_count))}%) by queying their doi. An additional {openalex_dimensions_publications_dois.shape[0]:,} publications were harvested from Openalex and {orcid_dimensions_publications_dois.shape[0]:,} publications were harvested from ORCID. Combining all data sources and removing duplicates results in {combined_publications_count:,}")

    st.header("Compilation of 2018-2023 Stanford Publications")
    st.image(str(root / "input/rialto-data-flow.png"))
    st.header("2018-2023 Stanford Publications by Data Source")
    st.caption("Number of unique and duplicate Stanford publications by data source.")
    st.pyplot(plot_venn3(openalex_dimensions_publications_dois, orcid_dimensions_publications_dois, sul_pub_dimensions_publications_dois, "OpenAlex", "ORCID iD", "Stanford Profiles (Web of Science & PubMed)"))

    st.header("2018-2023 Stanford Publications by Type")
    st.write(publications_type)

def plot_two():
    st.title("Open Access Publication Trends")
    st.header("Available Identifiers")
    st.write(f"{publications_pmcid_count:,} ({round(publications_pmcid_count/combined_publications_count*100)}%) publications had pmcid values. {publications_arxiv_id_count:,} ({round(publications_arxiv_id_count/combined_publications_count*100)}%) publications had arxiv_id values.")

    st.header("Open Access Status of 2018-2023 Stanford Publications")
    st.caption("Distribution of 2018-2023 Stanford Publications by open access status based on [Dimensions/Unpaywall access categories](https://www.dimensions.ai/wp-content/uploads/2021/02/Dimensions_New-OA-status-definition.pdf)")
    plt.pie(plot_two_data, labels = [s.capitalize() for s in plot_two_labels], colors=[colours[key] for key in plot_two_labels], autopct='%.2f')
    st.pyplot(plt)

    st.header("Open Access Preprints")
    st.write(f"There are {publications_oa_pre_print_count} open access preprints.")

def plot_three():
    st.title("Opportunities for Increasning Open Access Publications")

    st.header("Open Access Status of 2018-2023 Publications by Stanford School")
    st.caption("Distribution of 2018-2023 Publications by open access status for each Stanford school. Based on [Dimensions/Unpaywall access categories](https://www.dimensions.ai/wp-content/uploads/2021/02/Dimensions_New-OA-status-definition.pdf)")
    plot = plot_three_data.plot(kind='bar', stacked=True, color=[bronze, red, gold, green, gray])
    plot.set(xlabel='School', ylabel='Publications')

    st.pyplot(plt)

    st.header("Open Access Publications by School")
    st.write(oa_percent_school + '%')

    # clears cache
    plt.figure()
    st.header("Publications covered by Open Access Policy")
    st.write("The Stanford open access policy covers articles written by members of the academic council since December 2020. Dimensions does not provide publication months, and we also don't have historical lists of academic council members, so the data below includes all publications with type 'article' written by a member of the academic council since January 1, 2023.")
    st.write(f"There were {oa_policy_publications_count:,} ({round((oa_policy_publications_count/combined_publications_2021_count)*100):,}%) publications covered by the Stanford academic policy.")
    st.write(f"{non_academic_council_publications_count:,} ({round((non_academic_council_publications_count/combined_publications_count)*100):,}%) of all publications since 2018 do not include an author on the academic council.")
    plt.pie(oa_policy_publications_value_counts, labels = oa_policy_publications_labels, colors=[colours[key] for key in oa_policy_publications_labels], autopct='%.0f%%')
    st.pyplot(plt)

    # clears cache
    plt.figure()
    st.header("Role of Non Academic Council Publishers")
    st.write("The pie chart below shows the distrubition of roles among Stanford publishers that are not members of the academic council.")
    plt.pie(non_academic_council_publishers, labels = non_academic_council_publishers_labels, colors=[role_colours[key] for key in non_academic_council_publishers_labels], autopct='%.0f%%')
    st.pyplot(plt)

def plot_four():
    st.title("Decreasing the Cost of Open Access Publishing")
    st.header("Open access publication cost")
    st.write(f"Based on conservative estimates of average article processing charges-\$1,000 for gold open access articles and \$3,000 for hybrid open access articles-Stanford authors likely paid upwards of: \${oa_gold_cost:,} for gold open access and, \${oa_hybrid_cost:,} for hybrid open access during 2018-2023, resulting in an estimated \${oa_combined_cost:,} spent on article processing charges.")
    st.write(f"Paying to publish all 2018-2023 Stanford publications in gold open access journals would have likely cost upwards of \${stanford_cost_gold:,} while paying to publish all publications in hybrid open access journals would have likely cost upwards of \${stanford_cost_hybrid:,}.")

def plot_five():
    st.title("Funding Trends")
    st.header("Grant Data in Dimensions")
    st.write(f"{publications_supporting_grants_count:,} ({round((publications_supporting_grants_count/sul_pub_dimensions_publications_dois.shape[0])*100)}%) publications had associated grant data.")
    st.write(f"There is no field in the Dimensions organization entity that identifies it as a U.S. federal funding agency. To determine federal funding agencies we used a list from a recent OSTP impact study (Schares, 2022). {publications_federally_funded_count:,} ({round((publications_federally_funded_count/sul_pub_dimensions_publications_dois.shape[0])*100)}%) publications were federally funded. {publications_grant_and_federally_funded_count:,} publications were both federally funded and have values in the supporting_grant_ids column.")
    st.pyplot(plot_venn2(publications_supporting_grants_dois, publications_federally_funded_dois, 'Has Associated Grant', 'Federally Funded'))

    # clears cache
    plt.figure()
    st.header("Open Access Status of Federally Funded Publications")
    st.write("In order to estimate the percentage of Stanford publication that will have open access mandates, we can filter the publications for those containing a grant_id that are from a U.S. Government organization and then group them by open access status.")
    df = publications_grant_and_federally_funded_2019
    data = df['open_access_cleaned'].value_counts().sort_values()
    labels = df['open_access_cleaned'].value_counts().sort_values().index
    plt.pie(data, labels = [s.capitalize() for s in labels], colors=[colours[key] for key in labels], autopct='%.0f%%')

    st.pyplot(plt)

    st.header("References")
    st.write("Schares, E. (2022). OSTP impact. https://doi.org/10.5281/zenodo.7254815. Accessed May 31, 2023.")

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
    elif page == "Decreasing the Cost of Open Access Publishing":
        plot_four()
    elif page == "Funder & Publisher Research Access Policies":
        plot_five()

if __name__ == "__main__":
    main()
