
from app.forms import LoginForm, CreateAccountForm
from app.model import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from . import db, app
from flask import Flask, session, render_template, redirect, request, url_for, jsonify
from passlib.hash import sha256_crypt
from flask_login import login_user
from sqlalchemy import desc, exists, func, case,or_, extract ,and_

from app.util import verify_pass

# Set a secret key for session management
app.secret_key = "geoxhr123??"



@app.route('/')
def route_default():
    if 'user_id' in session:
        user_id = session['user_id']
        role = session['role']
        email = session['email']
        user = session['user']

        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Locate user by email
        user = Users.query.filter_by(email=email).first()

        if user and sha256_crypt.verify(password, user.password):
            # Successful login
            login_user(user)
            session['user_id'] = user.id
            session['role'] = user.role
            session['email'] = user.email
            session['user'] = f"{user.fname} {user.lname}"
            return redirect(url_for('index'))

        # Incorrect email or password
        return render_template('login.html', msg='Wrong email or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Create your database engine
engine = create_engine('mysql+pymysql://addatsco_geox_user:Addatgeox??@162.214.195.234/addatsco_geox_dashboard')

# Create a session factory
Session = sessionmaker(bind=engine)
class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

@app.route('/index')
def index():
    candidateplace = 0
    user_id = session['user_id']
    if session['role'] == 'user':
        totalforms = allforms_data.query.filter(allforms_data.user_id == user_id).count()
        candidateplace = recruiting_data.query.filter(
            or_(recruiting_data.did_you == 'Candidate Placement', recruiting_data.person_starting == 'Candidate Placement'),
            and_(recruiting_data.user_id == user_id)).count()
        totalcandidate = Emails_data.query.filter(Emails_data.action == 'Interested').count()
        total_users = Users.query.count()
        action = 'Interested'
        alldata = Emails_data.query.filter(Emails_data.action == action).order_by(desc(Emails_data.id)).all()

    else:
        total_users = Users.query.count()
        totalcandidate = Emails_data.query.filter(Emails_data.action == 'Interested').count()
        totalforms = allforms_data.query.count()
        action = 'Interested'
        alldata = Emails_data.query.filter(Emails_data.action == action).order_by(desc(Emails_data.id)).all()

    candidateplacement = (
        Users.query.filter_by(role='user')
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(recruiting_data.created_at).label('entry_date'),
            func.sum(case(
                (or_(recruiting_data.did_you == 'Candidate Placement',
                     recruiting_data.person_starting == 'Candidate Placement'), 1),
                else_=0)).label('placement_count')
        )
        .outerjoin(recruiting_data, Users.id == recruiting_data.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )
    resumesent = (
        Users.query.filter_by(role='user')
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(recruiting_data.created_at).label('entry_date'),
            func.sum(case(
                (or_(recruiting_data.did_you == 'Resume Sent',
                     recruiting_data.person_starting == 'Resume Sent'), 1),
                else_=0)).label('resume_count')
        )
        .outerjoin(recruiting_data, Users.id == recruiting_data.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )
    interview = (
        Users.query.filter_by(role='user')
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(recruiting_data.created_at).label('entry_date'),
            func.sum(case(
                (or_(recruiting_data.did_you == 'Interview Scheduled',
                     recruiting_data.person_starting == 'Interview Scheduled'), 1),
                else_=0)).label('interview_count')
        )
        .outerjoin(recruiting_data, Users.id == recruiting_data.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )

    interview = (
        Users.query.filter_by(role='user')
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(recruiting_data.created_at).label('entry_date'),
            func.sum(case(
                (or_(recruiting_data.did_you == 'Interview Scheduled',
                     recruiting_data.person_starting == 'Interview Scheduled'), 1),
                else_=0)).label('interview_count')
        )
        .outerjoin(recruiting_data, Users.id == recruiting_data.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )

    helpingform = (
        Users.query.filter_by(role='user')
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(recruiting_data.created_at).label('entry_date'),
            func.sum(case(
                (recruiting_data.did_you == 'Help Another', 1),
                else_=0)).label('helping_count')
        )
        .outerjoin(recruiting_data, Users.id == recruiting_data.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )
    contractsigned = (
        Users.query.filter_by(role='user')
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(Marketing.created_at).label('entry_date'),
            func.sum(case(
                (Marketing.status == 'New deal opened and contract signed', 1),
                else_=0)).label('contractsign_count')
        )
        .outerjoin(Marketing, Users.id == Marketing.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )
    contractnotsigned = (
        Users.query.filter_by(role='user')
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(Marketing.created_at).label('entry_date'),
            func.sum(case(
                (Marketing.status == 'New deal and contract not signed', 1),
                else_=0)).label('contractnotsign_count')
        )
        .outerjoin(Marketing, Users.id == Marketing.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )
    reopendeals = (
        Users.query.filter_by(role='user')
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(Marketing.created_at).label('entry_date'),
            func.sum(case(
                (Marketing.status == 'Reopened deals', 1),
                else_=0)).label('reopen_count')
        )
        .outerjoin(Marketing, Users.id == Marketing.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )


    interviews_data = []
    helpings_data = []
    resumesents_data = []
    contractsigned_data = []
    contractnotsigned_data = []
    reopendeals_data = []
    candidateplacement_data = []
    placementdata_count = []

    usernames = Users.query.filter(Users.role != 'admin').all()
    fullnames = []

    for user in usernames:
        fullnames.append(f"{user.fname} {user.lname}")

    for row in interview:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            interview_count = row.interview_count
            interviews_data.append({'date': formatted_date, 'count': interview_count, 'user_name': user_name})
    # print("interviews_data", interviews_data, usernames)

    for row in helpingform:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            helping_count = row.helping_count
            helpings_data.append({'date': formatted_date, 'count': helping_count, 'user_name': user_name})
    # print("helpings_data", helpings_data, usernames)

    for row in resumesent:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            resume_count = row.resume_count
            resumesents_data.append({'date': formatted_date, 'count': resume_count, 'user_name': user_name})
    # print("resumesents_data", resumesents_data)

    for row in contractsigned:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            contractsign_count = row.contractsign_count
            contractsigned_data.append({'date': formatted_date, 'count': contractsign_count, 'user_name': user_name})
    # print("contractsigned_data", contractsigned_data, usernames)

    for row in contractnotsigned:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            contractnotsign_count = row.contractnotsign_count
            contractnotsigned_data.append(
                {'date': formatted_date, 'count': contractnotsign_count, 'user_name': user_name})
    # print("contractsigned_data", contractnotsigned_data, usernames)

    for row in reopendeals:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            reopen_count = row.reopen_count
            reopendeals_data.append({'date': formatted_date, 'count': reopen_count, 'user_name': user_name})
    # print("contractsigned_data", contractnotsigned_data, usernames)

    for row in candidateplacement:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            placement_count = row.placement_count
            candidateplacement_data.append({'date': formatted_date, 'count': placement_count, 'user_name': user_name})

    # print(candidateplacement_data,usernames)
    jobsorder = db.session.query(Joborder).all()
    marketing_entries = db.session.query(Marketing).all()

    # Create a dictionary to store company names for faster lookup
    company_name_dict = {entry.id: entry.company for entry in marketing_entries}

    # Update the company names in the jobsorder list
    for job_order in jobsorder:
        company_id = job_order.company_id
        if company_id in company_name_dict:
            job_order.company = company_name_dict[company_id]
    # print(jobsorder, marketing_entries)
    data_array = DotDict({
        'counters': {
            'total_users': total_users,
            'totalcandidate': totalcandidate,
            'totalforms': totalforms,
            'candidateplace': candidateplace,

        },
        'interviews': interviews_data,
        'helpings': helpings_data,
        'resumesents': resumesents_data,
        'usernames': fullnames,
        'contractsigned' : contractsigned_data ,
        'contractnotsigned' : contractnotsigned_data ,
        'reopendeals' : reopendeals_data ,
        'candidateplacement' : candidateplacement_data,
        'placementdata_count' : placementdata_count
    })
    return render_template('index.html', data_array=data_array, jobsorder=jobsorder, alldata=alldata)


@app.route('/addmembers')
def addmembers():
        designation = userdesignation_data.query.all()
        role = Role.query.all()
        return render_template('addmember.html', designations=designation, roles=role)

@app.route('/updatemembers/<int:id>')
def updatemembers(id):
        if id is not None:
            designation = userdesignation_data.query.all()
            role = Role.query.all()
            user = db.session.query(Users).filter_by(id=id).first()
            return render_template('addmember.html', data=user, designations=designation, roles=role)


@app.route('/savemember', methods=["POST"])
def savemember():
    if request.method == 'POST':
        id = request.form.get('id')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        role = request.form.get('selected_role')
        designation = request.form.get('selected_designation')
        password = request.form.get('password')
        encpassword = sha256_crypt.encrypt(password)

        try:
            if id is not None:
                entry = db.session.query(Users).filter_by(id=id).first()
                if entry:
                    entry.id = id
                    entry.role = role
                    entry.fname = fname
                    entry.lname = lname
                    entry.email = email
                    entry.designation = designation
                else:
                    return jsonify({'error': 'Member with specified ID not found'}), 404
            else:
                email_exists = db.session.query(exists().where(Users.email == email)).scalar()
                if not email_exists:
                    entry = Users(fname=fname, lname=lname, email=email, password=encpassword, role=role,
                                  designation=designation)
                    db.session.add(entry)
                else:
                    return jsonify({'error': 'Email already exists'}), 400

            db.session.commit()
            response = jsonify({'message': 'Member saved successfully!'})
            response.status_code = 200

        except Exception as e:
            # Handle any errors that occurred during database operations
            db.session.rollback()
            response = jsonify({'error': f'Error saving member: {str(e)}'})
            response.status_code = 500

        return response

@app.route('/members')
def members():
    role = 'user'
    members_data = Users.query.filter(Users.role == role).order_by(desc(Users.id)).all()
    return render_template('members.html', members_data=members_data)

@app.route('/deletemembers/<int:id>', methods=['POST'])
def deletemembers(id):
    if id is not None:
        try:
            db.session.query(Users).filter(Users.id == id).delete()
            db.session.commit()
            return jsonify({'message': 'Member Deleted!'}), 200
        except Exception as e:
            return jsonify({'message': f'Error deleting member: {str(e)}'}), 500


@app.route('/changepassword', methods=["POST"])
def chnagepassword():
    if request.method == 'POST':
        user_id=session['user_id']
        oldpassword = request.form.get('oldps')
        newpassword = request.form.get('newps')
        confirmpassword = request.form.get('confirmpswrd')
        check = db.session.query(Users).filter_by(id=user_id).first()
        varify = sha256_crypt.verify(oldpassword, check.password)
        # print(varify)
        if varify:
            # print("varify")
            if newpassword==confirmpassword:
                # print("password confirm")
                password = sha256_crypt.encrypt(confirmpassword)
                check.password=password
                db.session.add(check)
                db.session.commit()
                return render_template('home/user.html', msg='password changed successfully')
            else:
                return render_template('home/user.html', msg='confirm password did not match')
        else:
            return render_template('home/user.html', msg='old password did not match')


@app.route('/forms')
def forms():
    if session['role'] == 'admin':
        alldata = allforms_data.query.order_by(desc(allforms_data.id)).all()
    elif session['role'] == 'user':
        user_id = session['user_id']
        alldata = allforms_data.query.filter(allforms_data.user_id == user_id).order_by(desc(allforms_data.id)).all()
    return render_template('forms.html', alldata=alldata)
