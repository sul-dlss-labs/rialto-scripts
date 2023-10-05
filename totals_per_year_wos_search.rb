# Total Publication Count By Year Report

# Count the total number of publications from Stanford by year
# Output is list of publications by year, from the specified start year until the current year

# required gems:
# gem install 'csv'
# gem install 'faraday'
# gem install 'faraday-retry'
# gem install 'nokogiri'
# gem install 'activesupport'

# requires ruby 2.3 or better

# Set parameters below in the code, get the WOS_API_KEY and pass in as an env variable,
#  create input CSV file and then run with
# WOS_API_KEY=XXXX ruby totals_per_year_wos_search.rb

$stdout.sync = true # flush output immediately
require 'csv'
require 'active_support/all'
require 'faraday'
require 'faraday/retry'
require 'nokogiri'
require './clarivate/rest_client.rb'
require './web_of_science/rest_retriever.rb'
require './web_of_science/base_rest_retriever.rb'
require './web_of_science/user_query_rest_retriever.rb'
require './web_of_science/queries.rb'
require './web_of_science/record.rb'
require './web_of_science/records.rb'
require './web_of_science/xml_parser.rb'
require './faculty_wos_search_helper'
require './web_of_science.rb'

#### BEGIN PARAMETERS TO SET ####
output_file='tmp/rialto_totals_by_year.csv'

start_year = 2021
end_year = Time.now.year # default to current year
institutions = ["Stanford"] # restrict the publication search (searched by name) to just authors from these institutions -- could be an array of institutions
#### END PARAMETERS TO SET ####

years_count = Hash.new(0)
total_pubs = 0
csv_output = CSV.open(output_file, "ab")
csv_output << ["#{institutions.join(', ')} - Web of Science search by year"]
csv_output << ["Year","Total pubs"]
csv_output.close

for year in start_year..end_year do

  csv_output = CSV.open(output_file, "ab")

  query = "PY=(#{year}) AND AD=(#{quote_wrap(institutions).join(" OR ")})"

  retriever = WebOfScience.queries.user_query(query, batch_size: 0)
  results = retriever.next_batch.to_a;
  num_records = retriever.records_found # shows total number of results returned

  puts "searching for #{year}...found #{num_records} pubs"
  years_count[year] = num_records
  total_pubs += num_records
  csv_output << [year,num_records]
  csv_output.close

end

puts
puts "Total pubs analzyed: #{total_pubs}"
puts

csv_output = CSV.open(output_file, "ab")
csv_output << []

csv_output << ["Total pubs",total_pubs]

csv_output.close
