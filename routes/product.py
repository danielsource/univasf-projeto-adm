import io

from flask import (
        Blueprint,
        render_template,
        request,
        redirect,
        url_for,
        flash,
        send_file,
        )
from flask_babel import _

from sqlalchemy import desc

from models.user import Role
from models.product import Product, ProductOrder, ProductTransaction
from util import db, requires_role

product_bp = Blueprint('product', __name__, url_prefix='/product')


@product_bp.route('/')
@requires_role(Role.MANAGER)
def start_page():
    products = Product.query.order_by(desc(Product.units_sold), desc(Product.id), Product.name).all()
    for product in products:
        if product.units_stored < product.units_min:
            flash(_('Product "') + product.name + _('" has less than minimum quantity.'), 'warn')
    return render_template('product/products.html', page_title=_('Products'),
                           products=products)


@product_bp.route('/add', methods=['GET', 'POST'])
@requires_role(Role.MANAGER)
def add_page():
    if request.method == 'POST':
        name = request.form['name']

        if Product.query.filter_by(name=name).first():
            flash(_('Product "') + name + _('" already exists.'), 'error')
            return redirect(url_for('.add_page'))

        product = Product.add_to_db(name=name,
                                    unit_price=int(float(request.form['unit_price']) * 100),
                                    units_stored=int(request.form['units_stored']),
                                    units_min=int(request.form['units_min']),
                                    units_sold=0)
        flash(_('Product #') + str(product.id) + _(' added successfully.'), 'info')
        return redirect(url_for('.start_page'))

    return render_template('product/add.html', page_title=_('Add new product'))


@product_bp.route('/update/<int:id>', methods=['GET', 'POST'])
@requires_role(Role.MANAGER)
def update_page(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form['name']

        if name != product.name and Product.query.filter_by(name=name).first():
            flash(_('Product "') + name + _('" already exists.'), 'error')
            return redirect(url_for('.start_page'))

        product.name = name
        product.unit_price = int(float(request.form['unit_price']) * 100)
        units_stored = int(request.form['units_stored'])
        product.units_min = int(request.form['units_min'])
        product_t = ProductTransaction(product_id=product.id,
                                       order_id=None,
                                       unit_price=product.unit_price,
                                       units=units_stored - product.units_stored,
                                       is_valid=True)
        product.units_stored = units_stored
        db.session.add(product_t)
        db.session.commit()
        flash(_('Product updated successfully.'), 'info')
        return redirect(url_for('.start_page'))

    return render_template('product/update.html', page_title=_('Update product ') + '"' + product.name + '"',
                           product=product)


@product_bp.route('/transactions')
@requires_role(Role.MANAGER)
def transactions_page():
    product_ts = ProductTransaction.query.order_by(desc(ProductTransaction.id)).all()
    return render_template('product/transactions.html', page_title=_('Stock changes'),
                           product_ts=product_ts)


@product_bp.route('/delete/<int:id>')
@requires_role(Role.MANAGER)
def delete_product(id):
    product = Product.query.get_or_404(id)
    ProductTransaction.query.filter_by(product_id=id).delete(synchronize_session=False)
    db.session.delete(product)
    db.session.commit()
    flash(_('Product deleted successfully.'), 'info')
    return redirect(url_for('.start_page'))


@product_bp.route('/download_arff_data')
@requires_role(Role.MANAGER)
def download_arff_data():
    title = 'product_orders'
    product_names = [name[0] for name in db.session.query(Product.name).order_by(Product.id).all()]
    header = f'@relation {title}'
    attributes = '\n'.join(f'@attribute "{name}" {{sim}}' for name in product_names)
    data_header = '@data'

    orders = ProductOrder.query.all()
    data_lines = []
    for order in orders:
        data_line = ['?'] * len(product_names)
        for product_t in order.products:
            name = product_t.product.name
            if name in product_names:
                idx = product_names.index(name)
                data_line[idx] = 'sim'
        data_lines.append(','.join(data_line))

    arff_content = f'{header}\n\n{attributes}\n\n{data_header}\n' + '\n'.join(data_lines)
    file_stream = io.BytesIO()
    file_stream.write(arff_content.encode('utf-8'))
    file_stream.seek(0)
    return send_file(file_stream, as_attachment=True, download_name=f'{title}.arff', mimetype='text/plain')
