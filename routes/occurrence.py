from flask import (
        g,
        Blueprint,
        render_template,
        request,
        redirect,
        url_for,
        flash,
        session
        )
from flask_babel import _

from sqlalchemy import desc

from models.user import Role
from models.occurrence import Occurrence, OccType
from util import db, requires_role

occurrence_bp = Blueprint('occurrence', __name__, url_prefix='/occurrence')


@occurrence_bp.route('/')
@requires_role(Role.ADMIN,
                       Role.MANAGER)
def start_page():
    occurrences = Occurrence.query.order_by(Occurrence.is_solved, desc(Occurrence.id)).all()
    return render_template('occurrence/occurrences.html', page_title=_('Occurrences'),
                           Role=Role,
                           occurrences=occurrences)


@occurrence_bp.route('/add', methods=['GET', 'POST'])
@requires_role(Role.ADMIN,
                       Role.MANAGER,
                       Role.OPERATOR)
def add_page():
    back = request.args.get('back')
    if back:
        session['back'] = back

    if request.method == 'POST':
        user_id = None
        if 'identify_user' in request.form:
            user_id = g.current_user.id
        type = OccType(request.form['type'])
        text = request.form['text']
        occurrence = Occurrence(user_id=user_id,
                                type=type,
                                text=text,
                                is_solved=False)
        db.session.add(occurrence)
        db.session.commit()
        flash(_('Occurrence added successfully.'), 'info')
        if 'back' in session:
            return redirect(url_for(session.pop('back')))
        else:
            return redirect(url_for('index.start_page'))
    return render_template('occurrence/add.html', page_title=_('Add new occurrence'))


@occurrence_bp.route('/resolve/<int:id>')
@requires_role(Role.ADMIN,
                       Role.MANAGER)
def resolve_page(id):
    occurrence = Occurrence.query.get_or_404(id)
    occurrence.is_solved = True
    db.session.commit()
    flash(_('Occurrence ') + str(id) + _(' is marked as resolved.'), 'info')
    return redirect(url_for('.start_page'))


@occurrence_bp.route('/read/<int:id>')
@requires_role(Role.ADMIN,
                       Role.MANAGER)
def read_page(id):
    occurrence = Occurrence.query.get_or_404(id)
    return occurrence.text


@occurrence_bp.route('/delete/<int:id>')
@requires_role(Role.ADMIN)
def delete(id):
    occurrence = Occurrence.query.get_or_404(id)
    db.session.delete(occurrence)
    db.session.commit()
    return redirect(url_for('.start_page'))
