
from datetime import datetime
from flask_login import UserMixin
from flask import Flask
from app import db, login_manager
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://addatsco_geox_user:Addatgeox??@162.214.195.234/addatsco_geox_dashboard'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



class Users(db.Model, UserMixin):

    id            = db.Column(db.Integer, primary_key=True)
    role      = db.Column(db.String(250), unique=False)
    fname      = db.Column(db.String(250), unique=False)
    lname      = db.Column(db.String(250), unique=False)
    email         = db.Column(db.String(250), unique=True)
    password      = db.Column(db.String(250))
    designation      = db.Column(db.String(250), unique=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            # if property == 'password':
            #     value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.fname)


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    user = Users.query.filter_by(email=email).first()
    return user if user else None



class allforms_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    form_id = db.Column(db.Integer, nullable=True)
    filledby = db.Column(db.String(500), nullable=True)
    belongsto = db.Column(db.String(500), nullable=True)
    form_type = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.name)

    def get_related_form(self):
        if self.form_type == 'New Deals Contract Signed':
            return Marketing.query.get(self.form_id)
        elif self.form_type == 'Person Placement':
            return recruiting_data.query.get(self.form_id)
        else:
            return None

    def delete(self):
        related_form = self.get_related_form()
        if related_form:
            db.session.delete(related_form)
        db.session.delete(self)
        db.session.commit()

class userdesignation_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(500))

    def __repr__(self):
        return "{}".format(self.designation)
        return "{}".format(self.designation)


class Emails_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    subject_part1 = db.Column(db.String(255), nullable=False)
    subject_part2 = db.Column(db.String(255), nullable=False)
    formatted_date = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_content = db.Column(db.LargeBinary, nullable=True)
    phone_number = db.Column(db.String(255), nullable=True)
    action = db.Column(db.String(500), nullable=False, default='user')
    status = db.Column(db.String(500), nullable=False, default='applied')
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "{} - {}".format(self.name, self.subject)


class Hrforms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(500), nullable=True)
    candidate_name = db.Column(db.String(500), nullable=True)
    late = db.Column(db.String(500), nullable=True)
    informed = db.Column(db.String(500), nullable=True)
    otherreport = db.Column(db.String(500), nullable=True)
    reason_vacation = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.user_id, self.name)

class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(500), nullable=True)
    title = db.Column(db.String(500), nullable=True)
    image = db.Column(db.String(500), nullable=True)
    company = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(500), nullable=True)
    job_type = db.Column(db.String(500), nullable=True)
    duration = db.Column(db.String(500), nullable=True)
    onsite = db.Column(db.String(500), nullable=True)
    salary_type = db.Column(db.String(500), nullable=True)
    salary = db.Column(db.String(500), nullable=True)
    job_date = db.Column(db.String(500), nullable=True)
    job_status = db.Column(db.String(500), nullable=True)
    description = db.Column(db.String(700), nullable=True)
    responsibility = db.Column(db.String(700), nullable=True)
    eligibility = db.Column(db.String(700), nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.user_id, self.name)



class Marketing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(500), nullable=True)
    company = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(500), nullable=True)
    cperson = db.Column(db.String(500), nullable=True)
    cphone = db.Column(db.Integer, nullable=True)
    location = db.Column(db.String(500), nullable=True)
    Markup = db.Column(db.Integer, nullable=True)
    otherReport = db.Column(db.Text(1000), nullable=True)
    company_status = db.Column(db.String(500))
    Notes = db.Column(db.Text(1000), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.user_id, self.name)



class Otherfinal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(500), nullable=True)
    other_report = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.user_id, self.name)



class recruiting_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(500), nullable=True)
    candidate = db.Column(db.String(500), nullable=True)
    phone = db.Column(db.Integer, nullable=True)
    company = db.Column(db.String(500), nullable=True)
    did_you = db.Column(db.String(500), nullable=True)
    ecname = db.Column(db.String(500), nullable=True)
    ecnumber = db.Column(db.Integer, nullable=True)
    location = db.Column(db.String(500), nullable=True)
    locationcgoing = db.Column(db.String(500), nullable=True)
    starttime = db.Column(db.String(500), nullable=True)
    needmember = db.Column(db.String(500), nullable=True)
    photo = db.Column(db.String(500), nullable=True)
    interviewdate = db.Column(db.String(500), nullable=True)
    companydate = db.Column(db.String(500), nullable=True)
    help = db.Column(db.String(500), nullable=True)
    person_starting = db.Column(db.String(500), nullable=True)
    other_report = db.Column(db.String(500), nullable=True)
    position = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.name, self.subject)


class Joborder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(250), nullable=False)
    company_id = db.Column(db.String(500), nullable=True)
    payrate = db.Column(db.Integer, nullable=True)
    jobstatus = db.Column(db.String(500), nullable=True)
    title = db.Column(db.String(500), nullable=True)
    salarytype = db.Column(db.String(500), nullable=True)
    starttime = db.Column(db.String(500), nullable=True)
    endtime = db.Column(db.String(500), nullable=True)
    vacancy = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "{} - {}".format(self.title, self.vacancy)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(500))

    def __repr__(self):
        return "{}".format(self.role_name)