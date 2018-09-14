from mongoengine import connect
from models import *

host_addr = 'SOME_URL'
connect(db='DB_NAME', username='USER', password='PASSWD', host=host_addr)


def save_city_and_record(city, record_list):
    connect('record')
    for record in record_list:
        record.save()
    connect('city')
    city.save()


def get_city_records(cid):
    connect('city')
    return City.objects(id=cid)

# city = get_city_records(109)
# for r in city[0].records:
#     print(f'cid: {r.cid}\tid: {r.id}\tOffence Group: {r.offence_group}\tOffence Type: {r.offence_type}')
#     for k, v in r.records_dict.items():
#         print(k, ':\t', v)
