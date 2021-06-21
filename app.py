from flask_sqlalchemy import SQLAlchemy
from flask import Flask, Blueprint, render_template, request, redirect, url_for
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
db = SQLAlchemy()

log_addm = db.Table('log_addm',
    db.Column('log_id', db.Integer, db.ForeignKey('log.id'), primary_key=True),
    db.Column('addm_id', db.Integer, db.ForeignKey('addm.id'), primary_key=True)
)

class Addm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    emails = db.Column(db.Integer, nullable=False)
    regdate = db.Column(db.Integer, nullable=False)


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    addms = db.relationship('Addm', secondary=log_addm, lazy='dynamic')

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(main)

    return app

main = Blueprint('main', __name__)


@main.route('/')
def addm():
    addms = Addm.query.all()

    return render_template('index.html', addms=addms, addm=None)

@main.route('/', methods=['POST'])
def addm_post():
    try:
        addm_name = request.form.get('addm-name')
        emails = request.form.get('email')
        regdate = datetime.date(datetime.now())
        valid = validate_email(emails)
        emails = valid.email
        user = Addm.query.filter_by(
            emails=emails).first()  # if this returns a user, then the email already exists in database
        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            return redirect(url_for('main.addm'))
        else:

            addm_id = request.form.get('addm-id')

            if addm_id:
                addm = Addm.query.get_or_404(addm_id)
                addm.name = addm_name
                addm.emails = emails
                addm.regdate = regdate
                #addm.fats = fats

            else:
                new_addm = Addm(
                    name=addm_name,
                    emails=emails,
                    regdate=regdate,
                    #fats=fats
                )

                db.session.add(new_addm)

            db.session.commit()
    except EmailNotValidError as e:
        print(str(e))

    return redirect(url_for('main.addm'))


@main.route('/delete_addm/<int:addm_id>')
def delete_addm(addm_id):
    # = Addm.query.get_or_404(addm_id)
    db.session.query(Addm).delete()
    db.session.commit()

    return redirect(url_for('main.addm'))


@main.route('/addm_addm_to_log/<int:log_id>', methods=['POST'])
def addm_addm_to_log(log_id):
    log = Log.query.get_or_404(log_id)

    selected_addm = request.form.get('addm-select')

    addm = Addm.query.get(int(selected_addm))

    log.addms.append(addm)
    db.session.commit()

    return redirect(url_for('main.view', log_id=log_id))


@main.route('/remove_addm_from_log/<int:log_id>/<int:addm_id>')
def remove_addm_from_log(log_id, addm_id):
    log = Log.query.get(log_id)
    addm = Addm.query.get(addm_id)

    log.addms.remove(addm)
    db.session.commit()

    return redirect(url_for('main.view', log_id=log_id))

@main.route('/create_log', methods=['POST'])
def create_log():
    date = request.form.get('date')

    log = Log(date=datetime.strptime(date, '%Y-%m-%d'))

    db.session.addm(log)
    db.session.commit()

    return redirect(url_for('main.view', log_id=log.id))