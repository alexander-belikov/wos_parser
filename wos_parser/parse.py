from re import compile
import xml.etree.cElementTree as cET
from .xml_consts import id_path
from .xml_consts import add_spec_path, \
    full_address_path, country_path, city_path, \
    state_path, zipcode_path, street_path, org_path, \
    add_no_key

from .xml_consts import pubinfo_path
from .xml_consts import add_path

from .xml_consts import names_path, name_path, display_name_path, \
    email_path, lastname_path, firstname_path, wos_standard_path

from .xml_consts import seq_no

from .xml_consts import references_path, reference_path, \
    uid_path, year_path, page_path, cited_author_path, cited_work_path, \
    cited_title_path, volume_path, doi_path

from .xml_consts import keywords_path, keyword_path
from .xml_consts import headings_path, heading_path
from .xml_consts import subheadings_path, subheading_path
from .xml_consts import subjects_path, subject_path

from .xml_consts import doctype_path, doctypes_path
from .xml_consts import identifiers_path, identifier_path
from .xml_consts import titles_path, title_path
from .xml_consts import languages_path, language_path
from .xml_consts import abstracts_path, abstract_path, abstract_paragraph_path
from .xml_consts import grants_path, grant_path, grant_agency_path
from .xml_consts import fundtext_path, fundtext_paragraph_path

from datetime import datetime
from hashlib import sha1

import logging
from itertools import filterfalse

#TODO add conference fields


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
        jsonic_leaves = None
        logging.info(' prune_branch() : empty branch parse: failed in branch {0} with value {1}'
                     .format(branch_path, jsonic_leaves))

    return success, jsonic_leaves


def add_optional_entry(input_dict, branch, entry_path, force_type=None, relaxed_type=True,
                       name_suffix=None):
    elem = branch.find(entry_path)
    update_dict = {}

    if elem != None:
        if type:
            try:
                value = force_type(elem.text)
            except:
                if relaxed_type:
                    value = elem.text
                else:
                    value = None
        else:
            value = elem.text
        if value:
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
        org_pref = list(filter(condition, org_names))
        org_rest = list(filterfalse(condition, org_names))

        # TODO add try-catch-raise with logging
        # if both lists are empty : exception triggered
        if len(org_pref) > 0:
            org_main = org_pref[0]
        else:
            org_main = org_rest[0]

        result_dict = {'organization': org_main.text}
        org_rest.extend(org_rest[1:])

        org_synonyms = list(map(lambda x: x.text, filter(lambda x: x.text, org_rest)))

        result_dict.update({'organization_synonyms': org_synonyms})

        if branch.attrib:
            if add_no_key in branch.attrib:
                # TODO add try-catch-raise with logging
                # if not int-able : exception triggered
                addr_number = int(branch.attrib[add_no_key])
                result_dict.update({add_no_key: addr_number})
        else:
            result_dict.update({add_no_key: 1})

        # entries below are optional
        add_optional_entry(result_dict, branch, full_address_path)
        add_optional_entry(result_dict, branch, country_path)
        add_optional_entry(result_dict, branch, city_path)
        add_optional_entry(result_dict, branch, state_path)
        add_optional_entry(result_dict, branch, zipcode_path)
        add_optional_entry(result_dict, branch, street_path)

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
        add_optional_entry(result_dict, branch, wos_standard_path)
        add_optional_entry(result_dict, branch, name_path)
        add_optional_entry(result_dict, branch, lastname_path)
        add_optional_entry(result_dict, branch, firstname_path)
        add_optional_entry(result_dict, branch, email_path)

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

        if seq_no not in result_dict.keys():
            result_dict[add_no_key] = 0
        else:
            try:
                result_dict[seq_no] = int(result_dict[seq_no])
            except:
                logging.error(' parse_name() : sequence number could not be extracted :')
                logging.error(etree_to_dict(branch))
    except:
        success = False
        result_dict = etree_to_dict(branch)
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
        add_optional_entry(result_dict, branch, year_path, int)
        add_optional_entry(result_dict, branch, year_path, name_suffix='_str')
        add_optional_entry(result_dict, branch, volume_path, int)
        add_optional_entry(result_dict, branch, page_path, int)
        add_optional_entry(result_dict, branch, doi_path)
        add_optional_entry(result_dict, branch, cited_author_path)
        add_optional_entry(result_dict, branch, cited_title_path)
        add_optional_entry(result_dict, branch, cited_work_path)

        try:
            uid = branch.find(uid_path)
            uid_value = uid.text
        except:
            logging.error(' parse_reference() : uid field absent:')
            logging.error(' parse_reference() : adding ROG id')
            if doi_path in result_dict.keys():
                uid_value = result_dict[doi_path]
            elif cited_title_path in result_dict.keys():
                value = sha1(result_dict[cited_title_path].encode('utf-8')).hexdigest()
                uid_value = 'ROG:' + value
            elif cited_author_path in result_dict.keys() \
                    and year_path+'+str' in result_dict.keys() \
                    and cited_work_path in result_dict.keys():
                str_combo = ' '.join([result_dict[cited_author_path],
                                      result_dict[year_path+'str'], result_dict[cited_work_path]])
                value = sha1(str_combo.encode('utf-8')).hexdigest()
                uid_value = 'ROG:' + value
            else:
                logging.error(' parse_reference() : uid assignment failed')
                raise

        result_dict.update({uid_path: uid_value})
    except:
        success = False
        result_dict = etree_to_dict(branch)
        if not result_dict['reference']:
            logging.warning(' parse_reference() : empty reference')
        else:
            result_dict = etree_to_dict(branch)[reference_path]
            logging.warning(' parse_reference() : corrupt reference :')
            logging.warning(result_dict)
    return success, result_dict


def parse_date(branch, global_year, path=pubinfo_path):
    # TODO include etree_to_dict dump in parse_date
    """
    expected reference structure:

    required:
        year : int
    optional:
        month : int
        day : int
    """

    # jsonic_leaves = list(map(lambda x: x[1], parsed_leaves))
    # if not success:
    #     jsonic_leaves = etree_to_dict(branch)


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

        # satisfied with just the year info
        # good_date = list(map(lambda x: date_dict[x][1], good_keys))
        # ultimate_success = all(list(map(lambda x: date_dict[x][0], date_dict.keys())
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

    if sd in info_dict.keys():
        sortdate = info_dict[sd]
        try:
            date = datetime.strptime(sortdate, '%Y-%m-%d')
            months[sd] = date.month
        except:
            logging.error(' extract_month() : sortdate format '
                          'corrupt: {0}'.format(sortdate))
    if pm in info_dict.keys():
        month_letter = info_dict[pm]
        try:
            if len(month_letter) == 3:
                date = datetime.strptime(month_letter, '%b')
            elif '-' in month_letter or ' ' in month_letter:
                date = datetime.strptime(month_letter[:3], '%b')
            # possible exception trigger
            months['pubmonth'] = date.month
        except:
            logging.error(' extract_month() : pubmonth format '
                          'corrupt: {0}'.format(month_letter))

    # give priority to sortdate month, report possible discrepancy
    if len(months) == 2 and months[sd] != months[pm]:
        logging.error(' extract_month() : extracted months '
                      'from sortdate and pubmonth are not '
                      'equal: {0} and {1}'.format(months[sd], months[pm]))

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
    if pm in info_dict.keys():
        month_letter = info_dict[pm]
        try:
            if ' ' in month_letter:
                date = datetime.strptime(month_letter, '%b %d')
                days['pubmonth'] = date.day
        except:
            logging.error(' extract_day() : pubmonth format '
                          'corrupt: {0}'.format(month_letter))

    # give priority to sortdate month, report possible discrepancy
    if len(days) == 2 and days[sd] != days[pm]:
        logging.error(' extract_day() : day extracted '
                      'from sortdate and from pubmonth are not '
                      'equal: {0} and {1}'.format(days[sd], days[pm]))

    if sd in days.keys():
        day = days[sd]
    elif pm in days.keys():
        day = days[pm]
    else:
        success = False

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
        result_dict = etree_to_dict(branch)
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
        value = etree_to_dict(pub)
    return success, value


def parse_grant(branch):
    """

    required:
        pubtype : str
    optional:
    """

    success = True
    try:
        value = branch.find(grant_agency_path).text
    except:
        logging.info(' parse_grant() : No text attr '
                      'for grant_agency_path field')
        success = False
        value = etree_to_dict(branch)
    return success, value


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
        logging.warn(' parse_title() : No text attr '
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
            # issn2int triggers an exception issn_str is not correct
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

    langueges_list = list(map(lambda x: x['value'], languages[1]))
    primary_language = list(map(lambda y: y['value'],
                                filter(lambda x: 'type' in x.keys() and
                                                 x['type'] == 'primary', languages[1])))
    # populate languages with a list
    result_dict['languages'] = langueges_list

    # populate primary_language with a primary language
    # if not available, the first available
    if primary_language:
        result_dict['primary_language'] = primary_language[0]
    elif langueges_list:
        result_dict['primary_language'] = langueges_list[0]

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

    if source_title:
        result_dict['source_title'] = source_title[0]

    return result_dict


def parse_record(pub, global_year):

    wosid = parse_id(pub)
    pubdate = parse_date(pub, global_year)
    authors = prune_branch(pub, names_path, name_path, parse_name)
    pubtype = parse_pubtype(pub)
    idents = prune_branch(pub, identifiers_path, identifier_path,
                          parse_identifier)

    success = all(map(lambda y: y[0], [wosid, pubdate,
                                       authors, pubtype, idents]))
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

        fund_text = parse_fundtext(pub)

        idents_flat = [item for sublist in idents[1] for item in sublist]

        prop_dict = {x: y for x, y in idents_flat}

        if pubtype[0]:
            prop_dict.update(pubtype[1])
        if languages[0]:
            prop_dict.update(language_dict)
        if titles[0]:
            prop_dict.update(titles_dict)
        if doctypes[0]:
            prop_dict.update({'doctype': doctypes[1]})
        if keywords[0]:
            prop_dict.update({'keywords': keywords[1]})
        if headings[0]:
            prop_dict.update({'headings': headings[1]})
        if subheadings[0]:
            prop_dict.update({'subheadings': subheadings[1]})
        if subjects[0]:
            prop_dict.update({'subjects': list(set(subjects[1]))})
        if abstracts[0]:
            prop_dict.update({'abstracts': abstracts[1]})
        if grant_agencies[0]:
            prop_dict.update({'grant_agencies': grant_agencies[1]})
        if fund_text[0]:
            prop_dict.update({'fund_text': fund_text[1]})

        record_dict = {
            'id': wosid[1],
            'date': pubdate[1],
            'addresses': addresses[1],
            'authors': authors[1],
            'references': references[1],
            'properties': prop_dict,
        }

    else:
        record_dict = etree_to_dict(pub)
        record_dict.update({'id': wosid[1]})
    return success, record_dict


def parse_wos_xml(fp, global_year, good_cf, bad_cf):
    events = ('start', 'end')
    tree = cET.iterparse(fp, events)
    context = iter(tree)
    event, root = next(context)
    rec_ = 'REC'

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


def issn2int(issn_str):
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
            raise ValueError(' issn2int(): invalid check digit'.format(check_bit, rem))

    else:
        logging.error(' issn2int() : issn {0} : does not match '
                      'the pattern {1}'.format(issn_str, pat))

        raise ValueError(' issn2int(): invalid issn string')


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
