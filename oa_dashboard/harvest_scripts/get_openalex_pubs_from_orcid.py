import csv, json, os, requests, time
from argparse import ArgumentParser
import pandas as pd

OUTPUT_CSV = f"output/openalex_publications_from_orcid.csv"

INPUT = pd.read_csv('../input/stanford_researcher_ids.csv')
sunet_orcid_dict = pd.Series(INPUT.orcid.values,index=INPUT.sunet).to_dict()

os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
with open(OUTPUT_CSV, 'a') as OUTPUT_CSV:
    publications_writer = csv.writer(OUTPUT_CSV)
    publications_writer.writerow(['sunet', 'orcid', 'doi'])
    for count, (sunet, orcid) in enumerate(sunet_orcid_dict.items(), start=1):
        print(f"Trying {count} of {len(INPUT)}: {orcid}")
        author_request = requests.get(f"https://api.openalex.org/authors/{orcid}", allow_redirects=True)
        if author_request.status_code == 200:
            works_url = author_request.json().get('works_api_url')
            works_request = requests.get(works_url)
            if works_request.status_code == 200:
                works = works_request.json()
                if works.get('results'):
                    for r in works.get('results'):
                        publications_writer.writerow([sunet, orcid, r.get('doi')])
            else:
                print(f'Works status_code was {works_request.status_code}')
        else:
            print(f'Author status_code was {author_request.status_code}')
