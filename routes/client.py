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
from models.client import Client
from util import db, requires_role

client_bp = Blueprint('client', __name__, url_prefix='/client')


@client_bp.route('/')
@requires_role(Role.MANAGER,
                       Role.OPERATOR)
def start_page():
    clients = Client.query.order_by(desc(Client.id)).all()
    return render_template('client/clients.html', page_title=_('Clients'),
                           clients=clients)


@client_bp.route('/add', methods=['GET', 'POST'])
@requires_role(Role.MANAGER,
                       Role.OPERATOR)
def add_page():
    back = request.args.get('back')
    if back:
        session['back'] = back

    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phone_number'] or None

        if phone_number and Client.query.filter_by(phone_number=phone_number).first():
            flash(_('Another user already has this phone number.'), 'error')
            return redirect(url_for('.add_page'))

        client = Client(name=name,
                        phone_number=phone_number,
                        is_deleted=False)
        db.session.add(client)
        db.session.commit()
        flash(_('Client added successfully.'), 'info')

        if 'back' in session:
            return redirect(url_for(session.pop('back')))
        else:
            return redirect(url_for('.start_page'))
    return render_template('client/add.html', page_title=_('Add new client'))


@client_bp.route('/update/<int:id>', methods=['GET', 'POST'])
@requires_role(Role.MANAGER,
                       Role.OPERATOR)
def update_page(id):
    client = Client.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phone_number']

        if phone_number != client.phone_number and Client.query.filter_by(phone_number=phone_number).first():
            flash(_('Another user already has this phone number.'), 'error')
            return redirect(url_for('.add_page'))

        client.name = name
        client.phone_number = phone_number
        db.session.commit()
        flash(_('Client updated successfully.'), 'info')
        return redirect(url_for('.start_page'))

    return render_template('client/update.html', page_title=_('Update client "') + client.name + '"',
                           client=client)


@client_bp.route('/delete/<int:id>')
@requires_role(Role.MANAGER,
                       Role.OPERATOR)
def delete_client(id):
    client = Client.query.get_or_404(id)
    client.name = client.phone_number = None
    client.is_deleted = True
    db.session.commit()
    flash(_('Client deleted successfully.'), 'info')
    return redirect(url_for('.start_page'))
