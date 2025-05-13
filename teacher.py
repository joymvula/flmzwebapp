from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app import db
from models import Child, LiteracyAssessment, Issue
from forms import LiteracyForm
from utils import generate_csv
from weasyprint import HTML

bp = Blueprint('teacher', __name__)

@bp.route('/literacy', methods=['GET', 'POST'])
@login_required
def literacy():
    assert current_user.role == 'teacher'
    form = LiteracyForm()
    form.child_id.choices = [(c.id, c.name) for c in Child.query.all()]
    if form.validate_on_submit():
        record = LiteracyAssessment(child_id=form.child_id.data, date=form.date.data,
                                    ticks=form.ticks.data, level=form.level.data)
        db.session.add(record)
        db.session.commit()
        flash('Literacy assessment saved.')
        return redirect(url_for('teacher.literacy'))
    history = LiteracyAssessment.query.filter_by(child_id=form.child_id.data).all() if form.child_id.data else []
    return render_template('teacher/literacy_assessment.html', form=form, history=history)

@bp.route('/issues/followup/<int:issue_id>', methods=['POST'])
@login_required
def followup_issue(issue_id):
    assert current_user.role in ['teacher','field_officer']
    issue = Issue.query.get_or_404(issue_id)
    issue.status = request.form.get('status', issue.status)
    db.session.commit()
    flash('Issue status updated.')
    return redirect(request.referrer)

@bp.route('/report/literacy')
@login_required
def literacy_report():
    data = LiteracyAssessment.query.all()
    csv_path = generate_csv(data, 'literacy')
    html = render_template('teacher/literacy_report.html', data=data)
    pdf_path = '/tmp/literacy_report.pdf'
    HTML(string=html).write_pdf(pdf_path)
    return send_file(pdf_path, as_attachment=True, attachment_filename='literacy_report.pdf')


@bp.route('/literacy/new', methods=['GET', 'POST'])
@login_required
def new_literacy():
    form = LiteracyForm()
    if form.validate_on_submit():
        entry = LiteracyAssessment(
            date=form.date.data,
            ticks=form.ticks.data,
            level=form.level.data,
            child_id=form.child_id.data
        )
        db.session.add(entry)
        db.session.commit()
        flash('Literacy assessment submitted.', 'success')
        return redirect(url_for('dashboard.index'))
    return render_template('dashboard.index', literacy_form=form)
