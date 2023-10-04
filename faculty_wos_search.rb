# Faculty Collaboration Report

# Enumerate stanford faculty's collaborations by country and/or by institution
# Input is a list of faculty names in a csv file
# Output is co-authors by institution and/or country enumerated

# required gems:
# gem install 'csv'
# gem install 'faraday'
# gem install 'faraday-retry'
# gem install 'nokogiri'
# gem install 'activesupport'

# requires ruby 2.3 or better

# Set parameters below in the code, get the WOS_API_KEY and pass in as an env variable,
#  create input CSV file and then run with
# WOS_API_KEY=XXXX ruby faculty_wos_search.rb

# input file is CSV format with name in columns in "last_name", "first_name", "middle_name" format each in its own column
#  the CSV file should include a header row as well, with those exact headers (including matching case shown)
#  extra columns are fine and "middle_name" is optional
# you can obtain an author list in this CSV format from the sul-rialto-orgs app
# e.g.
# last,first,middle
# Donald,Duck,
# Dude,Somename,L

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
input_file='tmp/faculty.csv'
output_file='tmp/faculty_results.csv'

start_date = "2021-01-01" # limit the start date when searching for publications, format: YYYY-MM-DD
end_date = Time.now.strftime("%Y-%m-%d") # the end date defaults to today

limit = 5 # limit the number of people searched regardless of input size (useful for testing), set to nil for no limit
search_orgs = true # set to false to skip organization enumeration for faster results
# an array of organizations to restrict the collaboration enumeration to (set to nil to enumerate over all organizations if search_orgs is set to true)
restrict_to_organizations = nil # ['Stanford','Stanford University','UCSF','University of California San Francisco','UCSF School of Medicine','University of California, San Francisco','UCB','Berkeley','University of California Berkeley','UC Berkeley']
search_countries = true # set to false to skip country enumeration for faster results
institutions = ["Stanford"] # restrict the publication search (searched by name) to just authors from these institutions -- could be an array of institutions
#### END PARAMETERS TO SET ####

puts "Reading #{input_file}"
names = CSV.parse(File.read(input_file),:headers=>true)
puts "#{names.size} total names found"

unless limit.blank?
  puts "limit of #{limit} applied"
  names = names[0..limit-1]
end
total_names = names.size
puts "#{total_names} total names will be operated on"
puts

countries_count = Hash.new(0)
author_countries_count = Hash.new
organizations_count = Hash.new(0)
author_organizations_count = Hash.new

total_pubs = 0
# set some maximum number of runs we will attempt to fetch records for any given person (thereby limiting the max number of pubs to max_records * max_runs_per_person)
max_records = 100 # this is the maximum number that can be returned in single query by WoS
max_runs_per_person = 30 # maximum number of pages of max_records per person

names.each_with_index do |name,index|
  next if name['last_name'].blank? && name['first_name'].blank?

  csv_output = CSV.open(output_file, "ab")

  last_name = name['last_name']
  first_name = name['first_name']
  middle_name = name['middle_name']
  full_name = "#{last_name}, #{first_name} #{middle_name}".strip

  puts "#{index+1} of #{total_names}: searching on #{full_name}"
  author_countries_count[full_name] = Hash.new(0)
  author_organizations_count[full_name] = Hash.new(0)

  query = "AU=(\"#{full_name}\") AND AD=(#{quote_wrap(institutions).join(" OR ")})"
  query_params = WebOfScience::UserQueryRestRetriever::Query.new(publish_time_span: "#{start_date}+#{end_date}")

  retriever = WebOfScience.queries.user_query(query, query_params: query_params)
  results = retriever.next_batch.to_a;
  num_records = retriever.records_found # shows total number of results returned

  puts "...found #{num_records} pubs"

  if num_records > 0
    num_pubs = enumerate_results(results,countries_count,author_countries_count[full_name],organizations_count,author_organizations_count[full_name],search_countries,search_orgs,restrict_to_organizations)
    while retriever.next_batch? do # we have more to go
      puts "..... fetching next batch"
      results = retriever.next_batch.to_a if  # get the next batch
      num_pubs = enumerate_results(result,countries_count,author_countries_count[full_name],organizations_count,author_organizations_count[full_name],search_countries,search_orgs,restrict_to_organizations)
    end
  end

  # puts author_countries_count[name] if search_countries
  # puts author_organizations_count[name] if search_orgs

  puts
  total_pubs += num_records

  csv_output << []
  csv_output << [full_name,num_records]
  sorted_author_countries_count = author_countries_count[full_name].sort_by{ |k, v| v }.reverse.to_h
  sorted_author_organizations_count = author_organizations_count[full_name].sort_by{ |k, v| v }.reverse.to_h
  if search_countries
    csv_output << sorted_author_countries_count.map {|key,value| key }
    csv_output << sorted_author_countries_count.map {|key,value| value }
  end
  if search_orgs
    csv_output << sorted_author_organizations_count.map {|key,value| key }
    csv_output << sorted_author_organizations_count.map {|key,value| value }
  end

  csv_output.close

end

puts
puts "Total pubs analzyed: #{total_pubs}"
puts
sorted_countries_count = countries_count.sort_by{ |k, v| v }.reverse.to_h if search_countries
sorted_organizations_count = organizations_count.sort_by{ |k, v| v }.reverse.to_h if search_orgs

# puts sorted_countries_count if search_countries
# puts sorted_organizations_count if search_orgs

csv_output = CSV.open(output_file, "ab")
csv_output << []

csv_output << ["Totals",total_pubs]
if search_countries
  csv_output << sorted_countries_count.map { |key,value| key }
  csv_output << sorted_countries_count.map { |key,value| value }
end
if search_orgs
  csv_output << sorted_organizations_count.map { |key,value| key }
  csv_output << sorted_organizations_count.map { |key,value| value }
end

csv_output.close
