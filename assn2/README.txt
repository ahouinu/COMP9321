// README.txt
Student ID: z5176343    Name: Tianpeng Chen


Installation Guide:

1. server side
    a) Unzip server.zip, and open project in PyCharm
    b) Setup virtual env for server project
    c) Install all required modules using 'pip install -r requirements.txt'
    d) run view.py (runs on localhost:5000 by default)

2. client side
    a) Unzip client.zip, and open project in PyCharm
    b) Setup virtual env for client project
    c) Install the only required module 'requests' using 'pip install -r requirements.txt'
    d) run client.py and follow prompts


Sample test cases:

    run client.py

    ---- START ----

    -- test 1 --
    import Sydney by name, get response in JSON
    input:
        1) type 0 to import data by name
        2) type Sydney\n JSON\n
    expected output:
        Status code: 201
        Payload:
        {
        "author":
            {
            "name":"admin"
            },
        "id":"/records/109",
        "title":"Sydney Crime Record",
        "updated":"2018-04-29 03:15"
        }
    -- test 1 --

    -- test 2 --
    import Leeton by name, get response in ATOM
    input:
        1) type 0 to import data by name
        2) type Leeton\n ATOM\n
    expected output:
        Status code: 201
        Payload:
        <?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <title type="text">Leeton Crime Record</title>
            <id>/records/67</id>
            <updated>2018-04-29T03:43:52.435106Z</updated>
            <author>
                <name>admin</name>
            </author>
            <generator>Werkzeug</generator>
        </feed>
    -- test 2 --

    -- test 3 --
    import Sydney by postcode (2000), should get 200
    input:
        1) type 1 to import data by postcode
        2) type 2000\n ATOM\n
    expected output:
        Status code: 200
        Payload:
        <?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <title type="text">Sydney Crime Record</title>
            <id>/records/109</id>
            <updated>2018-04-29T03:15:06.441264Z</updated>
            <author>
                <name>admin</name>
            </author>
            <generator>Werkzeug</generator>
        </feed>
    -- test 3 --

    -- test 4 --
    import Corwa by postcode (2583), since 2583 maps to multiple cities, my server will give 400 as response
    and suggest to import them by name
    input:
        1) type 1 to import data by postcode
        2) type 2583\n JSON\n
    expected output:
        Status code: 400
        Payload:
        {
        "LGA names of 2583":["Bathurst Regional","Cowra","Oberon","Upper Lachlan Shire"],
        "message":"Provided postcode maps to multiple cities, please use LGA name instead"
        }
    -- test 4 --

    -- test 5 --
    get all data collection
    input:
        1) type 2 to get all collection
        2) type ATOM\n (or JSON)
    expected output:
        Status code: 200
        Payload:
        <?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <title type="text">List of Entries</title>
          <id>/records</id>
          <updated>2018-04-29T03:43:52.435106Z</updated>
          <generator>Werkzeug</generator>
          <?xml version="1.0" encoding="utf-8"?>
          <feed xmlns="http://www.w3.org/2005/Atom">
            <title type="text">Sydney Crime Record</title>
            <id>/records/109</id>
            <updated>2018-04-29T03:15:06.441264Z</updated>
            <author>
              <name>admin</name>
            </author>
            <generator>Werkzeug</generator>
          </feed>
          <?xml version="1.0" encoding="utf-8"?>
          <feed xmlns="http://www.w3.org/2005/Atom">
            <title type="text">Bathurst Regional Crime Record</title>
            <id>/records/4</id>
            <updated>2018-04-29T03:16:53.181010Z</updated>
            <author>
              <name>admin</name>
            </author>
            <generator>Werkzeug</generator>
          </feed>
          <?xml version="1.0" encoding="utf-8"?>
          <feed xmlns="http://www.w3.org/2005/Atom">
            <title type="text">Leeton Crime Record</title>
            <id>/records/67</id>
            <updated>2018-04-29T03:43:52.435106Z</updated>
            <author>
              <name>admin</name>
            </author>
            <generator>Werkzeug</generator>
          </feed>
        </feed>
    -- test 5 --

    -- test 6 --
    get data entry of Sydney (cid=109)
    input:
        1) type 3 to get single data entry
        2) type 109\n ATOM\n
    expected output:
        Status code: 200
        Content: an ATOM feed containing all crime statistics of Sydney
    -- test 6 --

    -- test 7 --
    delete data entry of Leeton (cid=67)
    input:
        1) type 4 to delete single data entry
        2) type 67\n
    expected output:
        Status code: 200
        Payload:
        "The following record has been deleted: 67"
    -- test 7 --

    -- test 8 --
    filter 1 test 1
    query_string = 'lgaName eq Sydney'
    input:
        1) type 5 to get data using filter 1
        2) type lgaName eq Sydney\n
    expected output:
        Status code: 200
        Payload:
        <?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <title type="text">List of Entries</title>
          <id>/records</id>
          <updated>2018-04-29T04:13:39.519761Z</updated>
          <generator>Werkzeug</generator>
          <?xml version="1.0" encoding="utf-8"?>
          <feed xmlns="http://www.w3.org/2005/Atom">
            <title type="text">Sydney Crime Record</title>
            <id>/records/109</id>
            <updated>2018-04-29T04:13:39.519761Z</updated>
            <author>
              <name>admin</name>
            </author>
            <generator>Werkzeug</generator>
          </feed>
        </feed>
    -- test 8 --

    -- test 9 --
    filter 1 test 2
    query_string = 'lgaName eq Sydney or lgaName eq Blue Mountains'
    input:
        1) type 5 to get data using filter 1
        2) type lgaName eq Sydney or lgaName eq Blue Mountains
    expected output:
        Status code: 200
        Payload:
        <?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <title type="text">List of Entries</title>
          <id>/records</id>
          <updated>2018-04-29T04:15:56.629041Z</updated>
          <generator>Werkzeug</generator>
          <?xml version="1.0" encoding="utf-8"?>
          <feed xmlns="http://www.w3.org/2005/Atom">
            <title type="text">Sydney Crime Record</title>
            <id>/records/109</id>
            <updated>2018-04-29T04:13:39.519761Z</updated>
            <author>
              <name>admin</name>
            </author>
            <generator>Werkzeug</generator>
          </feed>
          <?xml version="1.0" encoding="utf-8"?>
          <feed xmlns="http://www.w3.org/2005/Atom">
            <title type="text">Blue Mountains Crime Record</title>
            <id>/records/12</id>
            <updated>2018-04-29T04:15:56.629041Z</updated>
            <author>
              <name>admin</name>
            </author>
            <generator>Werkzeug</generator>
          </feed>
        </feed>
    -- test 9 --

    -- test 10 --
    filter 2 test
    query_string = 'lgaName eq Sydney and year eq 2015'
    input:
        1) type 6 to get data using filter 2
        2) type lgaName eq Sydney and year eq 2015
    expected output:
        Status code: 200
        Payload:
        An ATOM feed containing all crime statistics in Sydney of year 2015
    -- test 10 --

    -- test 11 --
    auth test
    PLEASE RESTART CLIENT, and login as guest
    as a guest, my server may only accept 'GET' requests
    try:
        1) import data by name, should get 401
        2) import data by postcode, should get 401
        3) get collection, should get 200 and all collection
        4) get entry of Sydney(cid=109), should get 200 and data entry
        5) delete data, should get 401
        6) all filters should response 200 if the query_string is correct.
    -- test 11 --


    ---- END ----


Client Document:

The sample client provides 6 major functions to test the server:

{
    0: import_data_by_name
    1: import_data_by_postcode
    2: get_all_collection
    3: get_single_entry
    4: del_single_entry
    5: filter_1
    6: filter_2
}

When you run client.py, it will ask you to login first (as admin or guest, passwords are admin or guest respectively)
After that the program will take the token from server, and use it in every function later.

For content type negotiation, if a 'rtype' is asked, please type 'ATOM' or 'JSON'

-- import_data_by_name [POST]
    identity: admin only
    params: token, lgaName(from input), rtype(from input)
    returns: response text from server containing a data entry (201 or 200 for ok, 400 or 404 for error)
    note: lgaName may contain space or other punctuations, which is exactly same as the names on LGA website

-- import_data_by_postcode [POST]
    identity: admin only
    params: token, postcode(from input), rtype(from input)
    returns: response text from server containing a data entry (201 or 200 for ok, 400 or 404 for error)
    note: postcode may map to several LGA names (e.g. 2583),
          for this case I return a list containing all corresponding cities, and suggest user to import them by name

-- get_all_collection [GET]
    identity: admin or guest
    params: token, rtype(from input)
    returns: response text from server containing all data entries (200)

-- get_single_entry [GET]
    identity: admin or guest
    params: token, cid(from input), rtype(from input)
    returns: data entry of required city (200 for ok, 404 if not found)

-- del_single_entry [DELETE]
    identity: admin only
    params: token, cid(from input)
    returns: response text from server (200 for ok, 404 if not found)

-- filter_1 [GET]
    identity: admin or guest
    params: token, query_string (from input, format: lgaName eq Sydney [or lgaName eq Blue Mountains])
    returns: required data entry(entries) (200, 404 if not found)

-- filter_2 [GET]
    identity: admin or guest
    params: token, query_string (from input, format: lgaName eq Sydney and year eq 2015)
    returns: required data entry (200, 404 if not found)
    type 0\n, then type Sydney \n, ATOM/JSON \n


Thank you for reading and running my code,
Tianpeng