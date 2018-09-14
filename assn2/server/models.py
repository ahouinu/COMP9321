from mongoengine import StringField, IntField, DictField, \
    Document, EmbeddedDocument, ListField, EmbeddedDocumentField


class Entry:
    # id = IntField(required=True, primary_key=True)
    # updated = DateTimeField()
    # author = StringField(required=True, max_length=50)

    def __init__(self, id, title, updated, author, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.title = title
        self.updated = updated
        self.datetime = updated.strftime("%Y-%m-%d %H:%M")
        self.author = author

        # define dict for generating JSON and ATOM
        self._json_dict = {  # 'id': self.id,
                           'title': self.title,
                           'updated': self.datetime,
                           'author': {'name': self.author.username}}
        self._atom_dict = {'id': self.id,
                           'title': self.title,
                           'updated': self.updated,
                           'author': {'name': self.author.username}}


class Record(EmbeddedDocument):
    cid = IntField(required=True)
    id = IntField(required=True, primary_key=True)
    offence_group = StringField(required=True, max_length=100)
    # offence_type = StringField(required=True, max_length=50)
    records_dict = DictField(required=True)

    def __init__(self, cid, id, offence_group, records_dict,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cid = cid
        self.id = id
        self.offence_group = offence_group
        self.records_dict = records_dict
        try:
            self.offence_type = records_dict['Offence type']
        except KeyError:
            print('KeyError when initialising Record object')

        self._atom_str_list = [f'<offence-type>']

        for k, v in self.records_dict.items():

            _str = k.lower().replace(' ', '-').replace(',', '').replace('^', '').replace('*', '')

            if _str == 'offence-type':
                _str = 'name'

            if k[0].isdigit():
                _str = 's-' + _str

            self._atom_str_list.append(f'<{_str}>{v}</{_str}>')

        self._atom_str_list.append('</offence-type>')

    def __str__(self):
        return f'cid: {self.cid}\t id: {self.id}\t offence group: {self.offence_group}' \
               f'records: {self.records_dict}'

    def get_record_by_year(self, year):

        _list = self._atom_str_list[1: -4]
        _res = self._atom_str_list[0: 2]

        for e in _list:
            if str(year) in e[9: 13]:
                _res.append(e)
        _res.append('</offence-type>')

        return _res


class City(Document):
    id = IntField(required=True, primary_key=True)
    name = StringField(required=True, max_length=50)
    # postcodes = ListField(IntField())
    records = ListField(EmbeddedDocumentField(Record))

    def __init__(self, id, name, records=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.name = name
        # self.postcodes = postcodes
        self.records = records

    def __repr__(self):
        return f'id: {self.id}\t LGA name: {self.name} \t records: {self.records}'

    def __str__(self):
        return self.__repr__()

    def get_records_by_year(self, year):

        _str_list = []

        for r in self.records:
            _str_list += r.get_record_by_year(year)
            # _str += '\n'

        return _str_list


class Author:

    def __init__(self, id, username, password, records=[], *args, **values):
        super().__init__(*args, **values)
        self.id = id
        self.username = username
        self.password = password
        self.records = records
