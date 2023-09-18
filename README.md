# RIALTO Scripts

This repo contains scripts to produce custom research intelligence reporting.

Documentation for the scripts is often inline in the code.

Current Ruby scripts:
1. `faculty_wos_search.rb` - provide a list of faculty member names, search for their publications in WoS,
enumerate co-authors by country and/or organization, output a CSV file

2. `totals_per_year_wos_search.rb` - search for publications at Stanford by year between provided year range,
output a CSV file showing total publications for each year


## Producing a world map of co-authorship

1. Export a list of faculty members of interest from the sul-rialto-dev.stanford.edu app.  You can export all faculty members from Stanford by going to the organization view, selecting Stanford, and then filtering by faculty.
2. Open the CSV export in Excel and add a new column at the front to put the name in the expected format in a single cell: "Last Name, First Name". Add a header column.
3. Get the WOS_AUTH_CODE from Vault for sul-pub-prod
4. Run the `faculty_wos_search.rb` script.  Read the documentation.  Note that this will take a while for many authors, so may want to run a server in screen mode.
5. Take the output from the script and open in Excel.  The bottom of the output file has a list of countries and counts per country.  Select these rows and use Excel's geographical features to produce a map.  See https://support.microsoft.com/en-au/office/create-a-map-chart-in-excel-f2cfed55-d622-42cd-8ec9-ec8a358b593b
