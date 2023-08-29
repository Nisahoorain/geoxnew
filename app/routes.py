
from app.forms import LoginForm, CreateAccountForm
from app.model import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from . import db, app
from werkzeug.utils import secure_filename
import os
import io
from flask import Flask, session, render_template, redirect, request, url_for, jsonify,send_file
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


@app.route('/candidate')
def candidate():
    action = 'Interested'
    with db.session() as session:
        alldata = session.query(Emails_data).filter(Emails_data.action != action).order_by(desc(Emails_data.id)).all()
    return render_template('candidates.html', alldata=alldata)

# applied candidates route
@app.route('/selecteddata')
def selecteddata():
    action = 'Interested'
    alldata = Emails_data.query.filter(Emails_data.action == action).order_by(desc(Emails_data.id)).all()
    return render_template('candidates.html', alldata=alldata)

# for pdf view
@app.route('/pdf_content/<int:email_id>')
def get_pdf_content(email_id):
    email = Emails_data.query.filter_by(id=email_id).first()

    if email and email.file_content:
        file_name = email.file_name
        pdf_content = email.file_content

        # Mark the email as read when the user views the PDF
        if not email.is_read:
            email.is_read = True
            db.session.commit()

        response = send_file(
            io.BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=False,
            attachment_filename=file_name
        )

        return response

    return jsonify({'error': 'PDF not found'}), 404

# read/unread
@app.route('/check_is_read/<int:email_id>')
def check_is_read(email_id):
    email = Emails_data.query.get(email_id)
    if email:
        return jsonify({'is_read': email.is_read})
    return jsonify({'error': 'Email not found'}), 404

@app.route('/updatemail', methods=['POST'])
def updatemail():
    try:
        data = request.get_json()
        id = data.get('id')
        # Query the database to find the Users record by ID
        user = db.session.query(Emails_data).filter_by(id=id).first()

            # Update the 'action' field of the Users record with the selected option
        user.action = data.get('selectedOption')
        db.session.add(user)
            # Commit the changes to the database
        db.session.commit()
        return jsonify({'message': 'Update successful'}), 200

    except Exception as e:
        # Handle any other unexpected errors
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500


@app.route('/deletemail', methods=['POST'])
def deletemail():
    try:
        data = request.get_json()
        id = data.get('id')
        # Query the database to find the Users record by ID
        user = db.session.query(Emails_data).filter_by(id=id).first()
        if user:

            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'record deleted successfully'}), 200
        else:
            return jsonify({"Record not found for uid:", id})
    except Exception as e:
        # Handle any other unexpected errors
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500

@app.route('/members')
def members():
    role = 'user'
    members_data = Users.query.filter(Users.role == role).order_by(desc(Users.id)).all()
    return render_template('members.html', members_data=members_data)


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


@app.route('/deletemembers/<int:id>', methods=['POST'])
def deletemembers(id):
    if id is not None:
        try:
            db.session.query(Users).filter(Users.id == id).delete()
            db.session.commit()
            return jsonify({'message': 'Member Deleted!'}), 200
        except Exception as e:
            return jsonify({'message': f'Error deleting member: {str(e)}'}), 500

@app.route('/user')
def user():
    return render_template('/user.html')

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
                return render_template('user.html', msg='password changed successfully')
            else:
                return render_template('user.html', msg='confirm password did not match')
        else:
            return render_template('user.html', msg='old password did not match')


@app.route('/onereporting')
def onereporting():
    return render_template('/onereporting-form.html')


@app.route('/onereporting_form/<int:candidate_id>/job/<int:jobid>/OrderId/<int:OrderId>')
@app.route('/onereporting_form/<int:id>')
def onereporting_form(id=None, candidate_id=None, jobid=None, OrderId= None):
    if candidate_id is not None:
        user = db.session.query(Emails_data).filter_by(id=candidate_id).first()
        companydata = db.session.query(Marketing).filter_by(id=jobid, company_status='active').first()
        # companydata = Marketing.query.filter(Marketing.id == jobid, Marketing.company_status == 'active').all()
    elif id is not None:
        user = db.session.query(Emails_data).filter_by(id=id).first()
        companydata = None
    else:
        pass
    # company = Marketing.query.all()
    company = Marketing.query.filter(Marketing.company_status == 'active').all()
    positions = Joborder.query.filter_by(company_id=companydata.id, id=OrderId).all() if companydata else []
    # print("positions", positions,companydata, company)

    return render_template('recruiting.html', data=user, company=company, companydata=companydata, positions=positions)

@app.route('/marketing', methods=["POST"])
def marketing():
    if request.method == 'POST':
        id = request.form.get('id')
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        company = request.form.get('company')
        cperson = request.form.get('cperson')
        phone = request.form.get('phone')
        location = request.form.get('location')
        markup = request.form.get('markup')
        jobid = request.form.get('jobid')
        active = 'active'
        # jobCount = int(request.form.get('job_count'))

        # jobstatus = []
        # for i in range(1, jobCount + 1):
        #     jobstatus.append(request.form.get(f'jobstatus{i}'))
        job_titles = request.form.getlist('job_title')
        pay_rates = request.form.getlist('pay_rate')
        pay_rate_types = request.form.getlist('pay_rate_type')
        shifts_start = request.form.getlist('shift_start')
        shifts_end = request.form.getlist('shift_end')
        total_vacancies = request.form.getlist('total_vacancies')
        # print("jobstatus",jobstatus, jobCount)

        # new fields end
        Status = request.form.get('Status')
        other_report = request.form.get('otherreport')
        notes = request.form.get('notes')

        formtype = 'New Deals Contract Signed'
        if id is not None:
            entry = db.session.query(Marketing).filter_by(id=id).first()
            entry.company = company
            entry.status = Status
            entry.cperson = cperson
            entry.cphone = phone
            entry.Markup = markup
            entry.location = location
            entry.otherReport = other_report
            entry.Notes = notes
            db.session.add(entry)
            db.session.commit()
            forms = db.session.query(allforms_data).filter_by(form_id=id, form_type=formtype).first()
            forms.belongsto = cperson
            forms.status = Status
            db.session.add(forms)
            db.session.commit()

            for i in range(len(job_titles)):
                if i == 0:
                    # print(i, "length of jobs")
                    updatejob = db.session.query(Joborder).filter(Joborder.company_id == id,
                                                                  Joborder.id == jobid).first()
                    updatejob.job_title = job_titles[i]
                    updatejob.pay_rate = pay_rates[i]
                    updatejob.pay_rate_type = pay_rate_types[i]
                    updatejob.shift_start = shifts_start[i]
                    updatejob.shift_end = shifts_end[i]
                    updatejob.total_vacancy = total_vacancies[i]
                    updatejob.jobstatus = active
                    db.session.add(forms)
                    db.session.commit()

                if i >= 1:
                    # print("yess new")
                    job_title = job_titles[i]
                    pay_rate = pay_rates[i]
                    pay_rate_type = pay_rate_types[i]
                    shift_start = shifts_start[i]
                    shift_end = shifts_end[i]
                    total_vacancy = total_vacancies[i]

                    order = Joborder(user_id=user_id, company_id=id, payrate=pay_rate, salarytype=pay_rate_type,jobstatus = active,
                                      title=job_title, starttime=shift_start, endtime=shift_end,
                                     vacancy=total_vacancy)
                    db.session.add(order)
                    db.session.commit()


        else:
            # Now, insert the list data
            entry = Marketing(user_id=user_id, name=name, company=company, status=Status, cperson=cperson, company_status = active,
                              cphone=phone, location=location, Markup=markup, otherReport=other_report, Notes=notes)

            db.session.add(entry)
            db.session.commit()
            submitted_id = entry.id

            forms = allforms_data(user_id=user_id, form_id=submitted_id, filledby=name, belongsto=cperson,
                                  form_type=formtype, status=Status)
            db.session.add(forms)
            db.session.commit()
            for i in range(len(job_titles)):
                job_title = job_titles[i]
                pay_rate = pay_rates[i]
                pay_rate_type = pay_rate_types[i]
                shift_start = shifts_start[i]
                shift_end = shifts_end[i]
                # jobstatuss = jobstatus[i]
                total_vacancy = total_vacancies[i]

                order = Joborder(user_id=user_id, company_id=submitted_id, payrate=pay_rate, salarytype=pay_rate_type,
                                  jobstatus = active, title=job_title, starttime=shift_start, endtime=shift_end,
                                 vacancy=total_vacancy)
                # jobstatus = jobstatuss,
                db.session.add(order)
                db.session.commit()

        response = jsonify({'message': 'success'})
        response.status_code = 200
        # send_notification()
        return response
    else:
        # Handle other HTTP methods, if needed
        return "Unsupported method"

# @blueprint.route('/send_notification')
# def send_notification():
#     subject = 'Notification from Flask App'
#     recipients = ['hassani8is007@gmail.com']  # List of recipient email addresses
#     message_body = 'This is a notification message from your Flask app.'
#
#     with current_app.app_context():  # Needed to access current_app within a different context
#         msg = Message(subject=subject,
#                       recipients=recipients,
#                       body=message_body)
#         current_app.mail.send(msg)  # Use current_app.mail to access the mail instance
#
#     return 'Notification email sent!'

@app.route('/hrforms', methods=["POST"])
def hrforms():
    if request.method == 'POST':
        id = request.form.get('id')
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        candidate = request.form.get('cname')
        late = request.form.get('Late/absent')
        Informed = request.form.get('Informed/uninformed')
        reasonvacation = request.form.get('reasonvacation')
        notes = request.form.get('notes')
        formtype = 'HR Forms'
        status = late + " " + Informed
        if late != 'request for leave':
            reasonvacation = ""

        if id is not None:
            entry = db.session.query(Hrforms).filter_by(id=id).first()
            entry.candidate_name = candidate
            entry.late = late
            entry.informed = Informed
            entry.reason_vacation = reasonvacation
            entry.notes = notes
            db.session.add(entry)
            db.session.commit()

            forms = db.session.query(allforms_data).filter_by(form_id=id, form_type=formtype).first()
            forms.belongsto = candidate
            forms.status = status

        else:
            entry = Hrforms(user_id=user_id, name=name, candidate_name=candidate, late=late, informed=Informed,
                            reason_vacation=reasonvacation, notes=notes)

            db.session.add(entry)
            db.session.commit()
            submitted_id = entry.id

            forms = allforms_data(user_id=user_id, form_id=submitted_id, filledby=name, belongsto=candidate,
                                  form_type=formtype, status=status)
        db.session.add(forms)
        db.session.commit()
        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:
        # Handle other HTTP methods, if needed
        return "Unsupported method"


@app.route('/resumesent', methods=["POST"])
def resumesent():
    if request.method == 'POST':
        formid = request.form.get('formid')
        id = request.form.get('id')
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        candidate = request.form.get('cname')
        phone = request.form.get('cphone')
        position = request.form.get('selected_position')
        did_you = request.form.get('Didyou')
        companydate = request.form.get('companydate')
        relative_file_path = ''
        status = ''
        selected_value = request.form.get('selected_company')
        # print("selected_value:", selected_value)

        company_id, company_name = selected_value.split('|')
        # print("company_id:", company_id)
        # print("company_name:", company_name)

        interviewdate = request.form.get('interviewdate')

        other_report = request.form.get('Otherreport')
        # print(company_id, company_name,"split")
        if did_you == 'Help Another':
            help = request.form.get('help')
            person_starting = request.form.get('person_starting')
            status = person_starting
        elif did_you != 'Help Another':
            help = ''
            person_starting = ''
            status = did_you

        if did_you == 'Candidate Placement':
            ecname = request.form.get('ecname')
            ecnumber = request.form.get('ecnumber')
            location = request.form.get('Location')
            locationcgoing = request.form.get('clocation')
            starttime = request.form.get('starttime')
            needmember = request.form.get('needteam')

            file = request.files['myFile']
            if file.filename:
                filename = secure_filename(file.filename)

                # Get the base directory of the app
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

                # Create the directory 'static/assets/imgs' if it doesn't exist
                image_path = os.path.join(base_dir, 'static', 'assets', 'jobimgs')
                os.makedirs(image_path, exist_ok=True)

                # Append the desired filename to the image_path
                relative_file_path = os.path.join('static', 'assets', 'jobimgs', filename)

                # Save the file with the specified name
                file_path = os.path.join(image_path, filename)
                file.save(file_path)

        elif did_you != 'Candidate Placement':
            file = ""
            ecname = ''
            ecnumber = ''
            location = ''
            locationcgoing = ''
            starttime = ''
            needmember = ''

        notes = request.form.get('notes')
        formtype = 'Person Placement'
        if formid is not None:
            entry = db.session.query(recruiting_data).filter_by(id=formid).first()
            entry.candidate = candidate
            entry.phone = phone
            entry.company = company_name
            entry.did_you = did_you
            entry.ecname = ecname
            entry.ecnumber = ecnumber
            entry.location = location
            entry.locationcgoing = locationcgoing
            entry.starttime = starttime
            entry.needmember = needmember
            entry.interviewdate = interviewdate
            entry.companydate = companydate
            entry.help = help
            entry.person_starting = status
            entry.other_report = other_report
            entry.position = position
            entry.notes = notes
            if file:
                entry.photo = relative_file_path
            db.session.add(entry)
            db.session.commit()

            forms = db.session.query(allforms_data).filter_by(form_id=formid, form_type=formtype).first()
            forms.belongsto = candidate
            forms.status = status
            db.session.add(forms)
            db.session.commit()
            if status == "Candidate Placement":

                with Session() as session:  # Start a transaction
                    companyy = session.query(Marketing).filter(
                        Marketing.id == company_id
                    ).first()
                    # print(companyy)
                    updatevacancy = session.query(Joborder).filter(Joborder.company_id == companyy.id,
                                                                   Joborder.title == position,
                                                                   Joborder.jobstatus == 'active').first()
                    # updatevacancy = Joborder.query.filter(Joborder.company_id == companyy.id, Joborder.title == position, Joborder.jobstatus == 'active').first()

                    if updatevacancy.vacancy == 1:  # Check if a matching record was found
                        # print(updatevacancy.vacancy, "if")
                        updatevacancy.vacancy -= 1
                        updatevacancy.jobstatus = 'inactive'
                        session.add(updatevacancy)

                        session.commit()
                        # print(updatevacancy.vacancy, "after update")
                        checkjobs = Joborder.query.filter(Joborder.company_id == companyy.id,
                                                          Joborder.jobstatus == 'active').all()

                        all_vacancies_zero = all(data.vacancy == 0 for data in checkjobs)

                        if all_vacancies_zero:
                            # print(all_vacancies_zero, "vacancy")
                            # Perform your action when all vacancy counts are zero
                            companyinactive = session.query(Marketing).filter(Marketing.id == company_id).first()
                            companyinactive.company_status = 'inactive'
                            session.add(companyinactive)
                            session.commit()


                    else:
                        # print(updatevacancy.vacancy, "else")
                        updatevacancy.vacancy -= 1
                        session.add(updatevacancy)

                        session.commit()


            else:
                # Handle the case when no matching record is found
                hello  = "No matching record found for updating vacancy"
            db.session.commit()
            response = jsonify({'message': 'success'})
            response.status_code = 200
            return response
        else:
            entry = recruiting_data(user_id=user_id, name=name, candidate=candidate, phone=phone, company=company_name,
                               did_you=did_you,
                               ecname=ecname, ecnumber=ecnumber, location=location, locationcgoing=locationcgoing,
                               starttime=starttime,
                               needmember=needmember, photo=relative_file_path, interviewdate=interviewdate,
                               companydate=companydate, help=help, person_starting=status,
                               other_report=other_report, position=position, notes=notes)
            db.session.add(entry)
            db.session.commit()
            submitted_id = entry.id

            forms = allforms_data(user_id=user_id, form_id=submitted_id, filledby=name, belongsto=candidate,
                                  form_type=formtype, status=status)
            db.session.add(forms)
            db.session.commit()

            user = db.session.query(Emails_data).filter_by(id=id).first()

            user.status = status
            db.session.add(user)
            # Commit the changes to the database
            db.session.commit()
            if status == "Candidate Placement":

                with Session() as session:  # Start a transaction
                    companyy = session.query(Marketing).filter(
                        Marketing.id == company_id
                    ).first()
                    updatevacancy = session.query(Joborder).filter(Joborder.company_id == companyy.id,
                                                                   Joborder.title == position,
                                                                   Joborder.jobstatus == 'active').first()
                    # updatevacancy = Joborder.query.filter(Joborder.company_id == companyy.id, Joborder.title == position, Joborder.jobstatus == 'active').first()
                    if updatevacancy.vacancy == 1:  # Check if a matching record was found
                        updatevacancy.vacancy -= 1
                        updatevacancy.jobstatus = 'inactive'
                        session.add(updatevacancy)

                        session.commit()
                        checkjobs = Joborder.query.filter(Joborder.company_id == companyy.id,
                                                          Joborder.jobstatus == 'active').all()

                        all_vacancies_zero = all(data.vacancy == 0 for data in checkjobs)

                        if all_vacancies_zero:
                            # Perform your action when all vacancy counts are zero
                            companyinactive = session.query(Marketing).filter(Marketing.id == company_id).first()
                            companyinactive.company_status = 'inactive'
                            session.add(companyinactive)
                            session.commit()

                    else:
                        updatevacancy.vacancy -= 1
                        session.add(updatevacancy)

                        session.commit()


            else:
                # Handle the case when no matching record is found
                hello2  = "No matching record found for updating vacancy."
            db.session.commit()
            response = jsonify({'message': 'success'})
            response.status_code = 200
            return response
    else:
        # Handle other HTTP methods, if needed
        return "Unsupported method"

# @app.route('/alljobs')
# def alljobs():
#     alljobs = Jobs.query.all()
#     return render_template('jobs.html', alljobs=alljobs)

@app.route('/selectjob/<int:id>', methods=['POST', 'GET'])
def selectjob(id):
    if request.method == 'POST':
        jobid = request.form.get('jobid')
        # print(jobid)
        user = db.session.query(Emails_data).filter_by(id=id).first()
        jobdata = db.session.query(Jobs).filter_by(id=jobid).first()
        return render_template('recruiting.html', data=user, jobdata=jobdata)
    else:
        alljobs = Jobs.query.all()
        return render_template('jobs.html', alljobs=alljobs, id=id)


# @app.route('/editjob/<int:id>')
# def editjob(id):
#     job=db.session.query(Jobs).filter(Jobs.id==id).first()
#     return render_template('postnewjobs.html', job=job)
#############post job 5-8-2023
# @app.route('/postjob', methods=['POST'])
# def postjob():
#     if request.method == 'POST':
#         id = request.form.get('id')
#         title = request.form.get('title')
#         name = request.form.get('name')
#         company = request.form.get('company')
#         user_id = request.form.get('user_id')
#         location = request.form.get('location')
#         JobType = request.form.get('Job-Type')
#         duration = request.form.get('duration')
#         onsite = request.form.get('onsite')
#         salarytypes = request.form.get('salarytypes')
#         Salary = request.form.get('Salary')
#         date = request.form.get('date')
#         job_status = request.form.get('active')
#         description = request.form.get('description')
#         responsibility = request.form.get('responsibility')
#         eligibility = request.form.get('eligibility')
#         notes = request.form.get('notes')
#
#         file = request.files['myFile']
#         if file.filename:
#             filename = secure_filename(file.filename)
#
#                 # Get the base directory of the app
#             base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#
#                 # Create the directory 'static/assets/imgs' if it doesn't exist
#             image_path = os.path.join(base_dir, 'static', 'assets', 'jobimgs')
#             os.makedirs(image_path, exist_ok=True)
#
#                 # Append the desired filename to the image_path
#             relative_file_path = os.path.join( 'static', 'assets', 'jobimgs', filename)
#
#                 # Save the file with the specified name
#             file_path = os.path.join(image_path, filename)
#             file.save(file_path)
#         else:
#             relative_file_path=''
#
#         if id is not None:
#             entry = db.session.query(Jobs).filter_by(id=id).first()
#             entry.title=title
#             entry.company=company
#             entry.location=location
#             entry.job_type=JobType
#             entry.duration= duration
#             entry.onsite= onsite
#             entry.salary_type=salarytypes
#             entry.salary=Salary
#             entry.job_date=date
#             entry.job_status=job_status
#             entry.description=description
#             entry.responsibility=responsibility
#             entry.eligibility=eligibility
#             entry.notes=notes
#             if file.filename:
#                 entry.image =relative_file_path
#         else:
#             entry = Jobs(user_id=user_id, name=name, title=title, image=relative_file_path, company=company, location=location,
#                             job_type=JobType, duration= duration, onsite= onsite, salary_type=salarytypes, salary=Salary,
#                             job_date=date, job_status=job_status, description=description, responsibility=responsibility, eligibility=eligibility,
#                             notes=notes)
#         db.session.add(entry)
#         db.session.commit()
#
#         return redirect(url_for('home_blueprint.alljobs'))
#         return redirect(url_for('home_blueprint.alljobs'))

#
@app.route('/position', methods=['POST'])
def position():
    data = request.get_json()
    selectedOption = data.get('companyId')
    # print(selectedOption)
    positions = Joborder.query.filter(and_(Joborder.company_id == selectedOption, Joborder.jobstatus=='active')).all()
    positions_list = [{'position_name': position.title} for position in positions]

    return jsonify({'positions': positions_list})

# @blueprint.route('/position', methods=['POST'])
# def position():
#     data = request.get_json()
#     selectedOption = data.get('selectedOption')
#     print("selectedOption",selectedOption)
#     company = Marketing.query.filter_by(id=selectedOption).first()
#
#     if company:
#         positions = Joborder.query.filter_by(company_id=company.id).all()
#         positions_list = [{'position_name': position.title} for position in positions]
#         return jsonify({'positions': positions_list})
#     else:
#         return jsonify({'positions': []})

@app.route('/otherfinal', methods=["POST"])
def otherfinal():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        otherreport = request.form.get('otherreport')
        notes = request.form.get('notes')
        formtype = 'Other Final'
        status = "Other Report"
        candidate = "-"
        id = request.form.get('id')
        if id is not None:
            entry = db.session.query(Otherfinal).filter_by(id=id).first()
            entry.other_report = otherreport
            entry.notes = notes
            db.session.add(entry)
            db.session.commit()
        else:

            entry = Otherfinal(user_id=user_id, name=name, other_report=otherreport, notes=notes)

            db.session.add(entry)
            db.session.commit()
            submitted_id = entry.id

            forms = allforms_data(user_id=user_id, form_id=submitted_id, filledby=name, belongsto=candidate,
                                  form_type=formtype, status=status)
            db.session.add(forms)
            db.session.commit()
        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:
        # Handle other HTTP methods, if needed
        return "Unsupported method"

@app.route('/forms')
def forms():
    if session['role'] == 'admin':
        alldata = allforms_data.query.order_by(desc(allforms_data.id)).all()
    elif session['role'] == 'user':
        user_id = session['user_id']
        alldata = allforms_data.query.filter(allforms_data.user_id == user_id).order_by(desc(allforms_data.id)).all()
    return render_template('forms.html', alldata=alldata)


@app.route('/view/<int:form_id>/<string:form_type>')
def view(form_id, form_type):
    type='view'
    if form_type=='New Deals Contract Signed':
        formdata = Marketing.query.filter(Marketing.id==form_id).first()
        jobsdata = Joborder.query.filter(Joborder.company_id==form_id).all()
        # print(*jobsdata)
        return render_template('marketing.html', type=type, formdata=formdata, jobsdata=jobsdata)
    elif form_type=='Person Placement':
         formdata = recruiting_data.query.filter(recruiting_data.id==form_id).first()
         # company = Marketing.query.filter(Marketing.status=='New deal opened and contract signed', Marketing.jobstatus=='active', Marketing.vacancy>=1).all()
         company = Marketing.query.all()
         return render_template('recruiting.html', type=type, formdata=formdata, company=company)
    elif form_type=='HR Forms':
         formdata = Hrforms.query.filter(Hrforms.id==form_id).first()
         return render_template('hrforms.html', type=type, formdata=formdata)
    elif form_type=='Other Final':
         formdata = Otherfinal.query.filter(Otherfinal.id==form_id).first()
         return render_template('otherreport.html', type=type, formdata=formdata)


@app.route('/editforms/<int:form_id>/<string:form_type>')
def editforms(form_id, form_type):
    type='edit'
    if form_type=='New Deals Contract Signed':
        formdata = Marketing.query.filter(Marketing.id==form_id).first()
        return render_template('marketing.html', type=type, formdata=formdata)
    elif form_type=='Person Placement':
         formdata = recruiting_data.query.filter(recruiting_data.id==form_id).first()
         # company = Marketing.query.filter(Marketing.status=='New deal opened and contract signed', Marketing.jobstatus=='active', Marketing.vacancy>=1).all()
         company = Marketing.query.all()
         return render_template('recruiting.html', type=type, formdata=formdata, company=company)
    elif form_type=='HR Forms':
         formdata = Hrforms.query.filter(Hrforms.id==form_id).first()
         return render_template('hrforms.html', type=type, formdata=formdata)
    elif form_type=='Other Final':
         formdata = Otherfinal.query.filter(Otherfinal.id==form_id).first()
         return render_template('otherreport.html', type=type, formdata=formdata)


@app.route('/deleteform/<int:form_id>/<string:form_type>', methods=['POST'])
def deleteform(form_id, form_type):
    try:
        db.session.query(allforms_data).filter(allforms_data.form_id == form_id,
                                               allforms_data.form_type == form_type).delete()
        db.session.commit()

        if form_type == 'New Deals Contract Signed':
            db.session.query(Marketing).filter(Marketing.id == form_id).delete()
        elif form_type == 'Person Placement':
            db.session.query(recruiting_data).filter(recruiting_data.id == form_id).delete()
        elif form_type == 'HR Forms':
            db.session.query(Hrforms).filter(Hrforms.id == form_id).delete()
        elif form_type == 'Other Final':
            db.session.query(Otherfinal).filter(Otherfinal.id == form_id).delete()

        db.session.commit()
        return jsonify({'message': 'Form Deleted!'}), 200
    except Exception as e:
        return jsonify({'message': f'Error deleting form: {str(e)}'}), 500

def convert_unix_to_local(timestamp):
    # Convert Unix timestamp to local datetime
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp)


USER_ACCESS_TOKEN = '3bb93391790030e714cf2fbce97f603b'
