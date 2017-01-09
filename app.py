from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    make_response
)
import flask_login
import pymysql.cursors
import time
import datetime
import statistics
import hashlib
import bcrypt


def get_today():
    return str(datetime.date.today())


def epoch_to_str(ep):
    return time.strftime("%m/%d/%Y %I:%M %p", time.localtime(ep))


def str_to_epoch(s):
    return int(time.mktime(datetime.datetime.strptime(s, "%m/%d/%Y %I:%M %p").timetuple()))


def run_sql(sql, com=False):
    connection = pymysql.connect(host='127.0.0.1',
                                 user='user',
                                 password='password',
                                 db='babybets',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    date = None
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        if com:
            connection.commit()
        else:
            data = cursor.fetchall()
    except:
        return False
    finally:
        connection.close()

    if com:
        return True
    else:
        return data


def build_stats(data):
    data_dic = {'b': 0, 'g': 0, 'w': 0}
    weight_data = []
    len_data = []
    date_data = []
    for row in data:
        if row['gender'] == 'b':
            data_dic['b'] += 1
        else:
            data_dic['g'] += 1

        weight = row['lbs'].split(',')
        weight_data.append(int(weight[0]) * 16 + int(weight[1]))
        len_data.append(float(row['inches']))
        date_data.append(str_to_epoch(row['date']))

    med_weight = statistics.median(weight_data)
    med_weight = med_weight/16
    sml = str(med_weight).split('.')
    lbs = sml[0]
    oz = (float(med_weight) - float(sml[0])) * 16
    med_weight = "%s lbs. %s oz." % (lbs, int(oz))
    data_dic['w'] = med_weight
    data_dic['l'] = statistics.median(len_data)
    data_dic['d'] = epoch_to_str(statistics.median(date_data))
    return data_dic

# have to implement in the future
def log_user(data):
    # build the sql here and then submit to the database...
    print(data)

# should combine these for less queries
def baby_name():
    sql = "select value from settings where id = 'baby_name'"
    return run_sql(sql)[0]['value']

def close_date():
    sql = "select value from settings where id = 'close_date'"
    return run_sql(sql)[0]['value']

def betting_closed():
    sql = "select value from settings where id = 'betting'"
    return run_sql(sql)[0]['value']

def email_unique(email):
    sql = "select count(*) as count from users where email = '%s'"% email
    return run_sql(sql)[0]['count']

def create_vstr(email):
    h = hashlib.new('ripemd160')
    h.update(bytes(email, 'UTF-8'))
    return h.hexdigest()

# this should check that a user verified their address in the future
def check_user(email, pwd):
    sql = "select * from users where email = '%s'"% email
    data = run_sql(sql)
    hashed = data[0]['pwd']
    if len(data) == 0:
        rv = False
    else:
        rv = bcrypt.checkpw(bytes(pwd, 'UTF-8'), bytes(hashed, 'UTF-8'))
    return rv

def determine_admin(email):
    sql = "select * from users where email = '%s'"% email
    return int(run_sql(sql)[0]['id']) == 1

app = Flask(__name__)
app.secret_key = 'super secret string'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    sql = "select * from users where email = '%s'"% email
    if email not in run_sql(sql)[0]['email']:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    sql = "select * from users where email = '%s'"% email
    if email not in run_sql(sql)[0]['email']:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == users[email]['pw']

    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'GET':
        if 'p' in request.args and request.args['p'] == 'a':
            return render_template('signin.html', admin=True)
        else:
            return render_template('signin.html')
    
    email = request.form['email']
    pwd = request.form['pwd']
    
    if email and pwd:
        
        if check_user(email, pwd):
            user = User()
            user.id = email
            flask_login.login_user(user, remember=True)
            resp = make_response(redirect(url_for('main')))
            return resp
        else:
            return render_template('signin.html', msg="Username or password error")

    return 'Bad login'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    # create the user
    email = request.form['email'] # check for unique email address
    name = request.form['name']
    pwd = request.form['pwd']
    vpwd = request.form['vpwd']

    if not email or not name or not pwd or not vpwd:
        error_msg = "All fields must be filled in."
        return render_template('register.html', msg=error_msg)
    elif pwd != vpwd:
        error_msg = "Passwords must match."
        return render_template('register.html', msg=error_msg)
    elif email_unique(email) > 0:
        error_msg = "This email is already being used.<br/>Did you <a href=\"/forgot\">forget your password.</a>"
        return render_template('register.html', msg=error_msg)
    else:
        vstr = create_vstr(email)
        hpwd = bcrypt.hashpw(bytes(pwd, 'UTF-8'), bcrypt.gensalt()).decode("utf-8")
        # add the user to the database
        sql = "insert into users (name, email, pwd, vstr) VALUES ('%s', '%s', '%s', '%s')"% (name, email, hpwd, vstr)
        if run_sql(sql, com=True):
            msg = "Please verify your email address."
        else:
            msg = "oh snap, something bad happened and your account wasn't created."
        return render_template('register.html', msg=msg)

@app.route('/', methods=['GET', 'POST'])
@flask_login.login_required
def main():
    # return 'Logged in as: ' + flask_login.current_user.id
    if 'uname' in request.cookies:
        uname = request.cookies['uname']
    else:
        uname = ''

    # maybe check if uname is similar to a name with a bet
    # already placed and ask if they've already bet...
    if request.method == 'GET':
        closed = close_date()
        betting = betting_closed()
        if get_today() == closed or betting == 'closed':
            return redirect('/display?t=p')
        return render_template('main.html', baby_name=baby_name(), uname=uname, action='/')

    elif request.method == 'POST':
        error = None
        if 'name' in request.form and request.form['name'] == '':
            error = "Name cannot be empty."
        else:
            name = request.form['name']
        if 'date' in request.form and request.form['date'] == '':
            error = "Date cannot be empty."
        else:
            date = request.form['date']
        if 'gender' in request.form and request.form['gender'] == '':
            error = "Gender needs to be set."
        else:
            gender = request.form['gender']
        if 'lbs' in request.form and request.form['lbs'] == '':
            error = "Weight needs to be set."
        else:
            lbs = request.form['lbs']
        if 'inches' in request.form and request.form['inches'] == '':
            error = "Length needs to be set."
        else:
            inches = request.form['inches']

        if error is not None:
            return render_template('main.html', baby_name=baby_name(), uname=uname,
                                   msg=error)
        else:
            today = get_today()
            notes = request.form['notes']
            # let's add the data to the db
            sql = "insert into bets (name, gender, date, lbs, inches, notes, placed) values('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                name, gender, date, lbs, inches, notes, today)
            if run_sql(sql, com=True):
                return redirect(url_for('display'))
            else:
                error = "oh snap, something bad happened and your vote wasn't counted! :-O"
                return render_template('main.html', baby_name=baby_name(), uname=uname,
                                       msg=error)


@app.route('/display', methods=['GET'])
@flask_login.login_required
def display():
    sql = "select * from bets"
    data = run_sql(sql)
    stats = build_stats(data)
    if 't' in request.args and request.args['t'] == 'p':
        msg = 'Betting is closed.'
        return render_template('betdata.html', baby_name=baby_name(), data=data, stats=stats, msg=msg)
    return render_template('betdata.html', baby_name=baby_name(), data=data, stats=stats)


# an admin section
@app.route('/a', methods=['GET', 'POST'])
@flask_login.login_required
def admin():
    email = flask_login.current_user.id
    if determine_admin(email):
        sql = "select * from bets"
        data = run_sql(sql)
        return render_template('adata.html', baby_name=baby_name(), data=data)
    return 'Bad Request'


@app.route('/a/edit', methods=['GET', 'POST'])
@flask_login.login_required
def edit():
    email = flask_login.current_user.id
    if determine_admin(email):
        if request.method == 'GET':
            if 'p' in request.args:
                i = int(request.args['p'])
                sql = "select * from bets where id = %s" % i
                data = run_sql(sql)
                return render_template('update.html', baby_name=baby_name(), data=data)

        elif request.method == 'POST':
            error = None
            if 'id' in request.form:
                i = request.form['id']
            if 'name' in request.form and request.form['name'] == '':
                error = "Name cannot be empty."
            else:
                name = request.form['name']
            if 'date' in request.form and request.form['date'] == '':
                error = "Date cannot be empty."
            else:
                date = request.form['date']
            if 'gender' in request.form and request.form['gender'] == '':
                error = "Gender needs to be set."
            else:
                gender = request.form['gender']
            if 'lbs' in request.form and request.form['lbs'] == '':
                error = "Weight needs to be set."
            else:
                lbs = request.form['lbs']
            if 'inches' in request.form and request.form['inches'] == '':
                error = "Length needs to be set."
            else:
                inches = request.form['inches']

            if error is not None:
                return render_template('update.html',
                                       baby_name=baby_name(), msg=error)
            else:
                today = get_today()
                notes = request.form['notes']
                # let's add the data to the db
                sql = "update bets set name = '%s', gender = '%s', date = '%s', lbs = '%s', inches = '%s', notes = '%s', placed = '%s' where id = %d" % (
                    name, gender, date, lbs, inches, notes, today, int(i))
                if run_sql(sql, com=True):
                    return redirect(url_for('admin'))
                else:
                    error = "oh snap, something bad happened and your vote wasn't counted! :-O"
                    return render_template('update.html',
                                           baby_name=baby_name(), msg=error)
    return 'Bad request'


@app.route('/a/kb', methods=['GET', 'POST'])
@flask_login.login_required
def kill_betting():
    email = flask_login.current_user.id
    if determine_admin(email):
        if request.method == 'GET':
            return render_template('kb.html')
        elif request.method == 'POST':
            sql = "update settings set value = 'closed' where id = 'betting'"
            if run_sql(sql, com=True):
                return redirect(url_for('admin'))
            else:
                return 'oh snap! that didn\'t work.'

    return 'Bad Request'


@app.route('/a/delete', methods=['GET', 'POST'])
@flask_login.login_required
def del_bet():
    email = flask_login.current_user.id
    if determine_admin(email):
        if 'p' in request.args:
            i = int(request.args['p'])
            sql = "delete from bets where id = %s" % i
            print(sql)
            if run_sql(sql, com=True):
                return 'bet deleted!'
            else:
                return 'something went wrong...'
        return 'The admin section.'
    return 'Bad request'


@app.route('/logout')
def logout():
    flask_login.logout_user()
    resp = make_response('Logged out')
    resp.set_cookie('name', '', expires=0)
    return resp


@login_manager.unauthorized_handler
def unauthorized_handler():
    # return 'You are not authorized to view this page.'
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
