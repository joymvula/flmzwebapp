from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email
from models import Child, HomeVisit

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('field_officer','Field Officer'),('teacher','Teacher')])
    submit = SubmitField('Register')



class HomeVisitForm(FlaskForm):
    date = DateField("Visit Date", validators=[DataRequired()])
    findings = TextAreaField("Findings", validators=[DataRequired()])
    child_id = SelectField("Child", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        super(HomeVisitForm, self).__init__(*args, **kwargs)
        self.child_id.choices = [(c.id, c.name) for c in Child.query.order_by(Child.name).all()]


class VulnerabilityForm(FlaskForm):
    child_id = SelectField("Child", coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    score = IntegerField('Score', validators=[DataRequired()])
    findings = TextAreaField('Findings', validators=[DataRequired()])  # Added findings field
    submit = SubmitField('Save')
    
    def __init__(self, *args, **kwargs):
        super(VulnerabilityForm, self).__init__(*args, **kwargs)
        self.child_id.choices = [(c.id, c.name) for c in Child.query.order_by(Child.name).all()]


class LiteracyForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    ticks = IntegerField('Total Ticks', validators=[DataRequired()])
    level = StringField('Assessment Level')
    child_id = SelectField("Child", coerce=int, validators=[DataRequired()])

    submit = SubmitField('Save')
    def __init__(self, *args, **kwargs):
        super(LiteracyForm, self).__init__(*args, **kwargs)
        self.child_id.choices = [(c.id, c.name) for c in Child.query.order_by(Child.name).all()]


class IssueForm(FlaskForm):
    child_id = SelectField('Child', coerce=int, validators=[DataRequired()])
    status = SelectField('Status', choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')], validators=[DataRequired()])
    description = TextAreaField('Issue Description', validators=[DataRequired()])
    # findings = TextAreaField('Findings', validators=[DataRequired()])  # Added findings field
    visit_id = SelectField('Visit ID', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Report Issue')

    def __init__(self, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        self.child_id.choices = [(c.id, c.name) for c in Child.query.order_by(Child.name).all()]
        self.visit_id.choices = [(v.id, v.date) for v in HomeVisit.query.all()]

class ChildForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    age = StringField('Age')
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    # guardian_name = StringField('Guardian Name', validators=[DataRequired()])
    # contact_info = StringField('Contact Information', validators=[DataRequired()])
    # address = TextAreaField('Address', validators=[DataRequired()])
    submit = SubmitField('Save')