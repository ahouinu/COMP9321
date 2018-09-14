'''
COMP9321 18s1 Assignment 2
Python Client
Written by Tianpeng Chen z5176343 on 28/04/18

Usage: % python client.py
    then follow the prompts

Please see README.txt for sample test cases, sorry I should have made a doctest for this client...
'''

import requests

_root = 'http://127.0.0.1:5000'


def login(*args):

    if len(args) != 2:
        print('usage: login(username, password)')
        quit()

    json = {
        "username": args[0],
        "password": args[1]
    }

    result = requests.get('http://localhost:5000/auth', json=json, headers={"Content-Type": "application/json"})

    if not result.ok:
        print(f'Status code: {result.status_code}')
        print(result.text)
        quit()
    else:
        print(f'token: {result.text}\n')
        return result.text


def import_data_by_name(token, lgaName, rtype='ATOM'):

    # if len(args) != 1:
    #     print('Please provide LGA name')

    payload = {
        "lgaName": lgaName,
    }
    param = {
        "rtype": rtype
    }
    headers = {'AUTH_TOKEN': token}

    result = requests.post(_root+'/records', headers=headers, data=payload, params=param)

    if not result.ok:
        print(f'Status code: {result.status_code}')
        print(result.text)
        # quit()
    else:
        print(f'Status code: {result.status_code}')
        print('Payload:')
        print(result.text)
        # print(f'payload: {result.text}\n')
        # return result.text
    return


def import_data_by_postcode(token, postcode, rtype='ATOM'):

    postcode = int(postcode)

    payload = {
        "Postcode": postcode
    }
    param = {
        "rtype": rtype
    }
    headers = {'AUTH_TOKEN': token}

    result = requests.post(_root+'/records', headers=headers, data=payload, params=param)

    if not result.ok:
        print(f'Status code: {result.status_code}')
        print(result.text)
        # quit()
    else:
        print(f'Status code: {result.status_code}')
        print('Payload:')
        print(result.text)
        # print(f'payload: {result.text}\n')
        # return result.text
    return


def get_all_collection(token, rtype='ATOM'):

    param = {
        "rtype": rtype
    }
    headers = {'AUTH_TOKEN': token}

    # GET /records?rtype=ATOM
    result = requests.get(_root + '/records', headers=headers, params=param)

    if not result.ok:
        print(f'Status code: {result.status_code}')
        print(result.text)
        # quit()
    else:
        print(f'Status code: {result.status_code}')
        print('Payload:')
        print(result.text)
        # print(f'payload: {result.text}\n')
        # return result.text
    return


def get_single_entry(token, cid, rtype='ATOM'):
    param = {
        "rtype": rtype
    }
    headers = {'AUTH_TOKEN': token}

    result = requests.get(_root + f'/records/{cid}', headers=headers, params=param)

    if not result.ok:
        print(f'Status code: {result.status_code}')
        print(result.text)
        # quit()
    else:
        print(f'Status code: {result.status_code}')
        print('Payload:')
        print(result.text)
        # print(f'payload: {result.text}\n')
        # return result.text
    return


def del_single_entry(token, cid):

    headers = {'AUTH_TOKEN': token}

    # DELETE /records/<id>
    result = requests.delete(_root + f'/records/{cid}', headers=headers)

    if not result.ok:
        print(f'Status code: {result.status_code}')
        print(result.text)
        # quit()
    else:
        print(f'Status code: {result.status_code}')
        print('Payload:')
        print(result.text)
        # print(f'payload: {result.text}\n')
        # return result.text
    return


def filter_1(token, query_string):
    # try to simulate as a real browser...
    data = query_string.replace(' ', '+')
    data.encode('utf-8')
    print(data)
    headers = {'AUTH_TOKEN': token}

    result = requests.get(_root + f'/records/filter?{data}', headers=headers)

    if not result.ok:
        print(f'Status code: {result.status_code}')
        print(result.text)
        # quit()
    else:
        print(f'Status code: {result.status_code}')
        print('Payload:')
        print(result.text)
        # print(f'payload: {result.text}\n')
        # return result.text
    return


def filter_2(token, query_string):
    # try to simulate as a real browser...
    data = query_string.replace(' ', '+')
    data.encode('utf-8')
    headers = {'AUTH_TOKEN': token}

    result = requests.get(_root + f'/records/filter?{data}', headers=headers, data=data)

    if not result.ok:
        print(f'Status code: {result.status_code}')
        print(result.text)
        # quit()
    else:
        print(f'Status code: {result.status_code}')
        print('Payload:')
        print(result.text)
        # print(f'payload: {result.text}\n')
        # return result.text
    return


def main():
    print('Please login as admin or guest first')
    username = input('username:')
    password = input('password:')

    token = login(username, password)
    _list = [import_data_by_name, import_data_by_postcode, get_all_collection,
             get_single_entry, del_single_entry, filter_1, filter_2]

    while 1:

        print('Please select function')

        for i in range(len(_list)):
            print(f'{i}: {_list[i].__name__}')

        print(f'7: quit')

        op = int(input('Select 0-7\n'))
        # additions = tuple(input('Please provide additional arguments (separated by 1 space)\n').split(' '))

        try:
            if op == 0:
                # args[0]: lgaName
                lgaName = input('Please provide LGA name:')
                rtype = input('Please provide preferred return type: ATOM or JSON:')
                import_data_by_name(token, lgaName=lgaName, rtype=rtype)
            elif op == 1:
                # args[0]: Postcode
                postcode = input('Please provide postcode:')
                rtype = input('Please provide preferred return type: ATOM or JSON:')
                import_data_by_postcode(token, postcode=postcode, rtype=rtype)
            elif op == 2:
                # args[0]: rtype
                rtype = input('Please provide preferred return type: ATOM or JSON:')
                get_all_collection(token, rtype=rtype)
            elif op == 3:
                # args[0]: id
                # args[1]: rtype
                cid = input('Please provide city id:')
                rtype = input('Please provide preferred return type: ATOM or JSON:')
                get_single_entry(token, cid, rtype=rtype)
            elif op == 4:
                cid = input('Please provide city id:')
                del_single_entry(token, cid)
            elif op == 5:
                # args[0]: query_string
                query_string = input('Please provide your query string\n'
                                     'format: lgaName eq Sydney [or lgaName eq Blue Mountains]:\n')
                filter_1(token, query_string)
            elif op == 6:
                # args[0]: query_string
                query_string = input('Please provide your query string\n'
                                     'format: lgaName eq Sydney and year eq 2015:\n')
                filter_2(token, query_string)
            elif op == 7:
                quit(0)
            else:
                print('Wrong option, please try again!')
        except IndexError:
            print('Wrong additional arguments...Please try again')


if __name__ == '__main__':
    main()