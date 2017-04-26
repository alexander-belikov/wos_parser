# parse_id()
id_path = './UID'

# parse_address()
add_spec_path = './address_name/address_spec'
full_address_path = 'full_address'
country_path = 'country'
city_path = 'city'
state_path = 'state'
zipcode_path = 'zip'
street_path = 'street'
org_path = './organizations/organization'
suborg_path = './suborganizations/suborganization'
add_no_key = 'addr_no'
seq_no_key = 'seq_no'
role_key = 'role'
conf_id_key = 'conf_id'

# parse_name()
names_path = './static_data/summary/names'
name_path = 'name'
display_name_path = 'display_name'
email_path = 'email_addr'
lastname_path = 'last_name'
firstname_path = 'first_name'
wos_standard_path = 'wos_standard'

# parse_reference()
references_path = './static_data/fullrecord_metadata/references'
reference_path = 'reference'
uid_path = 'uid'
year_path = 'year'
ref_page_path = 'page'

cited_author_path = 'citedAuthor'
cited_title_path = 'citedTitle'
cited_work_path = 'citedWork'
volume_path = 'volume'
doi_path = 'doi'

# generic
pubinfo_path = './static_data/summary/pub_info'

# parse_page attribs
page_path = './static_data/summary/pub_info/page'
begin_key = 'begin'
end_key = 'end'
pagecount_key = 'page_count'

# parse_record()
add_path = './static_data/fullrecord_metadata/addresses'

# parse_identifier()
identifiers_path = 'dynamic_data/cluster_related/identifiers'
identifier_path = 'identifier'

# parse_doctype()
doctypes_path = './static_data/summary/doctypes'
doctype_path = 'doctype'

# parse_language()
languages_path = './static_data/fullrecord_metadata/languages'
language_path = 'language'

# parse_title()
titles_path = './static_data/summary/titles'
title_path = 'title'

# parse_keywords()
keywords_path = './static_data/fullrecord_metadata/keywords'
keyword_path = 'keyword'

# keywords_plus
keywordsplus_path = './static_data/item/keywords_plus'

# headings
headings_path = './static_data/fullrecord_metadata/category_info/headings'
heading_path = 'heading'

# subheadings
subheadings_path = './static_data/fullrecord_metadata/category_info/subheadings'
subheading_path = 'subheading'

# subjects
subjects_path = './static_data/fullrecord_metadata/category_info/subjects'
subject_path = 'subject'

# abstracts
abstracts_path = './static_data/fullrecord_metadata/abstracts'
abstract_path = 'abstract'
abstract_paragraph_path = './abstract_text/p'

# grants
grants_path = './static_data/fullrecord_metadata/fund_ack/grants'
grant_path = 'grant'
grant_agency_path = 'grant_agency'
grant_ids_path = 'grant_ids'
grant_id_path = 'grant_id'

# func text
fundtext_path = './static_data/fullrecord_metadata/fund_ack/fund_text'
fundtext_paragraph_path = 'p'

# conferences
conferences_path = './static_data/summary/conferences'
conference_path = 'conference'
conf_info_path = './conf_infos/conf_info'
conf_date_path = './conf_dates/conf_date'
conf_location_path = './conf_locations/conf_location'
conf_title_path = './conf_titles/conf_title'
conf_sponsor_path = './sponsors/sponsor'
conf_city = 'conf_city'
conf_state = 'conf_state'
conf_host = 'conf_host'

# editions
ewuid_path = './static_data/summary/EWUID'
edition_path = 'edition'

publishers_path = './static_data/summary/publishers'
publisher_path = './publisher'
publisher_address_spec_path = './address_spec'
publisher_full_address_path = 'full_address'
publisher_city_path = 'city'
publisher_name_path = './names/name'
# publisher_display_name == display_name_path
