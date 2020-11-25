# helper method used by the faculty_wos_search report

def enumerate_results(result_xml_doc,countries_count,author_countries_count,organizations_count,author_organizations_count,search_countries,search_orgs,restrict_to_organizations)
  begin

    puts "........collecting pubs"
    pubs = Nokogiri::XML(result_xml_doc.xpath("//records")[0].content).remove_namespaces!.xpath('//records/REC')

    if search_countries
      puts "........looking for countries"
      countries =  pubs.search('addresses//country').map {|address| address.content.titleize}
    end

    if search_orgs
      puts "........looking for organizations"
      organizations =  pubs.search("addresses//organization[@pref='Y']").map do |organization|
        org_name = organization.content
        unless restrict_to_organizations.blank?
          org_name if restrict_to_organizations.include?(org_name)
        else
          org_name
        end
      end
      organizations.reject!(&:blank?)
    end

    if search_countries
      puts "........enumerating countries"
      countries.each do |country|
        countries_count[country] += 1
        author_countries_count[country] += 1
      end
    end

    if search_orgs
      puts "........enumerating organizations"
      organizations.each do |organization|
        organizations_count[organization] += 1
        author_organizations_count[organization] += 1
      end
    end

    return pubs.size

  rescue
    return 0
  end

end
