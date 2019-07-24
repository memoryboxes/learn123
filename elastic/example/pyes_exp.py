# -*- coding: utf-8 -*-

import io
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


def insert(doc, doc_id, es):
    res = es.index(index="btgo1", doc_type='torrent', id=doc_id, body=doc)
    return res['result']


def gendoc():
    i = 0
    for line in io.open('tpb_2019_full.sort.csv', 'r'):
        line = line.replace('"', '')
        fields = line.strip().split('|')
        if len(fields) < 4:
            continue

        try:
            title = fields[0]
            size = int(fields[1])
            category = fields[2]
            link = fields[3]
        except BaseException:
            continue

        i += 1
        if i % 10000 == 0 and i > 10000:
            print("bulk insert {} docs".format(i))

        yield {
            "_index": "btgo1",
            "_type": "document",
            'title': title,
            'size': size,
            'category': category,
            'link': link
        }


if __name__ == '__main__':

    # you can use RFC-1738 to specify the url
    es = Elasticsearch(['http://192.168.1.100:9200'])
    bulk(es, gendoc())
