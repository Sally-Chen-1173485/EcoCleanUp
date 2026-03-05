from loginapp import app
from loginapp import db
from flask import redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
import re
import os
import uuid
from werkzeug.utils import secure_filename

# Create an instance of the Bcrypt class, which we'll be using to hash user
# passwords during login and registration.
flask_bcrypt = Bcrypt(app)

# Default role assigned to new users upon registration.
default_user_role = 'Volunteers'
default_status= 'active'

ALLOWED_PROFILE_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
DEFAULT_PROFILE_IMAGE = 'default_plant.jpg'

def get_default_profile_image_filename():
    """Return the default profile image filename available in /static."""
    preferred_default_path = os.path.join(app.root_path, 'static', DEFAULT_PROFILE_IMAGE)
    if os.path.exists(preferred_default_path):
        return DEFAULT_PROFILE_IMAGE
    return 'image1.jpg'

def upload_profile_image(file):
    """Save an uploaded profile image and return (db_path, error_message).

    - db_path is a relative path such as "uploads/abc123.jpg" for DB storage.
    - error_message is None on success, or a user-facing validation message.
    """
    if file is None or file.filename == '':
        return None, None

    filename = secure_filename(file.filename)
    if '.' not in filename:
        return None, 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WEBP.'

    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in ALLOWED_PROFILE_IMAGE_EXTENSIONS:
        return None, 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WEBP.'

    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, unique_filename))

    return f'uploads/{unique_filename}', None

def delete_uploaded_profile_image(file_path):
    """Delete an uploaded profile image file if it lives under static/uploads."""
    if not file_path or not file_path.startswith('uploads/'):
        return

    abs_path = os.path.join(app.root_path, 'static', file_path)
    if os.path.exists(abs_path):
        os.remove(abs_path)

def user_home_url():
    """Generates a URL to the homepage for the currently logged-in user.
    
    If the user is not logged in, this returns the URL for the login page
    instead. If the user appears to be logged in, but the role stored in their
    session cookie is invalid (i.e. not a recognised role), it returns the URL
    for the logout page to clear that invalid session data."""
    if 'loggedin' in session:
        role = session.get('role', None)

        if role == 'Volunteers':
            home_endpoint='customer_home'
        elif role == 'Event Leaders':
            home_endpoint='staff_home'
        elif role == 'Administrators':
            home_endpoint='admin_home'
        else:
            home_endpoint = 'logout'
    else:
        home_endpoint = 'login'
    
    return url_for(home_endpoint)

@app.route('/')
def root():
    """Root endpoint (/)
    
    Methods:
    - get: Redirects guests to the login page, and redirects logged-in users to
        their own role-specific homepage.
    """
    if 'loggedin' in session:
        return redirect(user_home_url())
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page endpoint.

    Methods:
    - get: Renders the login page.
    - post: Attempts to log the user in using the credentials supplied via the
        login form, and either:
        - Redirects the user to their role-specific homepage (if successful)
        - Renders the login page again with an error message (if unsuccessful).
    
    If the user is already logged in, both get and post requests will redirect
    to their role-specific homepage.
    """
    if 'loggedin' in session:
         return redirect(user_home_url())

    if request.method=='POST' and 'username' in request.form and 'password' in request.form:
        # Get the login details submitted by the user.
        username = request.form['username']
        password = request.form['password']

        # Attempt to validate the login details against the database.
        with db.get_cursor() as cursor:
            # Try to retrieve the account details for the specified username.
            #
            # Note: we use a Python multiline string (triple quote) here to
            # make the query more readable in source code. This is just a style
            # choice: the line breaks are ignored by MySQL, and it would be
            # equally valid to put the whole SQL statement on one line like we
            # do at the beginning of the `signup` function.
            cursor.execute('''
                           SELECT user_id, username, password_hash, role
                           FROM users
                           WHERE username = %s;
                           ''', (username,))
            account = cursor.fetchone()
            
            if account is not None:
                # We found a matching account: now we need to check whether the
                # password they supplied matches the hash in our database.
                password_hash = account['password_hash']
                
                if flask_bcrypt.check_password_hash(password_hash, password):
                    # Password is correct. Save the user's ID, username, and role
                    # as session data, which we can access from other routes to
                    # determine who's currently logged in.
                    # 
                    # Users can potentially see and edit these details using their
                    # web browser. However, the session cookie is signed with our
                    # app's secret key. That means if they try to edit the cookie
                    # to impersonate another user, the signature will no longer
                    # match and Flask will know the session data is invalid.
                    session['loggedin'] = True
                    session['user_id'] = account['user_id']
                    session['username'] = account['username']
                    session['role'] = account['role']

                    return redirect(user_home_url())
                else:
                    # Password is incorrect. Re-display the login form, keeping
                    # the username provided by the user so they don't need to
                    # re-enter it. We also set a `password_invalid` flag that
                    # the template uses to display a validation message.
                    return render_template('login.html',
                                           username=username,
                                           password_invalid=True)
            else:
                # We didn't find an account in the database with this username.
                # Re-display the login form, keeping the username so the user
                # can see what they entered (otherwise, they might just keep
                # trying the same thing). We also set a `username_invalid` flag
                # that tells the template to display an appropriate message.
                #
                # Note: In this example app, we tell the user if the user
                # account doesn't exist. Many websites (e.g. Google, Microsoft)
                # do this, but other sites display a single "Invalid username
                # or password" message to prevent an attacker from determining
                # whether a username exists or not. Here, we accept that risk
                # to provide more useful feedback to the user.
                return render_template('login.html', 
                                       username=username,
                                       username_invalid=True)

    # This was a GET request, or an invalid POST (no username and/or password),
    # so we just render the login form with no pre-populated details or flags.
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    """Signup (registration) page endpoint.

    Methods:
    - get: Renders the signup page.
    - post: Attempts to create a new user account using the details supplied
        via the signup form, then renders the signup page again with a welcome
        message (if successful) or one or more error message(s) explaining why
        signup could not be completed.

    If the user is already logged in, both get and post requests will redirect
    to their role-specific homepage.
    """
    if 'loggedin' in session:
         return redirect(user_home_url())
    
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form \
       and 'password_confirm' in request.form and 'full_name' in request.form and 'home_address' in request.form \
       and 'contact_number' in request.form and 'environmental_interests' in request.form:
        # Get the details submitted via the form on the signup page.
        username = request.form['username']
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        home_address = request.form['home_address']
        contact_number = request.form['contact_number']
        environmental_interests = request.form['environmental_interests']
        uploaded_profile_image = request.files.get('profile_image')
        profile_image, profile_image_upload_error = upload_profile_image(uploaded_profile_image)
        if not profile_image and not profile_image_upload_error:
            profile_image = get_default_profile_image_filename()

           

         
    

        # We start by assuming that everything is okay. If we encounter any
        # errors during validation, we'll store an error message in one or more
        # of these variables so we can pass them through to the template.
        username_error = None
        email_error = None
        password_error = None
        password_confirm_error = None
        full_name_error = None
        home_address_error = None
        contact_number_error = None
        env_interest_error = None
        profile_image_error = profile_image_upload_error

        # Check whether there's an account with this username in the database.
        with db.get_cursor() as cursor:
            cursor.execute('SELECT user_id FROM users WHERE username = %s;',
                           (username,))
            account_already_exists = cursor.fetchone() is not None
        
        # Validate the username, ensuring that it's unique (as we just checked
        # above) and meets the naming constraints of our web app.
        if account_already_exists:
            username_error = 'An account already exists with this username.'
        elif len(username) > 20:
            # The user should never see this error during normal conditions,
            # because we set a maximum length of 20 on the input field in the
            # template. However, a user or attacker could easily override that
            # and submit a longer value, so we need to handle that case.
            username_error = 'Your username cannot exceed 20 characters.'
        elif not re.match(r'[A-Za-z0-9]+', username):
            username_error = 'Your username can only contain letters and numbers.'            

        # Validate the new user's email address. Note: The regular expression
        # we use here isn't a perfect check for a valid address, but is
        # sufficient for this example.
        if len(email) > 100:
            email_error = 'Your email address cannot exceed 100 characters.'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            email_error = 'Invalid email address.'
                
        # Validate password. Think about what other constraints might be useful
        # here for security (e.g. requiring a certain mix of character types,
        # or avoiding overly-common passwords). Make sure that you clearly
        # communicate any rules to the user, either through hints on the signup
        # page or with clear error messages here.
        #
        # Note: Unlike the username and email address, we don't enforce a
        # maximum password length. Because we'll be storing a hash of the
        # password in our database, and not the password itself, it doesn't
        # matter how long a password the user chooses. Whether it's 8 or 800
        # characters, the hash will always be the same length.
        if len(password) < 8:
            password_error = 'Please choose a longer password!'
        elif password != password_confirm:
            password_confirm_error = 'Passwords do not match!'

        # Full name validation
        if not full_name or len(full_name) > 100:
            full_name_error = 'Full name is required and cannot exceed 100 characters.'

        # Home address validation
        if not home_address or len(home_address) > 255:
            home_address_error = 'Home address is required and must be under 255 characters.'

        # Contact number validation (simple length check, digits/spaces/hyphens)
        if not contact_number or len(contact_number) > 20 or not re.match(r'^[0-9\s\-+()]+$', contact_number):
            contact_number_error = 'Contact number required (max 20 chars, digits/spaces/hyphens).'

        # Environmental interests validation
        if not environmental_interests or len(environmental_interests) > 255:
            env_interest_error = 'Please describe at least one interest (max 255 chars).'

        # Profile image path (optional) length check
        if profile_image and len(profile_image) > 255:
            profile_image_error = 'Profile image path must be under 255 characters.'

        if (username_error or email_error or password_error or password_confirm_error or full_name_error or
            home_address_error or contact_number_error or env_interest_error or
            profile_image_error):
            # One or more validations failed; re-render form with previously
            # supplied values (except password) and error messages.
            return render_template('signup.html',
                                   username=username,
                                   full_name=full_name,
                                   email=email,
                                   home_address=home_address,
                                   contact_number=contact_number,
                                   environmental_interests=environmental_interests,
                                   username_error=username_error,
                                   full_name_error=full_name_error,
                                   email_error=email_error,
                                   password_error=password_error,
                                   password_confirm_error=password_confirm_error,
                                   home_address_error=home_address_error,
                                   contact_number_error=contact_number_error,
                                   env_interest_error=env_interest_error,
                                   profile_image_error=profile_image_error)
        else:
            # The new account details are valid. Hash the user's new password
            # and create their account in the database.
            password_hash = flask_bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Note: In this example, we just assume the SQL INSERT statement
            # below will run successfully. But what if it doesn't?
            #
            # If the INSERT fails for any reason, MySQL Connector will throw an
            # exception and the user will receive a generic error page. We
            # should implement our own error handling here to deal with that
            # possibility, and display a more useful message to the user.
            with db.get_cursor() as cursor:
                cursor.execute('''
                               INSERT INTO users (
                                   username, full_name, password_hash, email,
                                   contact_number, home_address, profile_image,
                                   environmental_interests, role, status)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                               ''',
                               (username, full_name, password_hash, email,
                                contact_number, home_address, profile_image,
                                environmental_interests, default_user_role, default_status))
            
            # Now that registration is complete, send the user back to the
            # signup page. We set the `signup_successful` flag to display a
            # post-signup message.
            return render_template('signup.html', signup_successful=True)            

    # This was a GET request, or an invalid POST (missing required fields).
    # Provide empty defaults for all template variables so Jinja doesn't raise
    # an undefined error.
    return render_template('signup.html',
                           username='', full_name='', email='',
                           home_address='', contact_number='',
                           environmental_interests='', profile_image='',
                           password_confirm_error=None)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """User Profile page endpoint.

    GET: Render a form containing the current user's profile details.
    POST: Validate and save updates to the fields that users are allowed to
    change (full name, home address, contact number, environmental
    interests and profile image).  If validation fails we re-display the form
    with appropriate error messages; on success a confirmation banner is shown.

    The user must be logged in to access this page; otherwise they're sent to
    the login screen.
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    # default error variables and success flag
    full_name_error = None
    home_address_error = None
    contact_number_error = None
    env_interest_error = None
    profile_image_error = None
    # password change errors
    current_password_error = None
    new_password_error = None
    confirm_password_error = None
    profile_updated = False

    # fetch current profile data (we'll show these values in the form)
    with db.get_cursor() as cursor:
        cursor.execute('''
            SELECT username, email, role, full_name, home_address,
                   contact_number, environmental_interests, profile_image,
                   password_hash
            FROM users
            WHERE user_id = %s;
        ''', (session['user_id'],))
        profile = cursor.fetchone()

    default_profile_image = get_default_profile_image_filename()
    if not profile.get('profile_image'):
        profile['profile_image'] = default_profile_image
        with db.get_cursor() as cursor:
            cursor.execute(
                'UPDATE users SET profile_image = %s WHERE user_id = %s;',
                (default_profile_image, session['user_id'])
            )

    # handle form submission
    if request.method == 'POST':
        # grab submitted values (strip to avoid leading/trailing spaces)
        full_name = request.form.get('full_name', '').strip()
        home_address = request.form.get('home_address', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        environmental_interests = request.form.get('environmental_interests', '').strip()
        profile_image = profile.get('profile_image')
        uploaded_profile_image = request.files.get('profile_image_file')
        delete_profile_image_requested = request.form.get('delete_profile_image') == '1'
        image_upload_only = request.form.get('image_upload_only') == '1'

        # password change fields (may be blank if user isn't changing)

        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # delete current image (revert to default display image)
        if delete_profile_image_requested:
            delete_uploaded_profile_image(profile.get('profile_image'))
            profile_image = default_profile_image
            with db.get_cursor() as cursor:
                cursor.execute('''
                    UPDATE users
                    SET profile_image = %s
                    WHERE user_id = %s;
                ''', (default_profile_image, session['user_id']))

            profile_updated = True
            profile['profile_image'] = default_profile_image

        # upload new image
        elif uploaded_profile_image and uploaded_profile_image.filename:
            new_profile_image, image_upload_error = upload_profile_image(uploaded_profile_image)
            if image_upload_error:
                profile_image_error = image_upload_error
            else:
                delete_uploaded_profile_image(profile.get('profile_image'))
                profile_image = new_profile_image
                with db.get_cursor() as cursor:
                    cursor.execute('''
                        UPDATE users
                        SET profile_image = %s
                        WHERE user_id = %s;
                    ''', (profile_image, session['user_id']))

                profile_updated = True
                profile['profile_image'] = profile_image

        # If this submit was just from selecting an image, stop here and re-render.
        if image_upload_only or delete_profile_image_requested:
            return render_template('profile.html',
                                   profile=profile,
                                   full_name_error=full_name_error,
                                   home_address_error=home_address_error,
                                   contact_number_error=contact_number_error,
                                   env_interest_error=env_interest_error,
                                   profile_image_error=profile_image_error,
                                   current_password_error=current_password_error,
                                   new_password_error=new_password_error,
                                   confirm_password_error=confirm_password_error,
                                   profile_updated=profile_updated,
                                   default_profile_image=default_profile_image)

        # validate inputs (same rules as signup)
        if not full_name or len(full_name) > 100:
            full_name_error = 'Full name is required and cannot exceed 100 characters.'
        if not home_address or len(home_address) > 255:
            home_address_error = 'Home address is required and must be under 255 characters.'
        if (not contact_number or len(contact_number) > 20 or
            not re.match(r'^[0-9\s\-+()]+$', contact_number)):
            contact_number_error = 'Contact number required (max 20 chars, digits/spaces/hyphens).'
        if not environmental_interests or len(environmental_interests) > 255:
            env_interest_error = 'Please describe at least one interest (max 255 chars).'
        if profile_image and len(profile_image) > 255:
            profile_image_error = 'Profile image path must be under 255 characters.'

        # handle password change if any field provided
        if current_password or new_password or confirm_password:
            # all three must be present
            if not current_password:
                current_password_error = 'Current password is required to change password.'
            elif not flask_bcrypt.check_password_hash(profile['password_hash'], current_password):
                current_password_error = 'Current password is incorrect.'
            if not new_password:
                new_password_error = 'New password cannot be blank.'
            elif len(new_password) < 8:
                new_password_error = 'New password must be at least 8 characters.'
            if new_password and new_password != confirm_password:
                confirm_password_error = 'Passwords do not match.'
            if current_password and new_password and new_password == current_password:
                new_password_error = 'New password must be different from current password.'
            if new_password and flask_bcrypt.check_password_hash(profile['password_hash'], new_password):
                new_password_error = 'New password must be different from current password.'

        if new_password and not new_password_error:
            with db.get_cursor() as cursor:
                cursor.execute('SELECT password_hash FROM users WHERE user_id = %s;', (session['user_id'],))
                latest_password_hash = cursor.fetchone()['password_hash']
            if flask_bcrypt.check_password_hash(latest_password_hash, new_password):
                new_password_error = 'New password must be different from current password.'
           
        # if there are no errors, write values back to the database
        if not (full_name_error or home_address_error or contact_number_error or
                env_interest_error or profile_image_error or
                current_password_error or new_password_error or confirm_password_error):
            with db.get_cursor() as cursor:
                # update profile fields
                cursor.execute('''
                    UPDATE users
                    SET full_name = %s,
                        home_address = %s,
                        contact_number = %s,
                        environmental_interests = %s,
                        profile_image = %s
                    WHERE user_id = %s;
                ''', (full_name, home_address, contact_number,
                      environmental_interests, profile_image,
                      session['user_id']))

                # if password change requested, hash and update
                if new_password and not new_password_error:
                    new_hash = flask_bcrypt.generate_password_hash(new_password).decode('utf-8')
                    cursor.execute('''
                        UPDATE users
                        SET password_hash = %s
                        WHERE user_id = %s;
                    ''', (new_hash, session['user_id']))

            profile_updated = True
            # update profile dict so the template shows current values
            profile['full_name'] = full_name
            profile['home_address'] = home_address
            profile['contact_number'] = contact_number
            profile['environmental_interests'] = environmental_interests
            profile['profile_image'] = profile_image
        else:
            # reflect submitted values on failure so user can correct them
            profile['full_name'] = full_name
            profile['home_address'] = home_address
            profile['contact_number'] = contact_number
            profile['environmental_interests'] = environmental_interests
            profile['profile_image'] = profile_image

    return render_template('profile.html',
                           profile=profile,
                           full_name_error=full_name_error,
                           home_address_error=home_address_error,
                           contact_number_error=contact_number_error,
                           env_interest_error=env_interest_error,
                           profile_image_error=profile_image_error,
                           current_password_error=current_password_error,
                           new_password_error=new_password_error,
                           confirm_password_error=confirm_password_error,
                           profile_updated=profile_updated,
                           default_profile_image=default_profile_image)

@app.route('/logout')
def logout():
    """Logout endpoint.

    Methods:
    - get: Logs the current user out (if they were logged in to begin with),
        and redirects them to the login page.
    """
    # Note that nothing actually happens on the server when a user logs out: we
    # just remove the cookie from their web browser. They could technically log
    # back in by manually restoring the cookie we've just deleted. In a high-
    # security web app, you may need additional protections against this (e.g.
    # keeping a record of active sessions on the server side).
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    
    return redirect(url_for('login'))