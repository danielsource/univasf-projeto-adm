from datetime import datetime
from enum import Enum

from util import db


class Product(db.Model):
    __tablename__ = 'Product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)
    units_stored = db.Column(db.Integer, nullable=False)
    units_min = db.Column(db.Integer, nullable=False)
    units_sold = db.Column(db.Integer, nullable=False, default=0)
    transactions = db.relationship('ProductTransaction', backref='product')

    @classmethod
    def add_to_db(cls, **new_product_attrs):
        product = cls(**new_product_attrs)
        db.session.add(product)
        db.session.commit()

        product_t = ProductTransaction(product_id=product.id,
                                       order_id=None,
                                       unit_price=product.unit_price,
                                       units=product.units_stored,
                                       is_valid=True)
        db.session.add(product_t)
        db.session.commit()
        return product

    def __repr__(self):
        return f'<Product id={self.id} name={self.name}>'


class ProductOrder(db.Model):
    __tablename__ = 'ProductOrder'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer,
                           db.ForeignKey('Client.id'),
                           nullable=True)
    value = db.Column(db.Integer, nullable=False, default=0)
    is_paid = db.Column(db.Boolean, nullable=True)
    checkout_datetime = db.Column(db.DateTime, nullable=True)
    products = db.relationship('ProductTransaction', backref='order')

    class NotEnoughUnitsError(Exception):
        def __init__(self, product_t):
            self.product_t = product_t
            self.message = f'Product "{product_t.product.name}" does not have enough units.'
            super().__init__(self.message)

    class CannotFinishError(Exception):
        def __init__(self, order):
            self.order = order
            self.message = f'Order #{order.id} cannot be finished.'
            super().__init__(self.message)

    def add_to_db(self, order, *product_transactions):
        err = False
        for product_t in product_transactions:
            try:
                if abs(product_t.units) > product_t.product.units_stored:
                    raise NotEnoughUnits(product_t)
                product_t.product.units_stored -= abs(product_t.units)
                product_t.product.units_sold += abs(product_t.units)
                product_t.is_valid = True
                order.value += product_t.total_price
            except NotEnoughUnitsError as e:
                err = True
                print('NotEnoughUnitsError: {e.message}', file=sys.stderr)
                flash(e.message, 'error')
        if err:
            db.session.rollback()
            raise CannotFinishError(order)
        order.checkout_datetime = datetime.now()
        db.session.commit()

    def __repr__(self):
        return f'<ProductOrder id={self.id} client_id={self.client_id}>'


class ProductTransaction(db.Model):
    __tablename__ = 'ProductTransaction'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('Product.id'),
                           nullable=False)
    order_id = db.Column(db.Integer,
                           db.ForeignKey('ProductOrder.id'),
                           nullable=True)
    unit_price = db.Column(db.Integer, nullable=False)
    units = db.Column(db.Integer, nullable=False)
    is_valid = db.Column(db.Boolean, nullable=False)

    @property
    def total_price(self):
        return self.unit_price * abs(self.units)

    def __repr__(self):
        return f'<ProductTransaction id={self.id} product_id={self.product_id} order_id={self.order_id}>'