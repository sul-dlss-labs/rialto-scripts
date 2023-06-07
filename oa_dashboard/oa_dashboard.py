import pathlib

import pickle
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import venn
import streamlit as st
from matplotlib_venn import venn2, venn2_circles
from matplotlib_venn import venn3, venn3_circles

sns.set(style="darkgrid")

# Getting back the objects:
sul_pub_raw_publications_count,\
sul_pub_raw_publications_doi_count,\
openalex_dimensions_publications_dois,\
orcid_dimensions_publications_dois,\
sul_pub_dimensions_publications_dois,\
dimensions_publications_dois,\
combined_publications_count,\
publications_type,\
publications_pmcid_count,\
publications_arxiv_id_count,\
open_access_pie_data,\
open_access_pie_labels,\
publications_oa_pre_print_count,\
group_by_school_pie,\
open_access_percent_school,\
oa_policy_publications_count,\
oa_policy_publications_value_counts,\
oa_policy_publications_labels,\
faculty_publications_count,\
faculty_publications_value_counts,\
faculty_publications_labels,\
faculty_2023,\
academic_council_2023,\
non_academic_council_publications_count,\
non_academic_council_publishers,\
combined_publications_2023_count,\
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
publications_grant_and_federally_funded_2019_data,\
publications_grant_and_federally_funded_2019_labels = pd.read_pickle('input/dashboard_objs.pkl')

# Color scheme
celadon = '#9CDE9F'
atomic_tangerine = '#FF934F'
cool_grey = '#A09EBB'
lemon_chiffon = '#FFFACD'
light_salmon = '#FFA07A'
pale_turquoise = '#AFEEEE'

venn_4_colors = [
    # r, g, b, a
    [160, 158, 187, 0.9],
    [156, 222, 159, 0.8],
    [255, 147, 79, 0.6],
    [255, 250, 205, 0.4],
]
venn_4_colors = [
    [i[0] / 255.0, i[1] / 255.0, i[2] / 255.0, i[3]]
    for i in venn_4_colors
]

oa_colours = {'bronze': '#CF853A',
           'gold': '#FFCA2A',
           'closed': '#2E4052',
           'green': '#35AB68',
           'hybrid': '#3772FF'}

role_colours = {'students, fellows, and residents': celadon,
                'registry': lemon_chiffon,
                'staff': cool_grey,
                'phdstudent': light_salmon,
                'postdoc': pale_turquoise,
                'faculty': atomic_tangerine}

# Plotting functions
def plot_one():
    st.title("Publications by Stanford researchers 2018-2023")
    st.header("Publications data context")
    st.write("The publications presented in this report are from Dimensions, Openalex, ORCID id, and SUL-Pub; SUL-Pub publications are harvested from Web of Science and Pubmed. The Dimensions, ORCID id, and OpenAlex publications were harvested based on the ORCID id of each researcher. The SUL-Pub publications were harvested from Web of Science and Pubmed initially using a name and institution query, then they were reviewed by each researcher for accuracy. All publications containing a DOI were then re-harvested from Dimensions in order to enrich the data available for each publication.")
    st.write(f"There were {sul_pub_raw_publications_count:,} publications exported from SUL-Pub. {sul_pub_raw_publications_doi_count:,} of them had a DOI. We were able to find {sul_pub_dimensions_publications_dois.shape[0]:,} of them in Dimensions ({round(100*(sul_pub_dimensions_publications_dois.shape[0]/sul_pub_raw_publications_doi_count))}%) by queying their DOI. An additional {dimensions_publications_dois.shape[0]:,} publications were harvested from Dimensions, {openalex_dimensions_publications_dois.shape[0]:,} from Openalex, and {orcid_dimensions_publications_dois.shape[0]:,} from ORCID. Combining all data sources and removing duplicates results in {combined_publications_count:,} total unique publications.")

    st.header("Compilation of 2018-2023 Stanford publications")
    st.image(str("input/rialto-data-flow.png"))
    st.header("2018-2023 Stanford Publications by Data Source")
    st.caption("Number of unique and duplicate Stanford publications by data source.")
    labels = venn.get_labels([set(openalex_dimensions_publications_dois), set(orcid_dimensions_publications_dois), set(sul_pub_dimensions_publications_dois), set(dimensions_publications_dois)], fill=['number']) # add 'logic' to 'fill' to get region numbers
    fig, ax = venn.venn4(labels, names=['OpenAlex', 'Orcid id', 'SUL Pub', 'Dimensions'], colors=venn_4_colors)
    st.pyplot(fig)
    st.header("2018-2023 Stanford publications by type")
    st.write(publications_type)

def plot_two():
    st.title("Open access publication trends")
    st.header("Available identifiers")
    st.write(f"{publications_pmcid_count:,} ({round(publications_pmcid_count/combined_publications_count*100)}%) of publications had pmcid values. {publications_arxiv_id_count:,} ({round(publications_arxiv_id_count/combined_publications_count*100)}%) of publications had arxiv_id values.")

    st.header("Open access status of 2018-2023 Stanford publications")
    st.caption("Distribution of 2018-2023 Stanford Publications by open access status based on [Dimensions/Unpaywall access categories](https://www.dimensions.ai/wp-content/uploads/2021/02/Dimensions_New-OA-status-definition.pdf)")
    plt.pie(open_access_pie_data, labels = [s.capitalize() for s in open_access_pie_labels], colors=[oa_colours[key] for key in open_access_pie_labels], autopct='%.2f')
    st.pyplot(plt)

    st.header("Open access preprints")
    st.write(f"There are {publications_oa_pre_print_count:,} open access preprints.")

def plot_three():
    st.title("Opportunities for Increasing open access publications")

    st.header("Open access status of 2018-2023 publications by Stanford school")
    st.caption("Distribution of 2018-2023 Publications by open access status for each Stanford school. Based on [Dimensions/Unpaywall access categories](https://www.dimensions.ai/wp-content/uploads/2021/02/Dimensions_New-OA-status-definition.pdf)")
    plot = group_by_school_pie.plot(kind='bar', stacked=True, color=[oa_colours.get('bronze'), oa_colours.get('closed'), oa_colours.get('gold'), oa_colours.get('green'), oa_colours.get('hybrid')])
    plot.set(xlabel='School', ylabel='Publications')

    st.pyplot(plt)

    st.header("Open access publications by school (2018-2023)")
    st.write(open_access_percent_school + '%')

    # clears cache
    plt.figure()
    st.header("Articles written by members of the academic council (2023)")
    st.write("The Stanford open access policy covers articles written by members of the academic council since December 2020. Dimensions does not provide publication months, and we also don't have historical lists of academic council members, so the data below includes all publications with type 'article' written by a member of the academic council since January 1, 2023.")
    st.write(f"There were {combined_publications_2023_count:,} in 2023. There were {oa_policy_publications_count:,} ({round((oa_policy_publications_count/combined_publications_2023_count)*100):,}%) publications covered by the Stanford academic policy.")
    st.write(f"{non_academic_council_publications_count:,} ({round((non_academic_council_publications_count/combined_publications_count)*100):,}%) of all publications since 2023 do not include an author on the academic council.")
    plt.pie(oa_policy_publications_value_counts, labels = oa_policy_publications_labels, colors=[oa_colours[key] for key in oa_policy_publications_labels], autopct='%.0f%%')
    st.pyplot(plt)

    # clears cache
    plt.figure()
    st.header("Articles writted by researchers with the faculty role (2023)")
    st.write(f"There were {combined_publications_2023_count:,} in 2023. There were {faculty_publications_count:,} ({round((faculty_publications_count/combined_publications_2023_count)*100):,}%) publications written by researchers with the 'faculty' role in the Profiles database.")
    plt.pie(faculty_publications_value_counts, labels = faculty_publications_labels, colors=[oa_colours[key] for key in faculty_publications_labels], autopct='%.0f%%')
    st.pyplot(plt)

    st.header("Role of non academic council publishers")
    st.write(non_academic_council_publishers)

    st.header("Comparison of faculty role (2023) with academic council (Fall 2022) designation")
    labels = venn.get_labels([faculty_2023, academic_council_2023], fill=['number']) # add 'logic' to 'fill' to get region numbers
    fig, ax = venn.venn4(labels, names=['Faculty', 'Academic Council'], colors=venn_4_colors)
    st.pyplot(fig)


def plot_four():
    st.title("Decreasing the cost of open access publishing")
    st.header("Open access publication cost")
    st.write(f"Based on conservative estimates of average article processing charges-\$1,000 for gold open access articles and \$3,000 for hybrid open access articles-Stanford authors likely paid upwards of: \${oa_gold_cost:,} for gold open access and, \${oa_hybrid_cost:,} for hybrid open access during 2018-2023, resulting in an estimated \${oa_combined_cost:,} spent on article processing charges.")
    st.write(f"Paying to publish all 2018-2023 Stanford publications in gold open access journals would have likely cost upwards of \${stanford_cost_gold:,} while paying to publish all publications in hybrid open access journals would have likely cost upwards of \${stanford_cost_hybrid:,}.")

def plot_five():
    st.title("Funding trends")
    st.header("Grant data in Dimensions")
    st.write(f"{len(publications_supporting_grants_dois):,} ({round((len(publications_federally_funded_dois)/combined_publications_count)*100)}%) publications had associated grant data.")
    st.write(f"There is no field in the Dimensions organization entity that identifies it as a U.S. federal funding agency. To determine federal funding agencies we used a list from a recent OSTP impact study (Schares, 2022). {publications_federally_funded_count:,} ({round((publications_federally_funded_count/combined_publications_count)*100)}%) publications were federally funded. {publications_grant_and_federally_funded_count:,} publications were both federally funded and have values in the supporting_grant_ids column.")
    labels = venn.get_labels([set(publications_supporting_grants_dois), set(publications_federally_funded_dois)], fill=['number']) # add 'logic' to 'fill' to get region numbers
    fig, ax = venn.venn4(labels, names=['Has Associated Grant', 'Federally Funded'], colors=venn_4_colors)
    st.pyplot(fig)
    # clears cache
    plt.figure()
    st.header("Open access status of federally funded publications")
    st.write("In order to estimate the percentage of Stanford publication that will have open access mandates, we can filter the publications for those containing a grant_id that are from a U.S. Government organization and then group them by open access status.")
    plt.pie(publications_grant_and_federally_funded_2019_data, labels = publications_grant_and_federally_funded_2019_labels, autopct='%.0f%%')

    st.pyplot(plt)

    st.header("References")
    st.write("Schares, E. (2022). OSTP impact. https://doi.org/10.5281/zenodo.7254815. Accessed May 31, 2023.")

def main():

    page = st.sidebar.selectbox(
        "Select a Page",
        [
            "Publications by Stanford Researchers",
            "Open Access Publications Trends",
            "Opportunities for Increasing Open Access Publications",
            "Decreasing the Cost of Open Access Publishing",
            "Funder & Publisher Research Access Policies"

        ]
    )
    if page == "Publications by Stanford Researchers":
        plot_one()
    elif page == "Open Access Publications Trends":
        plot_two()
    elif page == "Opportunities for Increasing Open Access Publications":
        plot_three()
    elif page == "Decreasing the Cost of Open Access Publishing":
        plot_four()
    elif page == "Funder & Publisher Research Access Policies":
        plot_five()

if __name__ == "__main__":
    main()
