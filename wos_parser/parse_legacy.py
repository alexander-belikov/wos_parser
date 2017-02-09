import xml.etree.cElementTree as cET
from .xml_consts import id_path
from .xml_consts import add_spec_path\

from .xml_consts import pubinfo_path
from .xml_consts import add_path

from .xml_consts import names_path, name_path\

from .xml_consts import references_path, reference_path

from .xml_consts import doctype_path, add_no_key, org_path

from .parse import is_int, extract_year, extract_month, \
    extract_day, etree_to_dict

au_email = './email_addr'
au_lastname = './last_name'
au_firstname = './first_name'
au_wos = './wos_standard'

fields_dict = {'wos': au_wos, 'first': au_firstname,
               'last': au_lastname, 'email': au_email}

import logging


def parse_date2(attrib_dict, global_year):
    # TODO include etree_to_dict dump in parse_date
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
        year = extract_year(attrib_dict, global_year)
        date_dict = {'year': year}
        try:
            month = extract_month(attrib_dict)
            date_dict.update({'month': month})
        except:
            logging.error('Could not capture month')
        try:
            day = extract_day(attrib_dict)
            date_dict.update({'day': day})
        except:
            logging.error('Could not capture day')

        # actually we are satisfied with just the year info
        # good_date = list(map(lambda x: date_dict[x][1], good_keys))
        # ultimate_success = all(list(map(lambda x: date_dict[x][0], date_dict.keys())
        date_dict = {k: v[1] for k, v in date_dict.items() if v[0]}
    except:
        date_dict = {}
        success = False
    return success, date_dict


def parse_refs(list_refs, condition='weak', lower_bound=0):
    # returns a list of wos:ids with or without years
    list_weak = filter(lambda x: not x[0] is None and
                       x[0].text.lower().startswith('wos:'), list_refs)
    if condition == 'weak':
        return list(map(lambda x: x[0].text, list_weak))
    else:
        strong_list = filter(lambda x: not x[1] is None and
                             is_int(x[1].text), list_weak)
        result_strong_list = list(map(lambda x: (x[0].text, int(x[1].text)),
                                  strong_list))
#         strong_list = filter(lambda x: not x[1] is None, list_weak)
#         result_strong_list = map(lambda x: (x[0].text, x[1].text),
#                                  strong_list)
        if condition == 'strong':
            return result_strong_list
        elif condition == 'superstrong':
            return list(map(filter(lambda x: x[1] > lower_bound, result_strong_list)))


def extract_author_info(authors):
    authors_parsed = [parse_name(name) for name in authors]
    return authors_parsed


def parse_name(name):

    namefields_dict = {k: name.find(fields_dict[k])
                       for k in fields_dict.keys()}
    parsed_dict = {k: ('' if namefields_dict[k] is None
                       else namefields_dict[k].text)
                   for k in namefields_dict.keys()}

    # name.attrib should hold {'addr_no': 'k m n'}

    address_numbers = {}
    if not name.attrib or add_no_key not in name.attrib.keys():
        address_numbers[add_no_key] = [0]
    else:
        ll_str = name.attrib[add_no_key].split(' ')
        ll_int = filter(lambda x: is_int(x), ll_str)
        address_numbers[add_no_key] = list(map(lambda x: int(x), ll_int))

    parsed_dict.update(address_numbers)

    return parsed_dict


def parse_adds(addr):
    addspecs = addr.findall(add_spec_path)
    res = list(map(lambda x: parse_address(x), addspecs))
    return res

def parse_address(addspec):
    addr_number = addspec.attrib[add_no_key]
    org_names = addspec.findall(org_path)
    # org_names = filter(lambda x: x.attrib['pref'] == 'Y', org_names)
    org_names_text = list(map(lambda x: x.text, org_names))
    return addr_number, org_names_text


def parse_wos_xml(xml_filename, global_year=None):
    """
    read xml file and pop a list of accumulated data
    """

    # rec_ = fixtag('', 'REC', nsmap)
    # uid_path = fixtag('', 'UID', nsmap)
    rec_ = 'REC'
    uid_path = 'UID'

    context = cET.iterparse(xml_filename, ("start", "end"))
    context = iter(context)
    # get the root element
    event, root = next(context)
    pubtypes_set = set()
    doc_types_set = set()
    pub_data = []

    for event, pub in context:
        if event == "end" and pub.tag == rec_:
            # reach all the branches
            wosid_ = pub.find(uid_path)
            if wosid_ is not None:
                wosid = wosid_.text
            else:
                continue
            identifiers_ = pub.findall(id_path)
            doctypes_ = pub.findall(doctype_path)
            addresses_ = pub.find(add_path)
            pubinfo_ = pub.find(pubinfo_path)
            ref_path = references_path + '/' + reference_path
            refs_ = pub.findall(ref_path)
            author_path = names_path + '/' + name_path
            authors_ = pub.findall(author_path)
            # orgs_ = pub.findall(org_path)

            dict_pub_identifiers_ = {item.attrib['type']: item.attrib['value']
                                     for item in identifiers_}

            # list_au_identifiers_ = [name.attrib for name in authors_]

            pubtype = pubinfo_.attrib['pubtype']
            year = extract_year(pubinfo_.attrib, global_year)

            try:
                month = extract_month(pubinfo_.attrib)
            except:
                logging.error("Could not capture month for wosid {0}".format(wosid))

            try:
                day = extract_day(pubinfo_.attrib)
            except:
                logging.error("Could not capture day for wosid {0}".format(wosid))

            pubtypes_set |= set([pubtype])

            refs = [(r.find('uid'), r.find('year')) for r in refs_]
            refs_parsed = parse_refs(refs, 'strong')

            list_au = extract_author_info(authors_)
            adds = parse_adds(addresses_)

            doc_types = list(map(lambda x: x.text, doctypes_))
            doc_types_set |= set(doc_types)

            info_dict = {
                            'id': wosid,
                            'year': year,
                            'month': month,
                            'day': day,
                            'pub_type': pubtype,
                            'doc_types': doc_types,
                            'pub_identifiers': dict_pub_identifiers_,
                            'authors': list_au,
                            'addresses': adds,
                            'refs': refs_parsed
            }

            pub_data.append(info_dict)
            root.clear()

    return pub_data, pubtypes_set, doc_types_set


# obsolete: use prune_branch
def parse_names(pub):
    names_branch = pub.find(names_path)
    name_leaves = names_branch.findall(name_path)
    names = list(map(parse_name, name_leaves))
    success = all(list(map(lambda x: x[0], names)))
    names_json = list(map(lambda x: x[1], names))
    if not success:
        names_json = etree_to_dict(names_branch)
    return success, names_json


# obsolete: use prune_branch
def parse_addresses(pub):
    addresses_branch = pub.find(add_path)
    address_specs = addresses_branch.findall(add_spec_path)
    addresses = list(map(parse_address, address_specs))
    success = all(list(map(lambda x: x[0], addresses)))
    list_addresses = list(map(lambda x: x[1], addresses))
    if not success:
        list_addresses = etree_to_dict(addresses_branch)
    return success, list_addresses

