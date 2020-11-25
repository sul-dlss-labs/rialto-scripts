# Total Publication Count By Year Report

# Count the total number of publications from Stanford by year
# Output is list of publications by year, from the specified start year until the current year

# required gems:
# gem install 'csv'
# gem install 'faraday'
# gem install 'nokogiri'

# requires ruby 2.3 or better

# Set parameters below in the code, get the WOS_AUTH_CODE and pass in as an env variable,
#  create input CSV file and then run with
# WOS_AUTH_CODE=XXXX ruby totals_per_year_wos_search.rb

$stdout.sync = true # flush output immediately
require 'csv'
require './wos_client'

#### BEGIN PARAMETERS TO SET ####
output_file='tmp/rialto_totals_by_year.csv'
start_year = 1970
end_year = Time.now.year # default to current year
institutions = ["Stanford University"] # restrict the publication search (searched by name) to just authors from these institutions -- could be an array of institutions
#### END PARAMETERS TO SET ####

client = WosClient.new(wos_auth_code: ENV['WOS_AUTH_CODE']) # find the WOS authorization key in shared_configs for sul_pub

years_count = Hash.new(0)
total_pubs = 0
csv_output = CSV.open(output_file, "ab")
csv_output << ["Stanford University - Web of Science search by year"]
csv_output << ["Year","Total pubs"]
csv_output.close

for year in start_year..end_year do

  csv_output = CSV.open(output_file, "ab")

  result_xml_doc = client.year_search(year, institutions)
  num_records = client.num_records(result_xml_doc)

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
