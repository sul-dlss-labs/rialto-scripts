from argparse import ArgumentParser
import csv
import pandas as pd

def main():
    dois = []
    with open(args.in_file[0], 'r') as f:
        string = f.read()
        for i in string.split():
            if i.startswith('https://doi'):
                dois.append(i.replace('https://doi.org/', '')[:-1]+'\n')

    print(f'{len(dois)} dois exported.')
    with open(args.out_file[0], 'w') as out:
        df = pd.DataFrame({'doi':dois})
        df.to_csv(out)

if __name__ == "__main__":
    # CLI client options.
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--in_file",
        action='store',
        nargs="+",
        help="Which input file do you want to process?")
    parser.add_argument(
        "-o",
        "--out_file",
        action='store',
        nargs="+",
        help="What is the name of the file you want to export the results to?")
    args = parser.parse_args()
    main()
