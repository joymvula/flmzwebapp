from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from forms import LoginForm, RegistrationForm, ChildForm, HomeVisitForm, VulnerabilityForm, IssueForm, LiteracyForm
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    child_form = ChildForm()
    visit_form = HomeVisitForm()
    vuln_form = VulnerabilityForm()
    literacy_form = LiteracyForm()
    issue_form = IssueForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard.index'))
        flash('Invalid credentials')
    return render_template('auth/login.html', form=form, child_form=child_form, visit_form=visit_form, vuln_form=vuln_form, literacy_form=literacy_form, issue_form=issue_form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    assert current_user.role == 'admin'
    form = RegistrationForm()
    child_form = ChildForm()
    visit_form = HomeVisitForm()
    vuln_form = VulnerabilityForm()
    literacy_form = LiteracyForm()
    issue_form = IssueForm()
    if form.validate_on_submit():
        u = User(email=form.email.data,
                 password_hash=generate_password_hash(form.password.data),
                 role=form.role.data)
        db.session.add(u)
        db.session.commit()
        flash('User created.')
        return redirect(url_for('auth.manage_users'))
    return render_template('auth/register.html', form=form, child_form=child_form, visit_form=visit_form, vuln_form=vuln_form, literacy_form=literacy_form, issue_form=issue_form)

@bp.route('/manage_users')
@login_required
def manage_users():
    assert current_user.role == 'admin'
    users = User.query.all()
    child_form = ChildForm()
    visit_form = HomeVisitForm()
    vuln_form = VulnerabilityForm()
    literacy_form = LiteracyForm()
    issue_form = IssueForm()
    return render_template('auth/manage_users.html', users=users, child_form=child_form, visit_form=visit_form, vuln_form=vuln_form, literacy_form=literacy_form, issue_form=issue_form)

@bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    assert current_user.role == 'admin'
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    flash('User deleted.')
    return redirect(url_for('auth.manage_users'))
