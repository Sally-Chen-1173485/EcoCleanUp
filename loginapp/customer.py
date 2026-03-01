from loginapp import app
from loginapp import db
from flask import redirect, render_template, session, url_for, request, flash
from datetime import date

@app.route('/customer/home', methods=['GET','POST'])
def customer_home():
     """Customer Homepage endpoint.

     Methods:
     - GET: Renders the homepage including a list of upcoming events with
       optional filters and the volunteer's past registrations/feedback.
     - POST: Handles event registration or feedback submission.

     If the user is not logged in, requests will redirect to the login page.
     """
     # Note: You'll need to use "logged in" and role checks like the ones below
     # on every single endpoint that should be restricted to logged-in users,
     # or users with a certain role. Otherwise, anyone who knows the URL can
     # access that page.
     #
     # In this example we've just repeated the code everywhere (you'll see the
     # same checks in staff.py and admin.py), but it would be a great idea to
     # extract these checks into reusable functions. You could place them in
     # user.py with the rest of the login system, for example, and import them
     # into other modules as necessary.
     #
     # One common way to implement login and role checks in Flask is with "View
     # Decorators", such as the "login_required" example in the official
     # tutorial [1]. If you choose to use that approach, you'll need to adapt
     # it a little to our project, as we don't store the username in `g.user`.
     #
     # References:
     # [1] https://flask.palletsprojects.com/en/stable/patterns/viewdecorators/

     if 'loggedin' not in session:
          # The user isn't logged in, so redirect them to the login page.
          return redirect(url_for('login'))
     elif session['role']!='Volunteers':
          # The user isn't logged in with a customer account, so return an
          # "Access Denied" page instead. We don't do a redirect here, because
          # we're not sending them somewhere else: just delivering an
          # alternative page.
          # 
          # Note: the '403' below returns HTTP status code 403: Forbidden to the
          # browser, indicating that the user was not allowed to access the
          # requested page.
          return render_template('access_denied.html'), 403

     # The user is logged in with a customer account; now we handle
     # event browsing, registration, and feedback.
     user_id = session['user_id']

     # handle POST actions for registration or feedback
     if request.method == 'POST':
          if 'register_event' in request.form:
               event_id = request.form.get('event_id')
               with db.get_cursor() as cursor:
                    cursor.execute(
                        'SELECT registration_id FROM eventregistrations '
                        'WHERE event_id = %s AND volunteer_id = %s;',
                        (event_id, user_id))
                    if cursor.fetchone():
                         flash('You are already registered for that event.', 'info')
                    else:
                         cursor.execute(
                             'INSERT INTO eventregistrations '
                             '(event_id, volunteer_id, registered_at) '
                             'VALUES (%s, %s, NOW());',
                             (event_id, user_id))
                         flash('Registration successful!', 'success')
          elif 'feedback_event' in request.form:
               event_id = request.form.get('event_id')
               rating = request.form.get('rating')
               comments = request.form.get('comments', '')
               with db.get_cursor() as cursor:
                    cursor.execute(
                        'SELECT 1 FROM eventregistrations '
                        'WHERE event_id = %s AND volunteer_id = %s;',
                        (event_id, user_id))
                    if cursor.fetchone():
                         cursor.execute(
                             'INSERT INTO feedback '
                             '(event_id, volunteer_id, rating, comments, submitted_at) '
                             'VALUES (%s, %s, %s, %s, NOW());',
                             (event_id, user_id, rating, comments))
                         flash('Thank you for your feedback!', 'success')
                    else:
                         flash('You can only give feedback for events you attended.', 'danger')

          # redirect to avoid form resubmission
          return redirect(url_for('customer_home'))

     # gather filters from query string
     date_from = request.args.get('date_from', '')
     date_to = request.args.get('date_to', '')
     location = request.args.get('location', '')
     evtype = request.args.get('event_type', '')

     # build query for upcoming events
     query = 'SELECT * FROM events WHERE event_date >= %s'
     params = [date.today()]
     if date_from:
          query += ' AND event_date >= %s'
          params.append(date_from)
     if date_to:
          query += ' AND event_date <= %s'
          params.append(date_to)
     if location:
          query += ' AND location_ LIKE %s'
          params.append(f"%{location}%")
     if evtype:
          query += ' AND event_type = %s'
          params.append(evtype)
     query += ' ORDER BY event_date ASC'

     with db.get_cursor() as cursor:
          cursor.execute(query, tuple(params))
          upcoming_events = cursor.fetchall()

          cursor.execute(
              'SELECT event_id FROM eventregistrations '
              'JOIN events USING(event_id) '
              'WHERE volunteer_id = %s AND event_date >= %s;',
              (user_id, date.today()))
          reg_rows = cursor.fetchall()
          registered_ids = {r['event_id'] for r in reg_rows}

          cursor.execute(
              '''
              SELECT t4.*, t2.rating, t2.comments
              FROM events t4
              JOIN eventregistrations t3 ON t4.event_id=t3.event_id
              LEFT JOIN feedback t2 ON t2.event_id=t4.event_id AND t2.volunteer_id=%s
              WHERE t3.volunteer_id=%s AND t4.event_date < %s
              ORDER BY t4.event_date DESC;
              ''',
              (user_id, user_id, date.today()))
          past_events = cursor.fetchall()

     return render_template('customer_home.html',
                            upcoming_events=upcoming_events,
                            registered_ids=registered_ids,
                            past_events=past_events,
                            date_from=date_from,
                            date_to=date_to,
                            location=location,
                            event_type=evtype)