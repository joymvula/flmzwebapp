from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, Response, abort
from flask_login import login_required, current_user
from app import db
from models import Child, HomeVisit, Vulnerability, Issue, LiteracyAssessment
from forms import HomeVisitForm, VulnerabilityForm, IssueForm, ChildForm
from utils import eliminate_redundant_fields, generate_csv
from weasyprint import HTML
from datetime import datetime

bp = Blueprint('fo', __name__)


@bp.route('/child/new', methods=['GET', 'POST'])
@login_required
def new_child():
    # assert current_user.role == 'field_officer'
    child_form = ChildForm()
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        if not name or not age or not gender:
            flash('All fields are required.', 'danger')
            # return redirect(url_for('fo.new_child'))
            return redirect(url_for('dashboard.index'))
        child = Child(name=name, age=age, gender=gender)
        db.session.add(child)
        db.session.commit()
        flash('Child added successfully.', 'success')
        # return redirect(url_for('fo.new_child'))
        return redirect(url_for('dashboard.index'))
    # return render_template('dashboard.html', child_form=child_form)

@bp.route('/home_visit', methods=['GET', 'POST'])
@login_required
def home_visit():
    assert current_user.role == 'field_officer'
    form = HomeVisitForm()
    form.child_id.choices = [(c.id, c.name) for c in Child.query.all()]
    if form.validate_on_submit():
        # smart question filter
        data = eliminate_redundant_fields(form.data, 'home_visit')
        visit = HomeVisit(child_id=form.child_id.data, date=form.date.data, findings=data['findings'])
        db.session.add(visit)
        db.session.commit()
        flash('Home visit saved.')
        return redirect(url_for('dashboard.index'))
    history = HomeVisit.query.filter_by(child_id=form.child_id.data).all() if form.child_id.data else []
    return render_template('dashboard.index', visit_form=form, history=history)

@bp.route('/vulnerability', methods=['GET', 'POST'])
@login_required
def vulnerability():
    assert current_user.role == 'field_officer'
    form = VulnerabilityForm()
    form.child_id.choices = [(c.id, c.name) for c in Child.query.all()]
    if form.validate_on_submit():
        record = Vulnerability(child_id=form.child_id.data, date=form.date.data, score=form.score.data)
        db.session.add(record)
        db.session.commit()
        flash('Vulnerability assessment saved.')
        return redirect(url_for('dashboard.index'))
    history = Vulnerability.query.filter_by(child_id=form.child_id.data).all() if form.child_id.data else []
    return render_template('dashboard.index', vuln_form=form, history=history)

@bp.route('/issues')
@login_required
def issues():
    assert current_user.role == 'field_officer'
    issues = Issue.query.filter_by(status='open').all()
    return render_template('field_officer/issues.html', issues=issues)

@bp.route('/report/<string:report_type>')
@login_required
def report(report_type):
    # report_type: 'home_visit' or 'vulnerability'
    if report_type == 'home_visit':
        data = HomeVisit.query.all()
    else:
        data = Vulnerability.query.all()
    # csv_path = generate_csv(data, report_type)

    csv_path = generate_csv(data, report_type)
    pdf_html = render_template(f'field_officer/{report_type}_report.html', data=data)
    pdf_path = f'/tmp/{report_type}_report.pdf'
    HTML(string=pdf_html).write_pdf(pdf_path)
    # send both as zip or individual
    return send_file(pdf_path, as_attachment=True, download_name=f"{report_type}_report.pdf")
    # return send_file(csv_path, as_attachment=True, attachment_filename=f"{report_type}_report.csv")

@bp.route('/visits/<int:visit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_visit(visit_id):
    visit = HomeVisit.query.get_or_404(visit_id)
    form = HomeVisitForm(obj=visit)

    if form.validate_on_submit():
        visit.date = form.date.data
        visit.findings = form.findings.data
        visit.child_id = form.child_id.data
        db.session.commit()
        flash("Visit updated successfully.", "success")
        return redirect(url_for('fo.view_visits'))

    return render_template('field_officer/edit_visit.html', form=form, visit=visit)


@bp.route('/visits/<int:visit_id>/delete')
@login_required
def delete_visit(visit_id):
    visit = HomeVisit.query.get_or_404(visit_id)
    db.session.delete(visit)
    db.session.commit()
    flash("Visit deleted.", "success")
    return redirect(url_for('fo.view_visits'))

@bp.route('/visits/export/<format>')
@login_required
def export_visits(format):
    visits = HomeVisit.query.order_by(HomeVisit.date.desc()).all()
    try:
        if format == 'csv':
            file_path = generate_csv(visits, 'home_visit')
            return send_file(file_path, as_attachment=True)
        elif format == 'pdf':

            assessment_data = {
                'report_date': datetime.now().strftime("%A, %B %d, %Y"),
                'assessment_date': "Thursday, May 30, 2024",
                'assessor': {
                    'id': 45,
                    'name': "Joy Musweu",
                    'gender': "Femail",
                    'supervisor': "Emmanuel Mkandawire"
                },
                'teacher': {
                    'id': 211197,
                    'name': "Demo Teacher",
                    'supervisor': "Demo Supervisor"
                },
                'child': {
                    'id': 202020,
                    'name': "Gile Phir",
                    'grade': "Grade 2",
                    'school': "Chainda LA"
                },
                'criteria': [{'passed': i > 22} for i in range(26)],
                'sight_words': 150,
                'total_ticks': 23,
                'assessment_score': "Assessment point",
                'interpretations': [
                    {'label': 'NOT YET WORKING...', 'range': '0-5 TICKS', 'active': False},
                    {'label': 'DEVELOPING...', 'range': '6-12 TICKS', 'active': False},
                    {'label': 'SECURE...', 'range': '13-21 TICKS', 'active': False},
                    {'label': 'ADVANCED...', 'range': '22-26 TICKS', 'active': True}
                ]
            }
            
            # Render the template with the dynamic data
            rendered = render_template('assessment_report.html', data=assessment_data)
            pdf = HTML(string=rendered).write_pdf()

            return Response(pdf, mimetype='application/pdf',
                            headers={'Content-Disposition': 'attachment; filename="home_visits.pdf"'})
        else:
            abort(400, "Unsupported format")
    except Exception as e:

        # Log the error and return a user-friendly message
        print(f"Error exporting visits: {e}")
        flash("An error occurred while exporting visits.", "danger")
        return redirect(url_for('dashboard.index'))


@bp.route('/vulns/export/<format>')
@login_required
def export_vulns(format):
    vulns = Vulnerability.query.order_by(Vulnerability.date.desc()).all()
    try:
        if format == 'csv':
            file_path = generate_csv(vulns, 'home_visit')
            return send_file(file_path, as_attachment=True)
        elif format == 'pdf':
            rendered = render_template('dashboard.index', vulns=vulns)
            pdf = HTML(string=rendered).write_pdf()
            return Response(pdf, mimetype='application/pdf',
                            headers={'Content-Disposition': 'attachment; filename="vulnerabilities.pdf"'})
        else:
            abort(400, "Unsupported format")
    except Exception as e:
        # Log the error and return a user-friendly message
        print(f"Error exporting visits: {e}")
        flash("An error occurred while exporting visits.", "danger")
        return redirect(url_for('dashboard.index'))

@bp.route('/lits/export/<format>')
@login_required
def export_lits(format):
    lits = LiteracyAssessment.query.order_by(LiteracyAssessment.date.desc()).all()
    try:
        if format == 'csv':
            file_path = generate_csv(lits, 'home_visit')
            return send_file(file_path, as_attachment=True)
        elif format == 'pdf':
            rendered = render_template('dashboard.index', lits=lits)
            pdf = HTML(string=rendered).write_pdf()
            return Response(pdf, mimetype='application/pdf',
                            headers={'Content-Disposition': 'attachment; filename="literacy_assesments.pdf"'})
        else:
            abort(400, "Unsupported format")
    except Exception as e:
        # Log the error and return a user-friendly message
        print(f"Error exporting visits: {e}")
        flash("An error occurred while exporting visits.", "danger")
        return redirect(url_for('dashboard.index'))
    
# --- Home Visit ---
@bp.route('/visit/new', methods=['GET', 'POST'])
@login_required
def new_visit():
    form = HomeVisitForm()
    if form.validate_on_submit():
        visit = HomeVisit(
            date=form.date.data,
            findings=form.findings.data,
            child_id=form.child_id.data
        )
        db.session.add(visit)
        db.session.commit()
        flash('Home visit added.', 'success')
        return redirect(url_for('dashboard.index'))
    return render_template('field_officer/home_visit_form.html', visit_form=form)

# --- Vulnerability Assessment ---
@bp.route('/vulnerability/new', methods=['GET', 'POST'])
@login_required
def new_vulnerability():
    form = VulnerabilityForm()
    if form.validate_on_submit():
        assessment = Vulnerability(
            date=form.date.data,
            score=form.score.data,
            data=form.findings.data,
            child_id=form.child_id.data
        )
        db.session.add(assessment)
        db.session.commit()
        flash('Vulnerability assessment added.', 'success')
        return redirect(url_for('dashboard.index'))
    return render_template('field_officer/vulnerability.html', form=form)

# --- New Issue ---
@bp.route('/issue/new', methods=['GET', 'POST'])
@login_required
def new_issue():
    form = IssueForm()
    if form.validate_on_submit():
        issue = Issue(
            description=form.description.data,
            status=form.status.data,
            child_id=form.child_id.data,
            visit_id=form.visit_id.data
        )
        db.session.add(issue)
        db.session.commit()
        flash('Issue logged.', 'success')
        return redirect(url_for('dashboard.index'))
    return render_template('field_officer/issues.html', issue_form=form)
