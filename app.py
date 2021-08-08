import secrets
from functools import wraps
from flask import Flask, render_template, flash, redirect, url_for, sessions, logging, request, session
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField
from passlib.hash import sha256_crypt


app = Flask(__name__)

# -------------------------Config MySQL-------------------
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "An_Aerospace_Company_db"
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app)


# -----------------------User Login--------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Great Cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('Login successful', 'success')
                return redirect(url_for('home'))

            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'User not found'
            return render_template('login.html', error=error)
    return render_template('login.html')


# -------------------Home-------------------------
@app.route('/home')
def home():
    return render_template('home.html')


# -------------------Request Wheel Assembly Subsystem Page-------------------------
@app.route('/wheel_assembly_subsystems')
def wheel_assembly_subsystems():
    return render_template('wheel_assembly_subsystems.html')


# ----------------------------------Register Form Class------------------------
class RegisterForm(Form):
    f_name = StringField('First Name', [validators.length(min=1, max=50)])
    l_name = StringField('Last Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.length(min=4, max=25)])
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')


# --------------------------------User Register---------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        f_name = form.f_name.data
        l_name = form.l_name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = mysql.connection.cursor()

        # Execute Query
        cur.execute("INSERT INTO users(f_name, l_name, email,username, password) VALUES (%s, %s, %s, %s, %s)",
                    (f_name, l_name, email, username,
                     password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Registration successful', 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# --------------------Aircraft Basic Information Entry-----------------


@app.route('/control_panel')
def control_panel():
    return render_template('Aircraft_Basic_Information_Entry/control_panel.html')


# -------Request Aircraft Basic information Entry Subsystems

@app.route('/aircraft_basic_information_entry')
def aircraft_basic_information_entry():
    return render_template('Aircraft_Basic_Information_Entry/aircraft_basic_information_entry.html')


@app.route('/list_all_aircraft')
def list_all_aircraft():
    # ----create cursor
    cur = mysql.connection.cursor()

    # ------ Get data from the table-----
    result = cur.execute("SELECT * FROM aircraft_basic_information_entry")

    if result > 0:
        # Get stored dat
        aircrafts = cur.fetchall()

        if result > 0:
            return render_template('Wheel_Assembly_Subsystems/List_All_Aircraft.html', aircrafts=aircrafts)
        else:
            msg = 'No Article Found'
            return render_template('dashboard.html', msg=msg)
        # ---------Close Connection--------------
        cur.close()

        return render_template('dashboard.html')

# --------------------Wheel Assembly Subsystems-----------------


@app.route('/list_all_wheel_assembly')
def list_all_wheel_assembly():
    # ------------ Create Cursor---------
    cur = mysql.connection.cursor()

    # -------------------- Get Aircraft ---------------
    result = cur.execute("SELECT * FROM wheel_assembly_subsystems")

    wheel_assembly = cur.fetchall()

    if result > 0:
        return render_template('Wheel_Assembly_Subsystems/list_all_wheel_assembly.html', wheel_assembly=wheel_assembly)

    else:
        msg = 'No Wheel Assembly Information Found'
        return render_template('dashboard.html', msg=msg)
    # ---------Close Connection--------------
    cur.close()

    return render_template('dashboard.html')


# -------------------------Check if user is logged in-----------------
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap


# ---------------------List All Aircraft----------------
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # ------------ Create Cursor---------
    cur = mysql.connection.cursor()

    # -------------------- Get Aircraft ---------------
    result = cur.execute("SELECT * FROM aircraft_basic_information_entry")

    aircrafts = cur.fetchall()

    if result > 0:
        return render_template('Wheel_Assembly_Subsystems/List_All_Aircraft.html', aircraft=aircrafts)
    else:
        msg = 'No Aircraft Found'
        return render_template('dashboard.html', msg=msg)
    # ---------Close Connection--------------
    cur.close()

    return render_template('dashboard.html')


# --------------------------------Add Aircraft Information Entry---------------------------------

class AddAircraftInformationEntry(Form):
    aircraft_name = StringField('Aircraft Name', [validators.length(min=1, max=50)])
    first_assembly_date = StringField('First Assembly Date', [validators.length(min=1, max=50)])
    chief_designer = StringField('Chief Designer', [validators.length(min=4, max=25)])
    description_of_use = StringField('Description of Use', [validators.length(min=6, max=50)])
    primary_customer = StringField('The Primary Customer', [validators.length(min=6, max=50)])
    list_of_parts_suppliers = TextAreaField('List of Parts Suppliers', [validators.length(min=6, max=50)])


@app.route('/add_aircraft_basic_information_entry', methods=['GET', 'POST'])
def add_aircraft_information_Entry():
    form = AddAircraftInformationEntry(request.form)
    if request.method == 'POST' and form.validate():
        aircraft_name = form.aircraft_name.data
        first_assembly_date = form.first_assembly_date.data
        chief_designer = form.chief_designer.data
        description_of_use = form.description_of_use.data
        primary_customer = form.primary_customer.data
        list_of_parts_suppliers = form.list_of_parts_suppliers.data

        cur = mysql.connection.cursor()

        # Execute Query
        cur.execute("INSERT INTO aircraft_basic_information_entry (aircraft_name, first_assembly_date, "
                    "chief_designer,description_of_use, "
                    "primary_customer, list_of_parts_suppliers) VALUES (%s, %s, %s, %s, %s, %s)",
                    (aircraft_name, first_assembly_date, chief_designer, description_of_use,
                     primary_customer, list_of_parts_suppliers))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Aircraft Information Added successful', 'success')

    # ------ Clear Form Fields ------
    form.aircraft_name.data = ""
    form.first_assembly_date.data = ""
    form.chief_designer.data = ""
    form.description_of_use.data = ""
    form.primary_customer.data = ""
    form.list_of_parts_suppliers.data = ""

    return render_template('Aircraft_Basic_Information_Entry/add_aircraft_information.html', form=form)


# ----------------------------------Class Update Wheel Assembly Subsystems------------------------
class UpdateWheelAssemblySubsystems(Form):
    parts_required_for_the_assembly = StringField('Parts Required for the Assembly',
                                                  [validators.length(min=1, max=500)])
    the_number_on_hand = StringField('The Number On-hand', [validators.length(min=1, max=500)])
    the_price_for_the_part = StringField('The Price for the Part', [validators.length(min=1, max=500)])
    description_of_the_part = StringField('Description of the Part', [validators.length(min=1, max=500)])


# --------------------------------Method Update Wheel Assembly Subsystem---------------------------------

@app.route('/update_wheel_assembly', methods=['GET', 'POST'])
def update_wheel_assembly_subsystems():
    form = UpdateWheelAssemblySubsystems(request.form)
    if request.method == 'POST' and form.validate():
        parts_required_for_the_assembly = form.parts_required_for_the_assembly.data
        the_number_on_hand = form.the_number_on_hand.data
        the_price_for_the_part = form.the_price_for_the_part.data
        description_of_the_part = form.description_of_the_part.data

        cur = mysql.connection.cursor()

        # Execute Query
        cur.execute("INSERT INTO wheel_assembly_subsystems(parts_required_for_the_assembly, the_number_on_hand, "
                    "the_price_for_the_part, "
                    "description_of_the_part) VALUES (%s, %s, %s, %s)",
                    (parts_required_for_the_assembly, the_number_on_hand, the_price_for_the_part,
                     description_of_the_part))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Wheel Assembly Subsystem Updated successful', 'success')
        # ------ Clear Form Fields ------
        form.parts_required_for_the_assembly.data = ""
        form.the_number_on_hand.data = ""
        form.the_price_for_the_part.data = ""
        form.description_of_the_part.data = ""

    return render_template('Wheel_Assembly_Subsystems/update_wheel_assembly_subsystem.html', form=form)


# -------- Search Aircraft------
class Search(Form):
    search_term = StringField('Enter the Name of the Aeroplane', [validators.length(min=1, max=50)])


@app.route('/aircraft_search', methods=['GET', 'POST'])
def search_plane():
    form = Search(request.form)
    if request.method == 'POST' and form.validate():
        search_term = form.search_term.data

        flash('Registration successful', 'success')

        return redirect(url_for('login'))

    return render_template('Aircraft_Basic_Information_Entry/aircraft_search.html', form=form)


# ---------------------Logout------------------
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('Logout successful', 'success')
    return redirect(url_for('login'))


secret = secrets.token_urlsafe(32)
app.secret_key = secret
if __name__ == '__main__':
    app.run(debug=True)
