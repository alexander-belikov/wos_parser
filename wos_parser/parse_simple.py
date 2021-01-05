import xml.etree.ElementTree as et
import xmltodict


def parse_simple(fp, good_cf):
    """
    driver func, parse file fp, push good and bad records
    accordingly to good_cf and bad_cf

    :param fp: filepointer to be parsed
    :param good_cf: chunk flusher of good records
    :return:
    """
    events = ("start", "end")
    tree = et.iterparse(fp, events)
    context = iter(tree)
    event, root = next(context)
    rec_ = "REC"
    for event, pub in context:
        if event == "end" and pub.tag == rec_:
            item = et.tostring(pub, encoding='utf8', method='xml').decode("utf")
            obj = xmltodict.parse(item)
            good_cf.push(obj)
            root.clear()
