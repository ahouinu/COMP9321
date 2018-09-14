'''
COMP9321 18s1 Assignment 2
Flask Server
Written by Tianpeng Chen z5176343, 29/04/18

Usage:  % python view.py
Note: Server runs on localhost:5000 by default
Mongodb:'mongodb://assn2:314628@ds157089.mlab.com:57089/comp9321_assn2'
'''


from flask import Flask, request, Flask, url_for, jsonify
from flask_restful import reqparse
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer)

from werkzeug.contrib.atom import AtomFeed
from datetime import datetime

import intestine
from models import *
import database
from auth import login_required, admin_required, SECRET_KEY, CURRENT_USER
# from Intestine import *

app = Flask(__name__)
# imported_dict = {}  # lgaName, cid
# entry_id = 0
entry_dict = {}
author = {'admin': Author(id=0, username='admin', password='admin'),
          'guest': Author(id=1, username='guest', password='guest')}

# TEST ONLY
# CURRENT_USER = 'admin'


# Server initialisation
def setup_app(app):
    global CURRENT_USER
    if not intestine.INDEX_INITIALISED:
        intestine.city_dict = intestine.get_index()
        intestine.get_postcode_dict()
    if not CURRENT_USER:
        CURRENT_USER = 'guest'


def return_response(obj, *args, rtype='ATOM', mode=None):

    # TODO: return AtomFeed.get_response() instead of AtomFeed

    if mode == 'Entry':

        if rtype == 'JSON':

            _id = url_for('get_record', id=obj.id)
            _dict = obj._json_dict
            _dict['id'] = _id

            if args:

                _dict['content'] = []
                # _tmp_dict = {}
                for r in args[0]:
                    _tmp_dict = {'id': r.id,
                                 'cid': r.cid,
                                 'Offence Group': r.offence_group}
                    for k, v in r.records_dict.items():
                        _tmp_dict[k] = v
                    _dict['content'].append(_tmp_dict)

            return jsonify(_dict)

        elif rtype == 'ATOM':

            _dict = obj._atom_dict

            if args:
                if args[0] == 'naked':
                    return AtomFeed(id=url_for('get_record', id=_dict['id']),
                                    title=_dict['title'], updated=_dict['updated'],
                                    author=_dict['author'].get('name'))
            return AtomFeed(id=url_for('get_record', id=_dict['id']),
                            title=_dict['title'], updated=_dict['updated'],
                            author=_dict['author'].get('name')).get_response()
            # return AtomFeed(kwargs)

        elif rtype == 'DICT':

            _id = url_for('get_record', id=obj.id)
            _dict = obj._json_dict
            _dict['id'] = _id

            return _dict

    if mode == 'Collection':

        _res = []

        if len(obj) == 0:
            return jsonify()

        if rtype == 'ATOM':
            for o in obj.values():
                _res.append(return_response(o, 'naked', rtype=rtype, mode='Entry'))
            return AtomFeed(id=url_for('get_record_collections'), title='List of Entries', entries=_res).get_response()

        if rtype == 'JSON':
            for o in obj.values():
                _res.append(return_response(o, rtype='DICT', mode='Entry'))
            return jsonify(_res)

    if mode == 'Get Entry':

        data = args[0][0].records
        _cid = data[0].cid

        if rtype == 'ATOM':
            _res = []
            _entry = entry_dict[_cid]
            _feed = AtomFeed(id=url_for('get_record', id=_cid), title=_entry.title, updated=_entry.updated,
                             author=_entry.author.username)
            for r in data:
                _res += r._atom_str_list
            _xml = '<?xml version="1.0" encoding="utf-8" ?>\n'
            _xml += '\n'.join([r for r in _res])
            _feed.add(id=url_for('get_record', id=_cid), title=_entry.title, updated=_entry.updated,
                      content=_xml, content_type='xhtml')
            return _feed.get_response()

        if rtype == 'JSON':
            res = return_response(obj, data, rtype=rtype, mode='Entry')
            return res

    if mode == 'year':

        if rtype == 'JSON':
            # Not Supported
            pass

        elif rtype == 'ATOM':

            if args:

                _res = args[0]
                _entry = obj

                _feed = AtomFeed(id=url_for('retreive_data_entries_with_filter'), title=_entry.title, updated=_entry.updated,
                                 author=_entry.author.username)

                _xml = '<?xml version="1.0" encoding="utf-8" ?>\n'
                _xml += '\n'.join([r for r in _res])
                _feed.add(id=url_for('retreive_data_entries_with_filter'), title=_entry.title, updated=_entry.updated,
                          content=_xml, content_type='xhtml')

                return _feed.get_response()

        return jsonify(message='Error when generating AtomFeed'), 400


@app.route('/records', methods=['POST'])
@admin_required
def import_records():
    # try:
    # data = request.data
    # global post_dict, imported_dict
    # print(data)
    global CURRENT_USER
    # TODO: return Atom Feed using werkzeug.contrib.atom.AtomFeed DONE
    lga_name = request.form.get('lgaName')
    postcode = request.form.get('Postcode')
    # get HTTP Content Negotiation
    parser = reqparse.RequestParser()
    parser.add_argument('rtype', type=str)
    args = parser.parse_args()
    rtype = args.get('rtype')
    if rtype not in ['ATOM', 'JSON']:
        rtype = 'ATOM'
    if postcode:
        postcode = int(postcode)
    if lga_name is None and postcode is None:
        return jsonify(message='Please provide valid LGA name or postcode'), 400
    if lga_name is None:
        try:
            lga_list = intestine.post_dict[postcode]
        except KeyError:
            return jsonify(message='City not found!'), 400
        if len(lga_list) == 0:
            return jsonify(message='City not found!'), 400
        if len(lga_list) > 1:
            _dict = {'message': 'Provided postcode maps to multiple cities, please use LGA name instead',
                     f'LGA names of {postcode}': lga_list}
            return jsonify(_dict), 400
        else:
            lga_name = lga_list[0]
    if lga_name in intestine.imported_dict:
        cid = intestine.imported_dict[lga_name]
        return return_response(entry_dict[cid], rtype=rtype, mode='Entry'), 200
    try:
        intestine.get_doc(city=lga_name, save=True)
    except ValueError:
        return jsonify(message='Please provide valid LGA name or postcode'), 400
    cid = intestine.imported_dict[lga_name]
    now = datetime.now()
    entry = Entry(cid, f'{lga_name} Crime Record', now, author=author[CURRENT_USER])
    entry_dict[cid] = entry

    # TODO: record author, save entry record DONE
    return return_response(entry, rtype=rtype, mode='Entry'), 201


@app.route('/records', methods=['GET'])
@login_required
def get_record_collections():
    if len(entry_dict) == 0:
        return jsonify(), 200
    parser = reqparse.RequestParser()
    parser.add_argument('rtype', type=str)
    args = parser.parse_args()
    rtype = args.get('rtype')

    if rtype not in ['ATOM', 'JSON']:
        rtype = 'ATOM'

    return return_response(entry_dict, rtype=rtype, mode='Collection'), 200


@app.route('/records/<id>', methods=['GET'])
@login_required
def get_record(id):
    # TODO: Get metadata from mongodb
    id = int(id)
    try:
        entry = entry_dict[id]
    except KeyError:
        return jsonify(message='Data entry not found! Please import first'), 404
    _city = database.get_city_records(id)

    parser = reqparse.RequestParser()
    parser.add_argument('rtype', type=str)
    args = parser.parse_args()

    rtype = args.get('rtype')
    if rtype not in ['ATOM', 'JSON']:
        rtype = 'ATOM'

    return return_response(entry, _city, rtype=rtype, mode='Get Entry'), 200


@app.route('/records/<id>', methods=['DELETE'])
@admin_required
def del_record(id):
    try:
        # entry = entry_dict[int(id)]
        _city = database.get_city_records(id)[0]
        intestine.imported_dict.pop(_city.name)
        entry_dict.pop(int(id))
    except KeyError:
        return jsonify('Not Found!'), 404
    return jsonify(f'The following record has been deleted: {id}'), 200
# def retrieve_user():
#     serialized_user = session.get('_user')


@app.route("/auth", methods=['GET'])
def generate_token():
    global CURRENT_USER
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    args = parser.parse_args()

    username = args.get('username')
    password = args.get('password')

    s = Serializer(SECRET_KEY, expires_in=600)
    token = s.dumps(username)

    if (username == 'admin' and password == 'admin') or\
            (username == 'guest' and password == 'guest'):
        CURRENT_USER = username
        return token.decode()

    return jsonify(message='Incorrect username or password, please try again!'), 404


@app.route('/records/filter', methods=['GET'])
@login_required
def retreive_data_entries_with_filter():
    '''
    query type 1: lgaName eq lgaVal [or lgaName eq lgaVal]
    query type 2: lgaName eq lgaVal and year eq yearVal
    :return:
    '''

    # _type = 0
    # get query parameters
    query_list = request.query_string.decode('utf-8').split('+')

    # decide query type
    if 'year' in query_list:
        return filter_2(query_list)
    else:
        return filter_1(query_list)


def filter_1(query_list):

    # TODO: modify to accept lgaNames like 'Blue Mountains'

    _list = []
    _entries = {}

    # if len(query_list) == 3:
    #     _list.append(query_list[2])
    #
    # else:
    #     _list.append(query_list[2])
    #     _list.append(query_list[6])

    if query_list.count('lgaName') == 1:
        _offset = query_list.index('eq')
        _list.append(' '.join([e for e in query_list[_offset + 1:]]))

    elif query_list.count('lgaName') == 2:
        _offset_eq_1 = query_list.index('eq')
        _offset_or = query_list.index('or')
        _offset_eq_2 = query_list.index('eq', _offset_eq_1 + 1, -1)
        _item_1 = ' '.join([e for e in query_list[_offset_eq_1 + 1: _offset_or]])
        _item_2 = ' '.join([e for e in query_list[_offset_eq_2 + 1:]])

        _list.append(_item_1)
        _list.append(_item_2)

    for e in _list:
        try:
            _cid = intestine.imported_dict[e]
            _entries[_cid] = entry_dict[_cid]
        except KeyError:
            return jsonify(message='Not Found'), 404

    return return_response(_entries, mode='Collection'), 200


def filter_2(query_list):

    _lgaName, _year = None, None

    _offset_eq_1 = query_list.index('eq')
    _offset_and = query_list.index('and')
    # _offset_eq_2 = query_list.index('eq', start=-1, stop=_offset_eq_1)

    _lgaName = ''.join([e for e in query_list[_offset_eq_1 + 1: _offset_and]])
    # _year = int(query_list[_offset_eq_2 + 1])
    _year = int(query_list[-1])

    try:
        _cid = intestine.imported_dict[_lgaName]
        _city = database.get_city_records(_cid)[0]
        _entry = entry_dict[_cid]
    except KeyError:
        return jsonify(message='Not Found'), 404

    # TODO: generate AtomFeed and return
    # print(_city.get_records_by_year(_year))
    _xml_str_list = _city.get_records_by_year(_year)

    return return_response(_entry, _xml_str_list, mode='year'), 200

setup_app(app)

if __name__ == '__main__':
    # app.config['TESTING'] = True
    app.run()
