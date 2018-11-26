import csv
from collections import deque
import elasticsearch
from elasticsearch import helpers


def json_converter():
    with open("elastic_wardrive-01.kismet.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        next(csv_reader)
        for line in csv_reader:
            wifi = {}
            wifi['Network'] = int(line[0])
            wifi['NetType'] = str(line[1])
            wifi['ESSID'] = str(line[2])
            wifi['BSSID'] = str(line[3])
            wifi['Channel'] = int(line[5])
            wifi['Encryption'] = str(line[7])
            wifi['MaxRate'] = float(line[9])
            yield wifi


es = elasticsearch.Elasticsearch()
es.indices.delete(index="wifiwd",ignore=404)
deque(helpers.parallel_bulk(es,json_converter(),index="wifiwd",doc_type="wifi"), maxlen=0)
es.indices.refresh()