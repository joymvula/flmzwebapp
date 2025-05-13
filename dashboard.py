# flask_legacy_app/routes/dashboard.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from extensions import db
from models import Child, HomeVisit, Vulnerability, LiteracyAssessment, Issue
from forms import ChildForm, HomeVisitForm, VulnerabilityForm, LiteracyForm, IssueForm

bp = Blueprint('dashboard', __name__, template_folder='../templates')
@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # Aggregate metrics
    total_children = Child.query.count()
    total_visits = HomeVisit.query.count()
    total_vulns = Vulnerability.query.count()
    total_literacies = LiteracyAssessment.query.count()
    total_issues = Issue.query.count()

    # Recent records (for tables)
    recent_visits = HomeVisit.query.order_by(HomeVisit.date.desc()).limit(5).all()
    recent_vulns = Vulnerability.query.order_by(Vulnerability.date.desc()).limit(5).all()
    recent_literacies = LiteracyAssessment.query.order_by(LiteracyAssessment.date.desc()).limit(5).all()
    recent_issues = Issue.query.order_by(Issue.created_at.desc()).limit(5).all()

    # Data for charts
    visits_by_month = (
        db.session.query(
            db.func.strftime('%Y-%m', HomeVisit.date).label('date'),
            db.func.count(HomeVisit.id).label('count')
        )
        .group_by('date')
        .order_by('date')
        .all()
    )
    vulns_by_month = (
        db.session.query(
            db.func.strftime('%Y-%m', Vulnerability.date).label('date'),
            db.func.avg(Vulnerability.score).label('score')
        )
        .group_by('date')
        .order_by('date')
        .all()
    )
    lits_by_month = (
        db.session.query(
            db.func.strftime('%Y-%m', LiteracyAssessment.date).label('date'),
            db.func.sum(LiteracyAssessment.ticks).label('ticks')
        )
        .group_by('date')
        .order_by('date')
        .all()
    )

    # Convert query results to dictionaries for JSON serialization
    visits = [{'date': v[0], 'count': v[1]} for v in visits_by_month]
    vulns = [{'date': v[0], 'score': round(v[1], 2)} for v in vulns_by_month]
    lits = [{'date': l[0], 'ticks': l[1]} for l in lits_by_month]

    child_form = ChildForm()
    visit_form = HomeVisitForm()
    vuln_form = VulnerabilityForm()
    literacy_form = LiteracyForm()
    issue_form = IssueForm()

    return render_template(
        'dashboard.html',
        current_user=current_user,
        # counts
        total_children=total_children,
        total_visits=total_visits,
        total_vulns=total_vulns,
        total_literacies=total_literacies,
        total_issues=total_issues,
        # tables
        recent_visits=recent_visits,
        recent_vulns=recent_vulns,
        recent_literacies=recent_literacies,
        recent_issues=recent_issues,
        # chart data
        visits=visits,
        vulns=vulns,
        lits=lits,
        # forms
        child_form=child_form,
        visit_form=visit_form,
        vuln_form=vuln_form,
        literacy_form=literacy_form,
        issue_form=issue_form
    )
