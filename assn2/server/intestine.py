# from flask import Flask, request, render_template, Flask, redirect, url_for, make_response, session, Blueprint
from bs4 import BeautifulSoup
from database import *
from collections import defaultdict
import urllib.request
import urllib.error
import pandas as pd
import ssl

# app = Flask(__name__)
sourceUrl = 'http://www.bocsar.nsw.gov.au/Pages/bocsar_crime_stats/bocsar_lgaexceltables.aspx'
postcodeUrl = 'https://docs.google.com/spreadsheets/d/1tHCxouhyM4edDvF60VG7nzs5QxID3ADwr3DGJh71qFg/export?format=csv'
# setting ssl for urlopen error [SSL: CERTIFICATE_VERIFY_FAILED]
ssl._create_default_https_context = ssl._create_unverified_context
city_dict = {}
imported_dict = {}
post_dict = defaultdict(list)
INDEX_INITIALISED = False


def get_data(url):
    '''
    Get bs4 soup from url
    :param url: str of url
    :return: soup parsed by lxml
    '''
    try:
        web_page = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(web_page, 'lxml')
        return soup
    except urllib.error.HTTPError:
        print("HTTPERROR!")
    except urllib.error.URLError:
        print("URLERROR!")


def get_index():
    '''
    Get links_dict from source 1
    :return: links_dict {city : link}
    '''
    sp = get_data(sourceUrl)
    links_dict = {}

    for a in sp.find_all('a', href=True):
        if a.text and a['href'].endswith('.xlsx'):
            links_dict[a.text] = a['href']

    INDEX_INITIALISED = True
    return links_dict


# def to_xml(xlsx_path, filename=None, mode='w'):
    # df_header = pd.read_excel(xlsx_path, sheet_name='Summary of offences', skiprows=4, skip_footer=76)
    # tmp_header_0, tmp_header_1 = list(df_header.iloc[0]), list(df_header.iloc[1])
    # header = []
    # year = None
    # header_length = df_header.shape[1]
    # for i in range(header_length):
    #     if i not in range(2, header_length - 3):
    #         item = tmp_header_1[i]
    #     elif i % 2 == 0:
    #         item = tmp_header_0[i] + ' ' + tmp_header_1[i]
    #     else:
    #         item = tmp_header_0[i - 1] + ' ' + tmp_header_1[i]
    #     header.append(item)
    # print(header)
    # pd.DataFrame.to_xml = to_xml
    #
    # def row_to_xml(row):
    #     xml = ['<item>']
    #     for i, col_name in enumerate(row.index):
    #         xml.append('  <field name="{0}">{1}</field>'.format(col_name, row.iloc[i]))
    #     xml.append('</item>')
    #     return '\n'.join(xml)
    #
    # res = '\n'.join(df.apply(row_to_xml, axis=1))
    #
    # if filename is None:
    #     return res
    # with open(filename, mode) as f:
    #     f.write(res)


def get_doc(city, save=False):
    '''

    :param city: str of city name
    :param save: bool
    :return: None
    '''
    global city_dict
    if not city_dict:
        city_dict = get_index()
    cid = sorted(city_dict).index(city)
    # print(city_dict)
    # print(list(city_dict))
    # print(sorted(city_dict))
    prefix = 'http://www.bocsar.nsw.gov.au'
    try:
        end_point = city_dict[city]
        filename = end_point.replace('/Documents/RCS-Annual/', '').replace('.xlsx', '')
        url = prefix + end_point
        xlsx_path = './xlsx/' + filename + '.xlsx'
        urllib.request.urlretrieve(url, xlsx_path)

    except KeyError:
        print('City Not Found!')
        return
    except urllib.error.HTTPError:
        print('HTTP ERROR!')
        return
    except urllib.error.URLError:
        print('URL ERROR!')
        return

    df = pd.read_excel(xlsx_path, sheet_name='Summary of offences', skiprows=4, skip_footer=14, header=[1, 2])
    nb_of_records = df.shape[0]
    # get headers (tuples)
    headers = list(df)
    headers[0] = (headers[0][1], '')
    # convert to string
    headers_str = []
    for i in range(len(headers)):
        if i == 0:
            headers_str.append(str(headers[i][0]).rstrip())
            continue
        if i < (len(headers) - 3):
            headers_str.append(str(headers[i][0]) + ' ' + str(headers[i][1]))
        else:
            headers_str.append(str(headers[i][1]))
    indices = [str(e) for e in df.index.values]
    last_index = indices[0]
    record_list = []
    for i in range(nb_of_records):
        d = list(df.iloc[i])
        if indices[i] == 'nan':
            index = last_index
        else:
            index = indices[i]
        # item = index + d
        items = {}
        for j in range(len(d)):
            items[headers_str[j]] = str(d[j])
        # TODO: add record to MongoDB after creation DONE
        record_list.append(Record(cid, i, index, items))
    _city = City(cid, city, record_list)
    if save:
        save_city_and_record(_city, record_list)
        imported_dict[_city.name] = _city.id


def get_postcode_dict():
    '''
    Get postcode_dict from source 2
    :return: None
    '''
    # filename = 'postcode_index.csv'
    # try:
    #     # urllib.request.urlretrieve(postcodeUrl, filename=filename)
    # except urllib.error.HTTPError:
    #     print('HTTP ERROR!')
    # except urllib.error.URLError:
    #     print('URL ERROR!')

    # if post_dict is not None:
    #     return
    # post_dict = defaultdict(list)
    global city_dict, post_dict
    _df = pd.read_csv(postcodeUrl)
    df = _df[_df['State'] == 'New South Wales']
    length = df.shape[0]
    for i in range(length):
        data = df.iloc[i]
        city = data['LGA region']
        postcode = data['Postcode']
        if city not in city_dict:
            continue
        post_dict[postcode].append(city)

    # return post_dict


# get_doc(city='Sydney')
# if not _INDEX_INITIALISED:
#     city_dict = get_index()
# # get_index()
# get_postcode_dict()
# post_dict[2017]