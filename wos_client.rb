require 'faraday'
require 'nokogiri'
# class to connect to WoS client and return results

class WosClient

  def initialize(wos_auth_code:, max_records: 100)
    @wos_auth_code = wos_auth_code
    @max_records = max_records # this is the maximum number that can be returned in single query by WoS
    authenticate
  end

  def web_of_science_conn
    @conn ||= Faraday.new(:url => 'http://search.webofknowledge.com')
  end

  def authenticate
    body = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:auth="http://auth.cxf.wokmws.thomsonreuters.com"><soapenv:Header/><soapenv:Body><auth:authenticate/></soapenv:Body></soapenv:Envelope>'
    auth = web_of_science_conn.post do |req|
         req.url '/esti/wokmws/ws/WOKMWSAuthenticate'
         req.headers['Content-Type'] = 'application/xml'
         req.headers['Authorization'] = "Basic #{@wos_auth_code}"
         req.body = body
    end
    auth_xml_doc  = Nokogiri::XML(auth.body).remove_namespaces!
    raise 'WoS authentication failed' if auth_xml_doc.xpath('//authenticateResponse//return').size == 0
    @sid = auth_xml_doc.xpath('//authenticateResponse//return')[0].content
  end

  def query_id(result_xml_doc)
    query_id_node = result_xml_doc.at_xpath('//queryId')
    query_id_node.nil? ? "" : query_id_node.content
  end

  def num_records(result_xml_doc)
    num_records_node = result_xml_doc.at_xpath('//recordsFound')
    num_records_node.nil? ? 0 : num_records_node.content.to_i
  end

  def run_search(body)
    begin
      response = web_of_science_conn.post do |req|
         req.url '/esti/wokmws/ws/WokSearch'
         req.headers['Content-Type'] = 'application/xml'
         req.headers['Cookie'] = "SID=\"#{@sid}\""
         req.body = body
      end
      Nokogiri::XML(response.body).remove_namespaces!
    rescue
      Nokogiri::XML("<xml/>")
    end
  end

  def year_search(year, institutions)
    body = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:woksearch=\"http://woksearch.v3.wokmws.thomsonreuters.com\"><soapenv:Header/><soapenv:Body><woksearch:search><queryParameters><databaseId>WOS</databaseId><userQuery>OG=(#{institutions.join(' OR ')}) AND PY=#{year}</userQuery><queryLanguage>en</queryLanguage></queryParameters><retrieveParameters><firstRecord>1</firstRecord><count>1</count><option><key>RecordIDs</key><value>On</value></option><option><key>targetNamespace</key><value>http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord</value></option></retrieveParameters></woksearch:search></soapenv:Body></soapenv:Envelope>"
    run_search(body)
  end

  def name_search(name, institutions, start_date, end_date)
    body = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:woksearch=\"http://woksearch.v3.wokmws.thomsonreuters.com\"><soapenv:Header/><soapenv:Body><woksearch:search><queryParameters><databaseId>WOS</databaseId><userQuery>AU=(#{name_query(name)}) AND OG=(#{institutions.join(' OR ')})</userQuery><timeSpan><begin>#{start_date}</begin><end>#{end_date}</end></timeSpan><queryLanguage>en</queryLanguage></queryParameters><retrieveParameters><firstRecord>1</firstRecord><count>#{@max_records}</count><option><key>RecordIDs</key><value>On</value></option><option><key>targetNamespace</key><value>http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord</value></option></retrieveParameters></woksearch:search></soapenv:Body></soapenv:Envelope>"
    run_search(body)
  end

  def continue_search(query_id, next_record)
    body = "<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\"><soap:Body><ns2:retrieve xmlns:ns2=\"http://woksearch.v3.wokmws.thomsonreuters.com\"><queryId>#{query_id}</queryId><retrieveParameters><firstRecord>#{next_record}</firstRecord><count>#{@max_records}</count></retrieveParameters></ns2:retrieve></soap:Body></soap:Envelope>"
    run_search(body)
  end

  private

  def name_query(name)
    split_name=name.split(',')
    last_name = split_name[0]&.strip
    first_middle_name = split_name[1]&.strip
    if first_middle_name.size == 1
      name_query = "#{last_name} #{first_middle_name[0]} OR #{last_name} #{first_middle_name[0]}"
    else
      first_name = first_middle_name.split(' ')[0]&.strip
      middle_name = first_middle_name.split(' ')[1]&.strip
      name_query = "#{last_name} #{first_name} OR #{last_name} #{first_name[0]}"
      name_query += " OR #{last_name} #{first_name[0]}#{middle_name[0]} OR #{last_name} #{first_name} #{middle_name[0]}" unless middle_name.blank?
    end
    name_query
  end

end
