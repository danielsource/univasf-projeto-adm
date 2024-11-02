from flask import (
        Blueprint,
        render_template,
        request,
        redirect,
        url_for,
        flash,
        session,
        )
from flask_babel import _

from sqlalchemy import desc

from models.user import Role
from models.product import Product, ProductOrder, ProductTransaction
from models.client import Client
from util import db, requires_role
from config import Config

order_bp = Blueprint('order', __name__, url_prefix='/order')


@order_bp.route('/')
@requires_role(Role.OPERATOR)
def start_page():
    session.pop('order_id', None)

    orders = ProductOrder.query.order_by(desc(ProductOrder.checkout_datetime), desc(ProductOrder.id)).all()
    for order in orders:
        invalid_order = False
        product_ts = ProductTransaction.query.filter_by(order_id=order.id).all()
        if not product_ts:
            invalid_order = True
        for product_t in product_ts:
            if not product_t.is_valid:
                invalid_order = True
                db.session.delete(product_t)
        if invalid_order:
            db.session.delete(order)
            db.session.commit()

    return render_template('order/orders.html', page_title=_('Orders'),
                           orders=orders)


@order_bp.route('/add', methods=['GET', 'POST'])
@requires_role(Role.OPERATOR)
def add_page():
    if not 'order_id' in session:
        order = ProductOrder()
        db.session.add(order)
        db.session.commit()
        session['order_id'] = order.id

    order = ProductOrder.query.get_or_404(session['order_id'])
    products = Product.query.order_by(Product.name).all()
    product_ts = ProductTransaction.query.filter_by(order_id=session['order_id']).all()

    if request.method == 'POST':
        product = Product.query.filter_by(id=int(request.form['product_id'])).first()
        product_t = ProductTransaction(product_id=product.id,
                                       order_id=session['order_id'],
                                       unit_price=product.unit_price,
                                       units=-float(request.form['units']),
                                       is_valid=False)
        db.session.add(product_t)
        db.session.commit()
        return redirect(url_for('order.add_page'))

    return render_template('order/add.html', page_title=_('New order #') + str(session["order_id"]),
                           order=order, products=products, product_ts=product_ts)


@order_bp.route('/finish', methods=['GET', 'POST'])
@requires_role(Role.OPERATOR)
def finish_page():
    clients = Client.query.filter_by(is_deleted=False).order_by(desc(Client.id)).all()

    if request.method == 'POST':
        client_id = request.form['client_id']
        make_pay = 'make-payment' in request.form

        if not make_pay:
            if not client_id:
                flash(_('Client must be identified.'), 'error')
                return redirect(url_for('order.finish_page'))
            unpaid_orders = ProductOrder.query.filter_by(client_id=client_id, is_paid=False).all()
            if len(unpaid_orders) >= Config.MAX_UNPAID_ORDERS:
                flash(_('Customer has exceeded the amount of unpaid orders. Customer needs to make at least one payment.'), 'error')
                return redirect(url_for('order.finish_page'))

        order = ProductOrder.query.get_or_404(session['order_id'])
        if client_id:
            order.client_id = int(client_id)
        order.is_paid = make_pay
        product_ts = ProductTransaction.query.filter_by(order_id=order.id).all()

        try:
            order.add_to_db(*product_ts)
        except ProductOrder.CannotFinishError as e:
            return redirect(url_for('.add_page'))

        session.pop('order_id')
        return redirect(url_for('.start_page'))

    return render_template('order/finish.html', page_title=_('New order #') + str(session["order_id"]),
                           clients=clients)


@order_bp.route('/remove-from-order/<int:id>')
@requires_role(Role.OPERATOR)
def remove_from_order(id):
    product_t = ProductTransaction.query.get_or_404(id)
    db.session.delete(product_t)
    db.session.commit()
    return redirect(url_for('.add_page'))


@order_bp.route('/empty-order/<int:id>')
@requires_role(Role.OPERATOR)
def empty_order(id):
    if not 'order_id' in session:
        return redirect(url_for('.start_page'))
    ProductTransaction.query.filter_by(order_id=session['order_id']).delete(synchronize_session=False)
    db.session.commit()
    return redirect(url_for('.add_page'))


@order_bp.route('/cancel-order/<int:id>')
@requires_role(Role.OPERATOR)
def cancel_order(id):
    if not 'order_id' in session:
        return redirect(url_for('.start_page'))
    ProductTransaction.query.filter_by(order_id=session['order_id']).delete(synchronize_session=False)
    order = ProductOrder.query.get_or_404(session['order_id'])
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('.start_page'))


@order_bp.route('/make-payment/<int:id>')
@requires_role(Role.OPERATOR)
def make_payment(id):
    order = ProductOrder.query.get_or_404(id)
    order.is_paid = True
    db.session.commit()
    return redirect(url_for('.start_page'))
