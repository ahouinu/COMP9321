from flask import Flask, jsonify, redirect, url_for
from flask_restful import reqparse
from datetime import datetime

app = Flask(__name__)
order_list = []
payment_list = []
# next_order_id = 0

price_dict = {'LongBlack': 4.00,
              'Latte': 4.50,
              'FlatWhite': 4.50,
              'Espresso': 3.50,
              'Mocha': 5.00,
              'Macchiato': 4.00}

status_dict = {-1: 'Od Cancelled',
              0: 'Od Received',
              1: 'Od Placed, Processing Payment',
              2: 'Paid',
              3: 'Making Drink',
              4: 'Drink Made',  # Not used
              5: 'Drink Served'}


class Order:

    def __init__(self, id, type, size, cost, additions=[]):
        self.id = id
        self.type = type
        self.size = size
        self.cost = cost
        self.additions = additions
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.status = 1  # created
        self.paid = False

    def __str__(self):
        return f'id: {self.id}\t type: {self.type}\t size: {self.size}\t ' \
               f'cost: {self.cost}\t additions: {self.additions}\t datetime: {self.datetime}\n'

    def __repr__(self):
        return self.__str__()


class Payment:

    def __init__(self, id, type, amount, card_details=None):
        self.id = id
        self.type = type
        if self.type == 'card':
            self.card_details = card_details
        else:
            self.card_details = None
        self.amount = amount
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M")

    def __str__(self):
        return f'id: {self.id}\ttype: {self.type}\t amount: {self.type}\t card details: {self.card_details}\t ' \
               f'datetime: {self.datetime}\n'

    def __repr__(self):
        return self.__str__()


@app.route("/orders", methods=['POST'])
def create_order():
    id = len(order_list)
    parser = reqparse.RequestParser()
    parser.add_argument('type', type=str, required=True)
    parser.add_argument('size', type=str, required=True)
    parser.add_argument('additions', type=str, action='append')
    args = parser.parse_args()
    type = args.get('type')
    size = args.get('size')
    cost = price_dict[type]
    if size == 'Large':
        cost += 0.50
    else:
        size = 'Small'
    additions = args['additions']
    order_list.append(Order(id, type, size, cost, additions))
    print(order_list[id])     # print to server console
    return jsonify(id=id, type=type, size=size, cost=cost, extra=additions, datetime=order_list[id].datetime,
                   payment_link=url_for('create_payment', id=id)), 201


# @app.route("/orders", methods=['GET'])
# def get_orders():
#     response = jsonify([od.__dict__ for od in order_list])
#     response.headers._list.append(('Access-Control-Allow-Origin', '*'))
#     return response


@app.route("/orders", methods=['GET'])
def get_orders_by_status():
    parser = reqparse.RequestParser()
    parser.add_argument('status', type=int)
    args = parser.parse_args()
    status = args.get('status')
    if status not in status_dict.keys():
        return jsonify(message='BadRequest'), 400
    od_list = []
    for od in order_list:
        if od.status == status:
            od_list.append(od.__dict__)
    response = jsonify(od_list)
    response.headers._list.append(('Access-Control-Allow-Origin', '*'))
    return response, 200


@app.route("/orders/<int:id>", methods=['GET'])
def get_order(id):
    if id < len(order_list):
        return jsonify(order_list[id].__dict__), 200
    return jsonify(message='Not Found'), 404


@app.route("/orders/<int:id>", methods=['DELETE'])
def cancel_order(id):
    if order_list[id].paid:
        return jsonify(message='Already Paid'), 400
    if id < len(order_list):
        order_list[id].status = -1     # put -1 for order cancelled
        return jsonify(id=id, message='Order Cancelled'), 200
    return jsonify(message='Not Found'), 404


@app.route("/orders/<int:id>", methods=['PUT'])
def update_order(id):
    id = int(id)
    if id < len(order_list):
        # get previous order
        order = order_list[id]
        if order.status > 1 or order.paid:
            return jsonify(message='Already Paid'), 400
        # get updated requests
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str)
        parser.add_argument('size', type=str)
        parser.add_argument('additions', type=str, action='append')
        args = parser.parse_args()
        type = args.get('type')
        size = args.get('size')
        # cost = price_dict[type]
        additions = args['additions']
        if type is not None:
            order.type = type
        if size is not None:
            order.size = size
        order.cost = price_dict[order.type]
        if order.size == 'Large':
            order.cost += 0.50
        else:
            order.size = 'Small'
        if order.additions is None:
            order.additions = additions
        elif additions is not None:
            order.additions.extend(additions)
        order.datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
        print(order_list[id])  # print to server console
        return jsonify(id=order.id, type=order.type, size=order.size, cost=order.cost, extra=order.additions,
                       datetime=order.datetime, payment_link=url_for('create_payment', id=id)), 200
    else:
        return jsonify(message='Not Found'), 404


@app.route("/payments/<int:id>", methods=['POST'])
def create_payment(id):
    id = int(id)
    if id >= len(order_list):
        return jsonify(message='Not Found'), 404
    order = order_list[id]
    if order.status != 1:
        return jsonify(message='Bad Order'), 400
    if order.status == -1:
        # if this order has been cancelled
        payment_list.append(None)
        return jsonify(message='Order Cancelled'), 201
    parser = reqparse.RequestParser()
    parser.add_argument('type', type=str, required=True)
    parser.add_argument('amount', type=float, required=True)
    parser.add_argument('card_details', type=str, action='append')
    args = parser.parse_args()
    type = args.get('type')
    amount = args.get('amount')
    card_details = args.get('card_details')
    payment_list.append(Payment(id, type, amount, card_details))
    if amount != order.cost:
        return jsonify(message='Wrong Amount'), 400
    print(payment_list[id])  # print to server console
    order.status += 1
    order.paid = True
    return jsonify(id=id, type=type, amount=amount, card_details=card_details, datetime=payment_list[id].datetime), 201


# for baristas
# use get_orders_by_status() instead
# @app.route("/orders", methods=['GET'])
# def baristas_get_orders():
#     od_list = []
#     for od in order_list:
#         if od.status > 0:   # if order has been created
#             od_list.append(od.__dict__)
#     response = jsonify(od_list)
#     response.headers._list.append(('Access-Control-Allow-Origin', '*'))
#     return response


@app.route("/orders/open", methods=['GET'])
def get_open_orders():
    od_list = []
    for od in order_list:
        if od.status in range(3):
            od_list.append(od.__dict__)
    response = jsonify(od_list)
    response.headers._list.append(('Access-Control-Allow-Origin', '*'))
    return response, 200

@app.route("/orders/<int:id>/choose", methods=['PUT'])
def choose_order(id):
    # id = int(id)
    if id > len(order_list):
        return jsonify(message='Not Found'), 404
    order = order_list[id]
    if order.status != 2:
        return jsonify(message='Bad Order'), 400
    order.status = 3
    print(order)  # print to server console
    return jsonify(id=order.id, type=order.type, size=order.size, additions=order.additions,
                   status=status_dict[order.status], createdtime=order.datetime,
                   check_payment=url_for('get_payment', id=id)), 200


# @app.route("/orders/<id>/make", methods=['PUT'])
# def make_drink(id):
#     id = int(id)
#     if id > len(order_list):
#         return jsonify(message='Not Found'), 404
#     order = order_list[id]
#     if order.status < 1:
#         return jsonify(message='Bad Order'), 400
#     order.status = 4
#     print(order)  # print to server console
#     return jsonify(id=order.id, type=order.type, size=order.size, additions=order.additions,
#                    status=status_dict[order.status], createdtime=order.datetime, ), 200


@app.route("/payments/<int:id>", methods=['GET'])
def get_payment(id):
    id = int(id)
    if id > min(len(payment_list), len(order_list)):
        return jsonify(message='Not Found'), 404
    order = order_list[id]
    payment = payment_list[id]
    return jsonify(id=payment.id, amount=payment.amount, datetime=payment.datetime, paid=order.paid), 200


@app.route("/orders/<int:id>/release", methods=['PUT'])
def release_drink(id):
    id = int(id)
    if id > len(order_list):
        return jsonify(message='Not Found'), 404
    order = order_list[id]
    if order.status != 3 or order.paid is False:
        return jsonify(message='Bad Order'), 400
    order.status = 5
    print(order)  # print to server console
    return jsonify(id=order.id, type=order.type, size=order.size, additions=order.additions,
                   status=status_dict[order.status], createdtime=order.datetime, ), 200


if __name__ == "__main__":
    app.run()
