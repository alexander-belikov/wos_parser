from re import compile, sub
import xml.etree.cElementTree as cET
from .xml_consts import id_path
from .xml_consts import add_spec_path, \
    full_address_path, country_path, city_path, \
    state_path, zipcode_path, street_path, org_path, \
    add_no_key

from .xml_consts import suborg_path

from .xml_consts import pubinfo_path
from .xml_consts import add_path

from .xml_consts import names_path, name_path, display_name_path, \
    email_path, lastname_path, firstname_path, wos_standard_path

from .xml_consts import seq_no_key

from .xml_consts import references_path, reference_path, \
    uid_path, year_path, ref_page_path, cited_author_path, cited_work_path, \
    cited_title_path, volume_path, doi_path

from .xml_consts import keywords_path, keyword_path, keywordsplus_path
from .xml_consts import headings_path, heading_path
from .xml_consts import subheadings_path, subheading_path
from .xml_consts import subjects_path, subject_path

from .xml_consts import doctype_path, doctypes_path
from .xml_consts import identifiers_path, identifier_path
from .xml_consts import titles_path, title_path
from .xml_consts import languages_path, language_path
from .xml_consts import abstracts_path, abstract_path, abstract_paragraph_path
from .xml_consts import grants_path, grant_path, grant_agency_path
from .xml_consts import grant_ids_path, grant_id_path
from .xml_consts import ewuid_path, edition_path

from .xml_consts import fundtext_path, fundtext_paragraph_path

from .xml_consts import conferences_path, conference_path
from .xml_consts import conf_location_path, conf_date_path
from .xml_consts import conf_sponsor_path, conf_title_path, conf_info_path
from .xml_consts import conf_city, conf_state, conf_host

from .xml_consts import conf_id_key
from .xml_consts import publishers_path, publisher_path
from .xml_consts import publisher_name_path, publisher_address_spec_path
from .xml_consts import publisher_city_path, publisher_full_address_path
from .xml_consts import role_key
from .xml_consts import page_path, begin_key, end_key, pagecount_key

from .xml_consts import len_wosid

from datetime import datetime
from hashlib import sha1

import logging
from itertools import filterfalse


def kill_trivial_namespace(s):
    pat = r'xmlns=\".*[^\"]\"(?=>)'
    p = compile(pat)
    m = p.search(s)
    positions = m.span()
    subst = ' '*(positions[1] - positions[0])
    rline = p.sub(subst, s, count=1)
    return rline


# TODO : is it possible to modify gz on the fly?
def xml_remove_trivial_namespace(source):
    if not hasattr(source, "read"):
        source = open(source, "r+")
    try:
        offsets = []
        while True:
            # logging.warning(' before next')
            line = next(source)
            # logging.warning(' after next')
            offsets.append(len(line))
            if 'xmlns=' in line:
                break
        nline = kill_trivial_namespace(line)
        # logging.warning(' after nline')
        source.seek(sum(offsets[:-1]))
        # logging.warning(' after seek')
        source.write(nline)
    except:
        logging.error(' in xml_remove_trivial_namespace() : '
                      'failed to modify the file')


def etree_to_dict(t):
    # based on http://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
    children = t.getchildren()
    if children:
        d = {t.tag: list(map(etree_to_dict, t.getchildren()))}
    else:
        d = {t.tag: t.text}
    d.update((k, v) for k, v in t.attrib.items())
    return d


def parse_id(branch):
    """

    :param branch:
    :return:


    required:
        id : str

    optional:
        None
    """
    success = True

    try:
        id_ = branch.find(id_path)

        try:
            value = id_.text
        except:
            logging.error(' parse_id() : in branch {0} '
                          'UID could not be parsed'.format(id_path))
            raise
    except:
        success = False
        value = etree_to_dict(branch)
    return success, value


def prune_branch(pub, branch_path, leaf_path, parse_func, filter_false=False):

    branch = pub.find(branch_path)
    if branch:
        leaves = branch.findall(leaf_path)
        parsed_leaves = list(map(parse_func, leaves))

        if filter_false:
            left_out = list(map(lambda x: x[1], filter(lambda x: not x[0], parsed_leaves)))
            if len(left_out) > 0:
                logging.info(' prune_branch() : in branch {0} {1} leaf(ves) were '
                              'filtered out.'.format(branch_path, len(left_out)))
            parsed_leaves = list(filter(lambda x: x[0], parsed_leaves))

        success = all(list(map(lambda x: x[0], parsed_leaves)))
        jsonic_leaves = list(map(lambda x: x[1], parsed_leaves))
        if not success:
            # keys might be the same
            jsonic_leaves = [etree_to_dict(branch)]
            logging.info(' prune_branch() : parse failed in branch {0} with value {1} '
                          .format(branch_path, jsonic_leaves))
    else:
        success = False
        jsonic_leaves = []
        logging.info(' prune_branch() : empty branch parse: failed in branch {0} with value {1}'
                     .format(branch_path, jsonic_leaves))

    return success, jsonic_leaves


def add_entry(input_dict, branch, entry_path, force_type=None, relaxed_type=False,
              name_suffix=None):
    elem = branch.find(entry_path)
    update_dict = {}

    try:
        value = elem.text
        if force_type:
            try:
                value = force_type(value)
            except:
                if not relaxed_type:
                    value = None
    except:
        value = None
    if name_suffix:
        name = entry_path + name_suffix
    else:
        name = entry_path

    update_dict.update({name: value})
    input_dict.update(update_dict)


def parse_address(branch):
    """
    expected address structure:

    required:
        organization : str
        add_no : int

    optional:
        full_address : str
        organization synonyms : list of str
        country : str
        city : str
        state : str
        zipcode : str
        street : str
    """
    success = True

    try:
        org_names = branch.findall(org_path)

        def condition(x):
            return x.attrib and 'pref' in x.attrib and x.attrib['pref'] == 'Y'

        # find first org with pref='Y'
        orgs_pref = list(filter(condition, org_names))
        orgs_pref = list(map(lambda x: x.text, filterfalse(lambda x: x is None, orgs_pref)))
        result_dict = {'organizations_pref': orgs_pref}

        orgs_rest = list(filterfalse(condition, org_names))
        orgs_rest = list(map(lambda x: x.text, filterfalse(lambda x: x is None, orgs_rest)))
        result_dict.update({'organizations': orgs_rest})

        suborg_names = branch.findall(suborg_path)
        suborgs = list(map(lambda x: x.text, filterfalse(lambda y: y is None, suborg_names)))
        result_dict.update({'suborganizations': suborgs})

        if branch.attrib:
            if add_no_key in branch.attrib:
                # TODO add try-catch-raise with logging
                # if not int-able : exception triggered
                addr_number = int(branch.attrib[add_no_key])
                result_dict.update({add_no_key: addr_number})
        else:
            result_dict.update({add_no_key: 1})

        # entries below are optional
        add_entry(result_dict, branch, full_address_path)
        add_entry(result_dict, branch, country_path)
        add_entry(result_dict, branch, city_path)
        add_entry(result_dict, branch, state_path)
        add_entry(result_dict, branch, zipcode_path)
        add_entry(result_dict, branch, street_path)

    except:
        success = False
        result_dict = etree_to_dict(branch)
    return success, result_dict


def parse_name(branch):
    #TODO clean up comment
    """
    expected name structure:

    required:
        display_name : str
        add_no : int (if more than one address)
        seq_no : int

    optional:
        wos_standard: str
        name : str
        lastname : str
        firstname : str
        email : str
        attribs : ('dais_id', 'role', 'seq_no')
    """
    success = True

    try:
        result_dict = {}

        # possible exception if //name is not available
        try:
            display_name = branch.find(display_name_path)
            result_dict.update({display_name_path: display_name.text})
        except:
            logging.error(' parse_name() : display_name not found:')
            logging.error(etree_to_dict(branch))
            raise

        # entries below are optional
        add_entry(result_dict, branch, wos_standard_path)
        add_entry(result_dict, branch, name_path)
        add_entry(result_dict, branch, lastname_path)
        add_entry(result_dict, branch, firstname_path)
        add_entry(result_dict, branch, email_path)

        result_dict.update((k, v) for k, v in branch.attrib.items())
        if add_no_key not in result_dict.keys():
            result_dict[add_no_key] = [0]
        else:
            try:
                add_no_str = result_dict[add_no_key].split(' ')
                # add_no_int = filter(lambda x: is_int(x), add_no_str)
                result_dict[add_no_key] = list(map(lambda x: int(x), add_no_str))
            except:
                logging.error(' parse_name() : address numbers string parsing failure:')
                logging.error(etree_to_dict(branch))

        if seq_no_key not in result_dict.keys():
            result_dict[add_no_key] = 0
        else:
            try:
                result_dict[seq_no_key] = int(result_dict[seq_no_key])
            except:
                logging.error(' parse_name() : sequence number could not be extracted :')
                logging.error(etree_to_dict(branch))
    except:
        success = False
        result_dict = etree_to_dict(branch)
    return success, result_dict


def parse_page(branch, path):
    """

    :param branch:
    :param path:
    :return: dict with keys
        required:
            page_count : int

        optional:
            end: str
            begin: str
            range: str
                NB range can be X123-X125, or 123A-125A
                so it might be used when
                page_count can not be cast to float
    """

    success = True
    result_dict = {k: None for k in [pagecount_key, begin_key, end_key, 'range']}
    try:
        entry = branch.find(path)
        pp = entry.text
        attrib_dict = entry.attrib
        result_dict.update(attrib_dict)
        result_dict['range'] = pp
        try:
            result_dict[pagecount_key] = int(result_dict[pagecount_key])
        except:
            try:
                delta = int(result_dict[end_key]) - int(result_dict[begin_key]) + 1
                if delta < 1:
                    logging.error(' parse_page() : page_count value below 1')
                    raise ValueError('failed to cast to int parsed page_count')
                result_dict[pagecount_key] = delta
            except:
                try:
                    pps = pp.split('-')
                    ipps = list(map(int, map(lambda x: sub(r'\D', '', x), pps)))
                    delta = (ipps[1] - ipps[0]) + 1
                    if delta < 1:
                        logging.error(' parse_page() : page_count value below 1')
                        raise ValueError('failed to cast to int parsed page_count')
                    result_dict[pagecount_key] = delta
                except:
                    logging.error(' parse_page() : failed to integerize page count field')
                    raise TypeError('failed to cast to int parsed page_count')
    except:
        success = False
        logging.error(' parse_page() : could not capture page')
    return success, result_dict


def parse_reference(branch):
    """
    expected reference structure:

    required:
        uid : str prefix = {'', 'wos', 'medline', 'insprec', 'zoorec' ...}

    optional:
        year : int
        page : int
        cited_author : str
        cited_work : str
        cited_title : str
        volume : str
        doi : str
    """
    success = True
    try:
        result_dict = {}
        add_entry(result_dict, branch, year_path, int)
        add_entry(result_dict, branch, year_path, name_suffix='_str')
        add_entry(result_dict, branch, volume_path, int)
        add_entry(result_dict, branch, volume_path, name_suffix='_str')
        add_entry(result_dict, branch, ref_page_path, int)
        add_entry(result_dict, branch, ref_page_path, name_suffix='_str')
        add_entry(result_dict, branch, doi_path)
        add_entry(result_dict, branch, cited_author_path)
        add_entry(result_dict, branch, cited_title_path)
        add_entry(result_dict, branch, cited_work_path)

        try:
            uid = branch.find(uid_path)
            uid_value = uid.text
        except:
            logging.error(' parse_reference() : uid field absent:')
            if result_dict[doi_path]:
                value = result_dict[doi_path]
                value = sha1(value.encode('utf-8')).hexdigest()
                uid_value = 'DOI:{0}'.format(value)[:len_wosid]
                logging.error(' parse_reference() : adding DOI id : {0}'.format(uid_value))
                logging.error(' parse_reference() : ref content {0}'.format(result_dict))
            elif result_dict[cited_title_path]:
                value = sha1(result_dict[cited_title_path].encode('utf-8')).hexdigest()
                uid_value = 'ROG:{0}'.format(value)[:len_wosid]
                logging.error(' parse_reference() : adding ROG id title : {0}'.format(uid_value))
                logging.error(' parse_reference() : ref content {0}'.format(result_dict))
            elif result_dict[cited_author_path] \
                    and result_dict[year_path + '_str'] \
                    and result_dict[cited_work_path]:
                str_combo = ' '.join([result_dict[cited_author_path],
                                      result_dict[year_path + '_str'], result_dict[cited_work_path]])
                value = sha1(str_combo.encode('utf-8')).hexdigest()
                uid_value = 'ROG:{0}'.format(value)[:len_wosid]
                logging.error(' parse_reference() : adding ROG id author year cited: {0}'.format(uid_value))
                logging.error(' parse_reference() : ref content {0}'.format(result_dict))
            else:
                logging.error(' parse_reference() : uid assignment failed')
                raise

        result_dict.update({uid_path: uid_value})
    except:
        success = False
        result_dict = etree_to_dict(branch)
        if not result_dict['reference']:
            logging.error(' parse_reference() : empty reference')
        else:
            logging.error(' parse_reference() : corrupt reference : {0}'.format(result_dict))
    return success, result_dict


##  modified to add vol,issue, has_abstract information
def parse_vol_issue_has_abs(branch, global_year, path = pubinfo_path):
    
    success = True
    
    try:
        attrib_dict = branch.find(path).attrib

        result_dict = {'vol':attrib_dict.get('vol', None)}
        result_dict.update({'issue':attrib_dict.get('issue', None)})
        result_dict.update({'has_abstract':attrib_dict.get('has_abstract', None)})
        
    
    except:
        logging.error(' parse_vol_issue() : could not capture vol or issue')
        success = False
        result_dict = {}
    return success, result_dict


def parse_date(branch, global_year, path=pubinfo_path):
    """
    expected reference structure:

    required:
        year : int
    optional:
        month : int
        day : int
    """

    success = True

    try:
        attrib_dict = branch.find(path).attrib
        year = extract_year(attrib_dict, global_year)
        date_dict = {'year': year}
        try:
            month = extract_month(attrib_dict)
            date_dict.update({'month': month})
        except:
            logging.error(' parse_date() : could not capture month')
        try:
            day = extract_day(attrib_dict)
            date_dict.update({'day': day})
        except:
            logging.error(' parse_date() : could not capture day')

        date_dict = {k: v[1] for k, v in date_dict.items() if v[0]}
    except:
        logging.error(' parse_date() : could not capture year')
        success = False
        date_dict = {}
    return success, date_dict


def extract_year(date_info_dict, global_year):
    years = {}
    sd = 'sortdate'
    py = 'pubyear'
    gl = 'globalyear'
    success = True
    year = -1

    if sd in date_info_dict.keys():
        sortdate = date_info_dict[sd]
        try:
            date = datetime.strptime(sortdate, '%Y-%m-%d')
            years[sd] = date.year
        except:
            logging.error(' extract_year() : sortdate format corrupt: {0}'.format(sortdate))

    elif py in date_info_dict.keys():
        pubyear = date_info_dict[py]
        try:
            years[py] = int(pubyear)
        except:
            logging.error(' extract_year() : pubyear format corrupt: {0}'.format(pubyear))
    else:
        years[gl] = global_year

    if sd in years.keys():
        year = years[sd]
    elif py in years.keys():
        year = years[py]
    elif gl in years.keys():
        year = years[gl]
    else:
        success = False

    return success, year

#TODO deal with -1 and success redundancy
#TODO plug in names of the functions in logging
#TODO check for other date fields (live cover date)


def extract_month(info_dict):
    months = {}
    sd = 'sortdate'
    pm = 'pubmonth'
    success = True
    month = -1
    seasons = {'WIN': 1, 'SPR': 3, 'SUM': 6, 'FAL': 9}

    if sd in info_dict.keys():
        sortdate = info_dict[sd]
        try:
            date = datetime.strptime(sortdate, '%Y-%m-%d')
            months[sd] = date.month
        except:
            logging.error(' extract_month() : sortdate format '
                          'corrupt: {0}'.format(sortdate))
    elif pm in info_dict.keys():
        month_letter = info_dict[pm][:3]
        try:
            date = datetime.strptime(month_letter, '%b')
            months['pubmonth'] = date.month
        except:
            if month_letter in seasons.keys():
                months['pubmonth'] = date.month
            else:
                logging.error(' extract_month() : pubmonth format '
                              'corrupt: {0}'.format(month_letter))
                raise ValueError(' extract_month() : pubmonth format '
                                 'corrupt: {0}'.format(month_letter))

    if sd in months.keys():
        month = months[sd]
    elif pm in months.keys():
        month = months[pm]
    else:
        success = False
    return success, month


def extract_day(info_dict):

    days = {}
    sd = 'sortdate'
    pm = 'pubmonth'
    success = True
    day = -1

    if sd in info_dict.keys():
        sortdate = info_dict[sd]
        try:
            date = datetime.strptime(sortdate, '%Y-%m-%d')
            days[sd] = date.day
        except:
            logging.error(' extract_day() : sortdate format '
                          'corrupt: {0}'.format(sortdate))
    elif pm in info_dict.keys():
        month_letter = info_dict[pm]
        try:
            if ' ' in month_letter:
                date = datetime.strptime(month_letter, '%b %d')
                days['pubmonth'] = date.day
        except:
            logging.error(' extract_day() : could not extract day '
                          'from pubmonth {0}'.format(month_letter))

    if sd in days.keys():
        day = days[sd]
    elif pm in days.keys():
        day = days[pm]
    else:
        success = False
        logging.error(' extract_day() : day extraction failure')

    return success, day


def parse_pubtype(branch):
    """

    required:
        pubtype : str
    optional:
    """
    success = True
    try:
        try:
            pubinfo = branch.find(pubinfo_path)
            result_dict = {'pubtype': pubinfo.attrib['pubtype']}
        except:
            logging.error(' parse_pubtype() : pubtype absent '
                          'down path {0}'.format(pubinfo_path))
            raise
    except:
        success = False
        result_dict = {'pubtype': None}
    return success, result_dict


def parse_abstract(branch):

    success = True
    try:
        paragraphs_ = branch.findall(abstract_paragraph_path)
        paragraphs = map(lambda x: x.text, paragraphs_)
        value = ' '.join(paragraphs)
    except:
        success = False
        value = etree_to_dict(branch)
    return success, value


def parse_fundtext(pub):
    """

    required:
        pubtype : str
    optional:
    """
    success = True
    try:
        branch = pub.find(fundtext_path)
        paragraphs_ = branch.findall(fundtext_paragraph_path)
        paragraphs = map(lambda x: x.text, paragraphs_)
        # if paragraphs:
        value = ' '.join(paragraphs)
    except:
        logging.info(' parse_fundtext() : fundtext absent '
                     'in path {0}'.format(pubinfo_path))
        success = False
        value = None
    return success, value


def parse_publisher(branch):
    """

    required:
        pubtype : str
    optional:
    """

    success = True
    result_dict = {}

    try:
        addr_specs = branch.findall(publisher_address_spec_path)
        acc_a = []
        for ads in addr_specs:
            subdict_a = {}
            if ads.attrib and add_no_key in ads.attrib.keys() \
                    and is_int(ads.attrib[add_no_key]):
                add_no = int(ads.attrib[add_no_key])
            else:
                add_no = 0

            full_addr = ads.find(publisher_full_address_path).text
            city = ads.find(publisher_city_path).text
            subdict_a.update({add_no_key: add_no})
            subdict_a.update({'city': city, 'address': full_addr})
            acc_a.append(subdict_a)

        names = branch.findall(publisher_name_path)
        acc_n = []
        for n in names:
            subdict_n = {}
            if n.attrib:
                if add_no_key not in n.attrib.keys():
                    subdict_n[add_no_key] = [0]
                else:
                    try:
                        add_no_str = n.attrib[add_no_key].split(' ')
                        subdict_n[add_no_key] = list(map(lambda x: int(x), add_no_str))
                    except:
                        logging.error(' parse_publisher() : address numbers string parsing failure :')
                        logging.error(etree_to_dict(branch))
                if seq_no_key not in n.attrib.keys():
                    subdict_n[add_no_key] = 0
                else:
                    try:
                        subdict_n[seq_no_key] = int(n.attrib[seq_no_key])
                    except:
                        logging.error(' parse_publisher() : sequence number could not be extracted :')
                        logging.error(etree_to_dict(branch))

                if role_key not in n.attrib.keys():
                    subdict_n[role_key] = None
                else:
                    subdict_n[role_key] = n.attrib[role_key]
                acc_n.append(subdict_n)

            # we skip fullname
            name = n.find(display_name_path)
            subdict_n[display_name_path] = name.text
        result_dict['addresses'] = acc_a
        result_dict['names'] = acc_n
    except:
        logging.info(' parse_publisher() : ')
        success = False
        result_dict = etree_to_dict(branch)
    return success, result_dict


def parse_conference(branch):
    """

    required:
        pubtype : str
    optional:
    """

    success = True
    result_dict = {}

    try:
        if conf_id_key in branch.attrib.keys():
            if is_int(branch.attrib[conf_id_key]):
                result_dict.update({conf_id_key: int(branch.attrib[conf_id_key])})
            else:
                result_dict.update({conf_id_key: None})

            result_dict.update({'{0}_str'.format(conf_id_key): branch.attrib[conf_id_key]})

        dates = branch.findall(conf_date_path)
        acc_dates = []

        for d in dates:
            dates_dict = {'dates_str': d.text}
            # 'conf_start' 'conf_end' keys
            dates_dict.update(d.attrib)
            acc_dates.append(dates_dict)
        result_dict['dates'] = acc_dates

        locations = branch.findall(conf_location_path)
        acc_locations = []
        for l in locations:
            city = l.find(conf_city)
            state = l.find(conf_state)
            host = l.find(conf_host)
            dd = {'conf_city': None if city is None else city.text,
                  'conf_state': None if state is None else state.text,
                  'conf_host': None if host is None else host.text}
            acc_locations.append(dd)
        result_dict['locations'] = acc_locations

        titles = branch.findall(conf_title_path)
        acc_titles = []
        for t in titles:
            acc_titles.append(t.text)
        result_dict['titles'] = acc_titles

        sponsors = branch.findall(conf_sponsor_path)
        acc_sponsors = []

        for s in sponsors:
            acc_sponsors.append(s.text)
        result_dict['sponsors'] = acc_sponsors

        infos = branch.findall(conf_info_path)
        acc_infos = []
        for i in infos:
            acc_infos.append(i.text)

        result_dict['infos'] = acc_infos
    except:
        logging.error(' parse_conference() : fail')
        success = False
        result_dict = etree_to_dict(branch)
    return success, result_dict


def parse_grant(branch):
    """

    required:
        pubtype : str
    optional:
    """

    success = True
    result_dict = {}
    try:
        agency = branch.find(grant_agency_path).text
        grant_ids = prune_branch(branch, grant_ids_path,
                                 grant_id_path, parse_generic, filter_false=True)
        result_dict.update({agency: grant_ids})
    except:
        logging.info(' parse_grant() : No text attr '
                     'for grant_agency_path field')
        success = False
        result_dict = etree_to_dict(branch)
    return success, result_dict


def parse_doctype(branch):
    """

    required:
        pubtype : str
    optional:
    """

    success = True
    try:
        value = branch.text
    except:
        logging.error(' parse_doctype() : No text attr '
                      'for doctype field')
        success = False
        value = etree_to_dict(branch)
    return success, value


def parse_language(branch):
    """

    required:
        language : str
    optional:
    """

    success = True
    try:
        value = {'value': branch.text}
        if branch.attrib:
            value.update(branch.attrib)
    except:
        logging.info(' parse_language() : No text attr '
                      'for language field')
        success = False
        value = etree_to_dict(branch)
    return success, value


def parse_generic(branch):
    """

    required:
        keyword : str
    optional:
    """

    success = True
    try:
        value = branch.text
    except:
        logging.info(' parse_generic() : No text attr for keyword field')
        success = False
        value = None
    return success, value


def parse_edition(branch):
    """

    required:
        pub_edition : str
    optional:
    """

    success = True
    value = None
    try:
        value = branch.attrib['value']
    except:
        logging.info(' parse_edition() : No value in attrib dict '
                     'for grant_agency_path field')
        success = False
        value = etree_to_dict(branch)
    return success, value


def parse_title(branch):
    """

    required:
        title : str
    optional:
    """

    success = True
    try:
        value = {'value': branch.text}
        if branch.attrib:
            value.update(branch.attrib)
    except:
        logging.warning(' parse_title() : No text attr '
                        'for title field')
        success = False
        value = etree_to_dict(branch)
    return success, value


def parse_identifier(branch):
    """

    required:
        identifier type : str
        identifier value : str
    optional:
    """
    success = True
    try:
        dd = branch.attrib
        result_pair = [(dd['type'], dd['value'])]
        if result_pair[0][0] == 'issn':
            # issn2int triggers an exception issn_str is not r'^\d{4}-\d{3}[\dxX]$'
            issn_int = issn2int(result_pair[0][1])
            result_pair.append(('issn_int', issn_int))
    except:
        result_pair = etree_to_dict(branch)
        logging.error(' parse_identifier() : identifier attrib '
                      'parse failed : {0}'.format(result_pair))
        success = False
    return success, result_pair


def process_languages(languages):
    result_dict = {}

    languages_list = list(map(lambda x: x['value'], languages[1]))
    primary_language = list(map(lambda y: y['value'],
                                filter(lambda x: 'type' in x.keys() and
                                                 x['type'] == 'primary', languages[1])))
    # populate languages with a list
    result_dict['languages'] = languages_list

    # populate primary_language with a primary language
    # if not available, the first available
    if primary_language:
        result_dict['primary_language'] = primary_language[0]
    elif languages_list:
        result_dict['primary_language'] = languages_list[0]

    return result_dict


def process_titles(titles):

    result_dict = {}

    item_title = list(map(lambda y: y['value'],
                          filter(lambda x: 'type' in x.keys() and
                                           x['type'] == 'item', titles[1])))
    source_title = list(map(lambda y: y['value'],
                            filter(lambda x: 'type' in x.keys() and
                                             x['type'] == 'source', titles[1])))
    if item_title:
        result_dict['item_title'] = item_title[0]
    else:
        result_dict['item_title'] = None
    if source_title:
        result_dict['source_title'] = source_title[0]
    else:
        result_dict['source_title'] = None

    return result_dict


def parse_record(pub, global_year):
    """
    top level parsing function
    :param pub: element corresponding to a publication
    :param global_year:
    :return: dict corresponding to a publication
    """

    wosid = parse_id(pub)
    pubdate = parse_date(pub, global_year)
    authors = prune_branch(pub, names_path, name_path, parse_name)
    pubtype = parse_pubtype(pub)
    idents = prune_branch(pub, identifiers_path, identifier_path,
                          parse_identifier)
    
    #add vol, issue, has_abstract information
    vol_issue_has_abs = parse_vol_issue_has_abs(pub, pubinfo_path)

    success = all(map(lambda y: y[0], [wosid, pubdate,
                                       authors, pubtype, idents,vol_issue_has_abs]))
    if success:
        addresses = prune_branch(pub, add_path, add_spec_path, parse_address)

        references = prune_branch(pub, references_path, reference_path,
                                  parse_reference, filter_false=True)

        doctypes = prune_branch(pub, doctypes_path, doctype_path,
                                parse_doctype, filter_false=True)

        languages = prune_branch(pub, languages_path, language_path,
                                 parse_language, filter_false=True)
        language_dict = process_languages(languages)

        titles = prune_branch(pub, titles_path, title_path,
                              parse_title, filter_false=True)
        titles_dict = process_titles(titles)

        keywords = prune_branch(pub, keywords_path, keyword_path,
                                parse_generic, filter_false=True)

        kws_plus = prune_branch(pub, keywordsplus_path, keyword_path,
                                parse_generic, filter_false=True)

        headings = prune_branch(pub, headings_path, heading_path,
                                parse_generic, filter_false=True)

        subheadings = prune_branch(pub, subheadings_path, subheading_path,
                                   parse_generic, filter_false=True)

        subjects = prune_branch(pub, subjects_path, subject_path,
                                parse_generic, filter_false=True)

        abstracts = prune_branch(pub, abstracts_path, abstract_path,
                                 parse_abstract, filter_false=True)

        grant_agencies = prune_branch(pub, grants_path, grant_path,
                                      parse_grant, filter_false=True)

        publishers = prune_branch(pub, publishers_path, publisher_path,
                                  parse_publisher, filter_false=True)

        conferences = prune_branch(pub, conferences_path, conference_path,
                                   parse_conference, filter_false=True)

        editions = prune_branch(pub, ewuid_path, edition_path, parse_edition)

        fund_text = parse_fundtext(pub)

        page_dict = parse_page(pub, page_path)

        idents_flat = [item for sublist in idents[1] for item in sublist]

        prop_dict = {x: y for x, y in idents_flat}

        ## add vlo, issue, and has_abstract information
        prop_dict.update({'vol':vol_issue_has_abs[1].get('vol',None)})
        prop_dict.update({'issue':vol_issue_has_abs[1].get('issue',None)})
        prop_dict.update({'has_abstract':vol_issue_has_abs[1].get('has_abstract',None)})

        prop_dict.update(pubtype[1])
        prop_dict.update(language_dict)
        prop_dict.update(titles_dict)
        prop_dict.update({'doctype': doctypes[1]})
        prop_dict.update({'keywords': keywords[1]})
        prop_dict.update({'keywords_plus': kws_plus[1]})
        prop_dict.update({'headings': headings[1]})
        prop_dict.update({'subheadings': subheadings[1]})
        prop_dict.update({'subjects': list(set(subjects[1]))})
        prop_dict.update({'abstracts': abstracts[1]})
        prop_dict.update({'grant_agencies': grant_agencies[1]})
        prop_dict.update({'fund_text': fund_text[1]})
        prop_dict.update({'conferences': conferences[1]})
        prop_dict.update({'page_info': page_dict[1]})
        prop_dict.update({'editions': editions[1]})

        record_dict = {
            'id': wosid[1],
            'date': pubdate[1],
            'addresses': addresses[1],
            'authors': authors[1],
            'references': references[1],
            'publishers': publishers[1],
            'properties': prop_dict,
        }

    else:
        record_dict = etree_to_dict(pub)
        record_dict.update({'id': wosid[1]})
    return success, record_dict


def parse_wos_xml(fp, global_year, good_cf, bad_cf, ntest=None):
    """
    driver func, parse file fp, push good and bad records
    accordingly to good_cf and bad_cf

    :param fp: filepointer to be parsed
    :param global_year: apriori known year
    :param good_cf: chunk flusher of good records
    :param bad_cf: chunk flusher of bad records
    :param ntest: number of records for test mode
    :return:
    """
    events = ('start', 'end')
    tree = cET.iterparse(fp, events)
    context = iter(tree)
    event, root = next(context)
    rec_ = 'REC'
    it = 0

    for event, pub in context:
        if event == "end" and pub.tag == rec_:
            ans = parse_record(pub, global_year)
            if ans[0]:
                good_cf.push(ans[1])
            else:
                msg = ' parse_wos_xml() : wos_id {0} failed ' \
                      'to parse, placed in the bad heap'.format(ans[1]['id'])
                logging.error(msg)
                bad_cf.push(ans[1])
            if not good_cf.ready() or not bad_cf.ready():
                break
            root.clear()
            it += 1
            if ntest and it >= ntest:
                break


def issn2int(issn_str):
    """
    reduce issn containing str to int
    and verify the check digit
    :param issn_str:
    :return: issn_int
    """

    pat = r'^\d{4}-\d{3}[\dxX]$'
    p = compile(pat)
    if p.match(issn_str):
        res = 0
        check = map(lambda x: int(x), issn_str[:4] + issn_str[5:8])
        check_bit = int(issn_str[-1]) if is_int(issn_str[-1]) else issn_str[-1]
        for pp in zip(check, range(8, 1, -1)):
            res += pp[0] * pp[1]

        rem = (11 - res) % 11
        rem = 'X' if rem == 10 else rem

        if rem == check_bit:
            return int(issn_str[0:4] + issn_str[5:8])
        else:
            logging.error(' issn2int() : in issn {0} '
                          'check bit is corrupt'.format(issn_str))
            logging.error(' equal to {0}, should be {1}'.format(check_bit, rem))
            # raise ValueError(' issn2int(): invalid check digit'.format(check_bit, rem))
            return int(issn_str[0:4] + issn_str[5:8])

    else:
        logging.error(' issn2int() : issn {0} : does not match '
                      'the pattern {1}'.format(issn_str, pat))

        raise ValueError(' issn2int(): invalid issn string')


def issnint2str(issn_int):
    """
    given issn int produce issn str
    :param issn_int:
    :return: issn_str
    """
    if type(issn_int) is not int:
        raise TypeError('issn_int is not int')
    issn_ = '{num:07d}'.format(num=issn_int)
    check = map(lambda x: int(x), issn_)
    res = 0
    for pp in zip(check, range(8, 1, -1)):
        res += pp[0] * pp[1]

    rem = (11 - res) % 11
    rem = 'X' if rem == 10 else rem
    issn_str = '{0}-{1}{2}'.format(issn_[:4], issn_[4:], rem)
    return issn_str


def is_int(x):
    try:
        int(x)
    except:
        return False
    return True


def fixtag(ns, tag, nsmap):
    # in case we have / every '/tag' -> '/key:tag'
    # ids = rel_ids.replace('/', '/{{{0}}}'.format(nsmap[key]))
    # or ids = rel_ids.replace('/', '/{0}:'.format(key))
    if ns in nsmap.keys():
        return '{' + nsmap[ns] + '}' + tag
    else:
        return tag
