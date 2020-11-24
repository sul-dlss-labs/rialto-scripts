# Total Publication County By Year Report
# Count the total number of publications from Stanford by year
# Input is a list of faculty names in a csv file
# Output is list of publications by year, from the specified start year until the current year

# required gems:
# gem install 'csv'
# gem install 'faraday'
# gem install 'nokogiri'

# Set parameters below in the code, get the WOS_AUTH_CODE and pass in as an env variable,
#  create input CSV file and then run with
# WOS_AUTH_CODE=XXXX ruby totals_wos_search.rb

$stdout.sync = true # flush output immediately

# input file is CSV format with name in first column in "Last, First Middle" format all in a single column (all values surrouned by quotes).
#  the CSV file should include a header row as well, though the header names don't matter
#  extra columns are fine
# e.g.
# Names
# "Donald, Duck"
# "Dude, Somename L"

output_file='tmp/rialto_totals_by_year.csv'
start_year = 1970

institutions = ["Stanford University"] # restrict the publication search (searched by name) to just authors from these institutions -- could be an array of institutions
wos_auth_code = ENV['WOS_AUTH_CODE'] # the WOS authorization key (see shared_configs for sul_pub)

require 'rubygems'
# Set up gems listed in the Gemfile.
ENV['BUNDLE_GEMFILE'] ||= File.expand_path('../../Gemfile', __FILE__)

require 'bundler/setup' if File.exist?(ENV['BUNDLE_GEMFILE'])
require 'csv'
require 'faraday'
require 'nokogiri'

def web_of_science_conn
  @conn ||= Faraday.new(:url => 'http://search.webofknowledge.com')
end

def authenticate(wos_auth_code)
  body = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:auth="http://auth.cxf.wokmws.thomsonreuters.com"><soapenv:Header/><soapenv:Body><auth:authenticate/></soapenv:Body></soapenv:Envelope>'
  auth = web_of_science_conn.post do |req|
       req.url '/esti/wokmws/ws/WOKMWSAuthenticate'
       req.headers['Content-Type'] = 'application/xml'
       req.headers['Authorization'] = "Basic #{wos_auth_code}"
       req.body = body
  end
  auth_xml_doc  = Nokogiri::XML(auth.body).remove_namespaces!
  auth_xml_doc.xpath('//authenticateResponse//return')[0].content
end

def run_search(body,sid)
  begin
    response = web_of_science_conn.post do |req|
       req.url '/esti/wokmws/ws/WokSearch'
       req.headers['Content-Type'] = 'application/xml'
       req.headers['Cookie'] = "SID=\"#{sid}\""
       req.body = body
    end
    Nokogiri::XML(response.body).remove_namespaces!
  rescue
    Nokogiri::XML("<xml/>")
  end
end

def query_body(year,institutions)
  "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:woksearch=\"http://woksearch.v3.wokmws.thomsonreuters.com\"><soapenv:Header/><soapenv:Body><woksearch:search><queryParameters><databaseId>WOS</databaseId><userQuery>OG=(#{institutions.join(' OR ')}) AND PY=#{year}</userQuery><queryLanguage>en</queryLanguage></queryParameters><retrieveParameters><firstRecord>1</firstRecord><count>1</count><option><key>RecordIDs</key><value>On</value></option><option><key>targetNamespace</key><value>http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord</value></option></retrieveParameters></woksearch:search></soapenv:Body></soapenv:Envelope>"
end

sid = authenticate(wos_auth_code)

years_count = Hash.new(0)

total_pubs = 0
csv_output = CSV.open(output_file, "ab")
csv_output << ["Stanford University - Web of Science search by year"]
csv_output << ["Year","Total pubs"]
csv_output.close

for year in start_year..Time.now.year do

  csv_output = CSV.open(output_file, "ab")

  result_xml_doc = run_search(query_body(year,institutions),sid)
  query_id_node = result_xml_doc.at_xpath('//queryId')
  query_id = query_id_node.nil? ? "" : query_id_node.content
  num_records_node = result_xml_doc.at_xpath('//recordsFound')
  num_records = num_records_node.nil? ? 0 : num_records_node.content.to_i
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
