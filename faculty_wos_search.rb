# Faculty Collaboration Report

# Enumerate stanford faculty's collaborations by country and/or by institution
# Input is a list of faculty names in a csv file
# Output is co-authors by institution and/or country enumerated

# required gems:
# gem install 'csv'
# gem install 'faraday'
# gem install 'nokogiri'
# gem install 'activesupport'

# requires ruby 2.3 or better

# Set parameters below in the code, get the WOS_AUTH_CODE and pass in as an env variable,
#  create input CSV file and then run with
# WOS_AUTH_CODE=XXXX ruby faculty_wos_search.rb

# input file is CSV format with name in first column in "Last, First Middle" format all in a single column (all name values surrounded by quotes).
#  the CSV file should include a header row as well, though the header names don't matter
#  extra columns are fine
# e.g.
# Names
# "Donald, Duck"
# "Dude, Somename L"

$stdout.sync = true # flush output immediately
require 'csv'
require 'active_support/all'
require './wos_client'
require './faculty_wos_search_helper'

#### BEGIN PARAMETERS TO SET ####
input_file='tmp/rialto_sample.csv'
output_file='tmp/rialto_sample_results.csv'

start_date = "1970-01-01" # limit the start date when searching for publications, format: YYYY-MM-DD
end_date = Time.now.strftime("%Y-%m-%d") # the end date defaults to today

limit = nil # limit the number of people searched regardless of input size (useful for testing), set to nil for no limit
search_orgs = true # set to false to skip organization enumeration for faster results
# an array of organizations to restrict the collaboration enumeration to (set to nil to enumerate over all organizations if search_orgs is set to true)
restrict_to_organizations = nil # ['Stanford','Stanford University','UCSF','University of California San Francisco','UCSF School of Medicine','University of California, San Francisco','UCB','Berkeley','University of California Berkeley','UC Berkeley']
search_countries = true # set to false to skip country enumeration for faster results
institutions = ["Stanford University"] # restrict the publication search (searched by name) to just authors from these institutions -- could be an array of institutions
#### END PARAMETERS TO SET ####

puts "Reading #{input_file}"
names = []
CSV.foreach(input_file,:headers=>true) do |row|
  names << row[0]
end
puts "#{names.size} total names found"

names.uniq!
puts "#{names.size} total unique names found"

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

client = WosClient.new(wos_auth_code: ENV['WOS_AUTH_CODE'], max_records: max_records) # find the WOS authorization key in shared_configs for sul_pub

names.each_with_index do |name,index|
  next if name.blank?

  csv_output = CSV.open(output_file, "ab")

  puts "#{index+1} of #{total_names}: searching on #{name}"
  author_countries_count[name] = Hash.new(0)
  author_organizations_count[name] = Hash.new(0)
  num_retrieved = 0
  num_runs = 0
  result_xml_doc = client.name_search(name, institutions, start_date, end_date)
  num_records = client.num_records(result_xml_doc)
  query_id = client.query_id(result_xml_doc)

  puts "...found #{num_records} pubs"

  if num_records > 0
    num_pubs = enumerate_results(result_xml_doc,countries_count,author_countries_count[name],organizations_count,author_organizations_count[name],search_countries,search_orgs,restrict_to_organizations)
    num_retrieved += num_pubs
    while (num_retrieved < num_records && num_pubs != 0 && num_runs < max_runs_per_person) do # we have more to go
      next_record = num_retrieved + 1
      puts "..... fetching next batch starting at #{next_record}"
      result_xml_doc = client.continue_search(query_id, next_record)
      num_pubs = enumerate_results(result_xml_doc,countries_count,author_countries_count[name],organizations_count,author_organizations_count[name],search_countries,search_orgs,restrict_to_organizations)
      num_retrieved += num_pubs
      num_runs+=1
    end
  end

  puts author_countries_count[name] if search_countries
  puts author_organizations_count[name] if search_orgs

  puts
  total_pubs += num_records

  csv_output << []
  csv_output << [name,num_records]
  sorted_author_countries_count = author_countries_count[name].sort_by{ |k, v| v }.reverse.to_h
  sorted_author_organizations_count = author_organizations_count[name].sort_by{ |k, v| v }.reverse.to_h
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

puts sorted_countries_count if search_countries
puts sorted_organizations_count if search_orgs

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
