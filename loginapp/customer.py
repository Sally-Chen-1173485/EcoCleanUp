from loginapp import app
from loginapp import db
from flask import redirect, render_template, session, url_for, request, flash
from datetime import date, datetime


def _ensure_volunteer_logged_in():
     if 'loggedin' not in session:
          return redirect(url_for('login'))
     if session.get('role') != 'Volunteers':
          return render_template('access_denied.html'), 403
     return None

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

     guard_response = _ensure_volunteer_logged_in()
     if guard_response is not None:
          return guard_response

     # The user is logged in with a customer account; now we handle
     # event browsing, registration, and feedback.
     user_id = session['user_id']

     # handle POST actions for registration or feedback
     if request.method == 'POST':
          if 'register_event' in request.form:
               event_id = request.form.get('event_id')
               with db.get_cursor() as cursor:
                    cursor.execute('''
                         SELECT event_id, event_date, start_time, end_time
                         FROM events
                         WHERE event_id = %s;
                    ''', (event_id,))
                    selected_event = cursor.fetchone()

                    if not selected_event:
                         flash('Selected event does not exist.', 'danger')
                         return redirect(url_for('customer_home'))

                    now = datetime.now()
                    if (
                         selected_event['event_date'] < now.date()
                         or (
                              selected_event['event_date'] == now.date()
                              and selected_event['end_time'] is not None
                              and selected_event['end_time'] <= now.time()
                         )
                    ):
                         flash('You cannot register for events that are in the past.', 'warning')
                         return redirect(url_for('customer_home'))

                    cursor.execute(
                         'SELECT registration_id FROM eventregistrations '
                         'WHERE event_id = %s AND volunteer_id = %s;',
                         (event_id, user_id)
                    )
                    if cursor.fetchone():
                         flash('You are already registered for that event.', 'info')
                    else:
                         cursor.execute('''
                              SELECT t4.event_name, t4.start_time, t4.end_time
                              FROM eventregistrations t3
                              JOIN events t4 ON t4.event_id = t3.event_id
                              WHERE t3.volunteer_id = %s
                                AND t4.event_date = %s
                                AND t4.event_id <> %s
                                AND (
                                     %s IS NULL OR %s IS NULL
                                     OR t4.start_time IS NULL OR t4.end_time IS NULL
                                     OR (t4.start_time < %s AND t4.end_time > %s)
                                )
                              LIMIT 1;
                         ''', (
                              user_id,
                              selected_event['event_date'],
                              selected_event['event_id'],
                              selected_event['start_time'],
                              selected_event['end_time'],
                              selected_event['end_time'],
                              selected_event['start_time']
                         ))
                         conflicting_event = cursor.fetchone()

                         if conflicting_event:
                              flash('You cannot register for another event at the same time (or same date when time is unspecified).', 'warning')
                              return redirect(url_for('customer_home'))

                         cursor.execute(
                              'INSERT INTO eventregistrations '
                              '(event_id, volunteer_id, registered_at) '
                              'VALUES (%s, %s, NOW());',
                              (event_id, user_id)
                         )
                         flash('Registration successful!', 'success')

          elif 'feedback_event' in request.form:
               event_id = request.form.get('event_id')
               rating = request.form.get('rating')
               comments = request.form.get('comments', '')
               with db.get_cursor() as cursor:
                    cursor.execute(
                         'SELECT 1 FROM eventregistrations '
                         'WHERE event_id = %s AND volunteer_id = %s;',
                         (event_id, user_id)
                    )
                    if cursor.fetchone():
                         cursor.execute(
                              'INSERT INTO feedback '
                              '(event_id, volunteer_id, rating, comments, submitted_at) '
                              'VALUES (%s, %s, %s, %s, NOW());',
                              (event_id, user_id, rating, comments)
                         )
                         flash('Thank you for your feedback!', 'success')
                    else:
                         flash('You can only give feedback for events you attended.', 'danger')

          return redirect(url_for('customer_home'))

     date_from = request.args.get('date_from', '')
     date_to = request.args.get('date_to', '')
     location = request.args.get('location', '')
     evtype = request.args.get('event_type', '')
     past_scope = request.args.get('past_scope', 'all')
     if past_scope not in ('all', 'mine'):
          past_scope = 'all'

     query = 'SELECT * FROM events WHERE event_date >= %s'
     params = [date.today()]
     if date_from:
          query += ' AND event_date >= %s'
          params.append(date_from)
     if date_to:
          query += ' AND event_date <= %s'
          params.append(date_to)
     if location:
          query += ' AND location_ ILIKE %s'
          params.append(f"%{location}%")
     if evtype:
          query += ' AND event_type ILIKE %s'
          params.append(evtype)
     query += ' ORDER BY event_date ASC'

     with db.get_cursor() as cursor:
          cursor.execute(query, tuple(params))
          upcoming_events = cursor.fetchall()

          cursor.execute(
               'SELECT event_id FROM eventregistrations '
               'JOIN events USING(event_id) '
               'WHERE volunteer_id = %s AND event_date >= %s;',
               (user_id, date.today())
          )
          reg_rows = cursor.fetchall()
          registered_ids = {r['event_id'] for r in reg_rows}

          past_query = '''
               SELECT t4.*, t2.rating, t2.comments,
                      (t3.registration_id IS NOT NULL) AS is_registered
               FROM events t4
               LEFT JOIN eventregistrations t3
                 ON t4.event_id=t3.event_id AND t3.volunteer_id=%s
               LEFT JOIN feedback t2
                 ON t2.event_id=t4.event_id AND t2.volunteer_id=%s
               WHERE t4.event_date < %s
          '''
          past_params = [user_id, user_id, date.today()]
          if past_scope == 'mine':
               past_query += ' AND t3.registration_id IS NOT NULL'
          past_query += ' ORDER BY t4.event_date DESC;'

          cursor.execute(past_query, tuple(past_params))
          past_events = cursor.fetchall()

          cursor.execute(
               '''
               SELECT t4.event_id, t4.event_name, t4.event_date, t4.start_time, t4.end_time, t4.location_
               FROM eventregistrations t3
               JOIN events t4 ON t3.event_id = t4.event_id
               WHERE t3.volunteer_id = %s
                 AND t4.event_date >= %s
               ORDER BY t4.event_date ASC, t4.start_time ASC NULLS LAST;
               ''',
               (user_id, date.today())
          )
          reminder_events = cursor.fetchall()

          cursor.execute(
               '''
               SELECT t3.registration_id AS reminder_id,
                      t3.reminder_message AS message,
                      t3.reminder_sent_at AS sent_at,
                      t4.event_id, t4.event_name, t4.event_date, t4.start_time, t4.end_time, t4.location_
               FROM eventregistrations t3
                                    JOIN events t4 ON t3.event_id = t4.event_id
               WHERE t3.volunteer_id = %s
                 AND t3.reminder_pending = TRUE
               ORDER BY t3.reminder_sent_at DESC NULLS LAST;
               ''',
               (user_id,)
          )
          reminder_notifications = cursor.fetchall()

          if reminder_notifications:
               reminder_ids = [n['reminder_id'] for n in reminder_notifications]
               cursor.execute(
                    'UPDATE eventregistrations SET reminder_pending = FALSE WHERE registration_id = ANY(%s);',
                    (reminder_ids,)
               )

     return render_template(
          'customer_home.html',
          upcoming_events=upcoming_events,
          registered_ids=registered_ids,
          past_events=past_events,
          reminder_events=reminder_events,
          reminder_notifications=reminder_notifications,
          date_from=date_from,
          date_to=date_to,
          location=location,
          event_type=evtype,
          past_scope=past_scope
     )


@app.route('/customer/event/<int:event_id>')
def customer_event_detail(event_id):
     """Shared event detail page for volunteers, event leaders and admins."""
     if 'loggedin' not in session:
          return redirect(url_for('login'))
     if session.get('role') not in ('Volunteers', 'Event Leaders', 'Administrators'):
          return render_template('access_denied.html'), 403

     user_id = session['user_id']
     is_volunteer = session.get('role') == 'Volunteers'
     with db.get_cursor() as cursor:
          cursor.execute('''
               SELECT t4.*, t1.full_name AS leader_name
               FROM events t4
               LEFT JOIN users t1 ON t4.event_leader_id = t1.user_id
               WHERE t4.event_id = %s;
          ''', (event_id,))
          event = cursor.fetchone()

          if not event:
               flash('Event not found.', 'danger')
               return redirect(url_for('customer_home'))

          if is_volunteer:
               cursor.execute('''
                    SELECT registration_id
                    FROM eventregistrations
                    WHERE event_id = %s AND volunteer_id = %s;
               ''', (event_id, user_id))
               is_registered = cursor.fetchone() is not None
          else:
               is_registered = False

     if session['role'] == 'Event Leaders':
          back_url = url_for('staff_home')
     elif session['role'] == 'Administrators':
          back_url = url_for('admin_events')
     else:
          back_url = url_for('customer_home')

     return render_template(
          'event_detail.html',
          event=event,
          volunteers=[],
          outcome=None,
          feedbacks=[],
          can_manage_event=False,
          is_registered=is_registered,
          deregister_url=url_for('customer_deregister_event', event_id=event_id),
          back_url=back_url,
          back_label='Back to Event List',
          now=datetime.now()
     )


@app.route('/customer/event/<int:event_id>/deregister', methods=['POST'])
def customer_deregister_event(event_id):
     """Allow a volunteer to remove their own registration from an event."""
     guard_response = _ensure_volunteer_logged_in()
     if guard_response is not None:
          return guard_response

     user_id = session['user_id']
     with db.get_cursor() as cursor:
          cursor.execute('''
               SELECT registration_id
               FROM eventregistrations
               WHERE event_id = %s AND volunteer_id = %s;
          ''', (event_id, user_id))
          registration = cursor.fetchone()

          if not registration:
               flash('You are not registered for this event.', 'warning')
               return redirect(url_for('customer_event_detail', event_id=event_id))

          cursor.execute('''
               DELETE FROM eventregistrations
               WHERE event_id = %s AND volunteer_id = %s;
          ''', (event_id, user_id))

     flash('You have deregistered from this event.', 'success')
     return redirect(url_for('customer_home'))