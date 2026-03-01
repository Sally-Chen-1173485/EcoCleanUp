from loginapp import app
from loginapp import db
from flask import redirect, render_template, session, url_for, request, flash
from datetime import date, datetime
from flask_bcrypt import Bcrypt

flask_bcrypt = Bcrypt(app)


def check_event_leader():
     """Helper to check if user is logged in and is an Event Leader."""
     if 'loggedin' not in session:
          return False
     return session['role'] == 'Event Leaders'


def check_admin():
     """Return True if current user is an administrator."""
     if 'loggedin' not in session:
          return False
     return session['role'] == 'Administrators'


def check_leader_or_admin():
     """Return True if the user is either an Event Leader or an Administrator."""
     if 'loggedin' not in session:
          return False
     return session['role'] in ('Event Leaders', 'Administrators')

@app.route('/staff/home')
def staff_home():
     """Event Leader Homepage - lists their events.

     Methods:
     - get: Renders the homepage listing the logged-in event leader's events.

     If the user is not logged in or not an event leader (or admin), redirects or shows access denied.
     """
     if not check_leader_or_admin():
          return redirect(url_for('login'))
     elif session['role'] not in ('Event Leaders','Administrators'):
          return render_template('access_denied.html'), 403

     user_id = session['user_id']

     # Fetch events. administrators see all, leaders only their own
     with db.get_cursor() as cursor:
          if session['role']=='Administrators':
               cursor.execute('SELECT * FROM events ORDER BY event_date ASC;')
          else:
               cursor.execute(
                   'SELECT * FROM events WHERE event_leader_id = %s ORDER BY event_date ASC;',
                   (user_id,))
          events = cursor.fetchall()

     return render_template('staff_home.html', events=events)

@app.route('/staff/event/create', methods=['GET', 'POST'])
def create_event():
     """Create a new cleanup event."""
     if 'loggedin' not in session:
          return redirect(url_for('login'))
     elif session['role']!='Event Leaders':
          return render_template('access_denied.html'), 403

     user_id = session['user_id']
     errors = {}

     if request.method == 'POST':
          event_name = request.form.get('event_name', '').strip()
          location = request.form.get('location', '').strip()
          event_type = request.form.get('event_type', '').strip()
          event_date = request.form.get('event_date', '').strip()

          if not event_name or len(event_name) > 100:
               errors['event_name'] = 'Event name required (max 100 chars)'
          if not location or len(location) > 255:
               errors['location'] = 'Location required (max 255 chars)'
          if not event_type or len(event_type) > 50:
               errors['event_type'] = 'Event type required (max 50 chars)'
          if not event_date:
               errors['event_date'] = 'Event date required'
          else:
               try:
                    ed = date.fromisoformat(event_date)
                    if ed < date.today():
                         errors['event_date'] = 'Event date cannot be in the past'
               except:
                    errors['event_date'] = 'Invalid date format'

          if not errors:
               with db.get_cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO events (event_name, event_leader_id, location_, event_type, event_date) '
                        'VALUES (%s, %s, %s, %s, %s);',
                        (event_name, user_id, location, event_type, event_date))
               flash('Event created successfully!', 'success')
               return redirect(url_for('staff_home'))

     # use unified template
     return render_template('event.html', mode='create', errors=errors)

@app.route('/staff/event/<int:event_id>')
def event_detail(event_id):
     """View event details with registered volunteers."""
     if not check_leader_or_admin():
          return redirect(url_for('login'))
     elif session['role'] not in ('Event Leaders','Administrators'):
          return render_template('access_denied.html'), 403

     user_id = session['user_id']

     with db.get_cursor() as cursor:
          cursor.execute(
              'SELECT * FROM events WHERE event_id = %s AND event_leader_id = %s;',
              (event_id, user_id))
          event = cursor.fetchone()
          if not event:
               flash('Event not found or you do not have permission.', 'danger')
               return redirect(url_for('staff_home'))

          # Fetch registered volunteers
          cursor.execute(
              '''
              SELECT t3.registration_id, t1.user_id AS volunteer_id, t1.username, t1.full_name, t1.email,
                     t3.attendance, t3.registered_at
              FROM eventregistrations t3
              JOIN users t1 ON t3.volunteer_id = t1.user_id
              WHERE t3.event_id = %s
              ORDER BY t1.username;
              ''',
              (event_id,))
          volunteers = cursor.fetchall()

          # Fetch event outcomes if they exist
          cursor.execute(
              'SELECT * FROM eventoutcomes WHERE event_id = %s;',
              (event_id,))
          outcome = cursor.fetchone()

          # Fetch feedbacks
          cursor.execute(
              '''
              SELECT t2.*, t1.username, t1.full_name
              FROM feedback t2
              JOIN users t1 ON t2.volunteer_id = t1.user_id
              WHERE t2.event_id = %s
              ORDER BY t2.submitted_at DESC;
              ''',
              (event_id,))
          feedbacks = cursor.fetchall()

     # render shared template in detail mode
     # provide current date for badge comparison in template
     return render_template('event.html', mode='detail', event=event,
                            volunteers=volunteers, outcome=outcome, feedbacks=feedbacks,
                            now=datetime.now())

@app.route('/staff/event/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
     """Edit an existing event."""
     if not check_leader_or_admin():
          return redirect(url_for('login'))
     elif session['role'] not in ('Event Leaders','Administrators'):
          return render_template('access_denied.html'), 403

     user_id = session['user_id']
     errors = {}

     with db.get_cursor() as cursor:
          if session['role'] == 'Administrators':
               cursor.execute('SELECT * FROM events WHERE event_id = %s;', (event_id,))
          else:
               cursor.execute(
                   'SELECT * FROM events WHERE event_id = %s AND event_leader_id = %s;',
                   (event_id, user_id))
          event = cursor.fetchone()
          if not event:
               flash('Event not found or you do not have permission.', 'danger')
               return redirect(url_for('staff_home'))

     if request.method == 'POST':
          event_name = request.form.get('event_name', '').strip()
          location = request.form.get('location', '').strip()
          event_type = request.form.get('event_type', '').strip()
          event_date = request.form.get('event_date', '').strip()

          if not event_name or len(event_name) > 100:
               errors['event_name'] = 'Event name required (max 100 chars)'
          if not location or len(location) > 255:
               errors['location'] = 'Location required (max 255 chars)'
          if not event_type or len(event_type) > 50:
               errors['event_type'] = 'Event type required (max 50 chars)'
          if not event_date:
               errors['event_date'] = 'Event date required'

          if not errors:
               with db.get_cursor() as cursor:
                    cursor.execute(
                        'UPDATE events SET event_name = %s, location_ = %s, '
                        'event_type = %s, event_date = %s WHERE event_id = %s;',
                        (event_name, location, event_type, event_date, event_id))
               flash('Event updated successfully!', 'success')
               return redirect(url_for('event_detail', event_id=event_id))

     # unified template for edit mode
     return render_template('event.html', mode='edit', event=event, errors=errors)

@app.route('/staff/event/<int:event_id>/cancel', methods=['POST'])
def cancel_event(event_id):
     """Cancel an event."""
     if not check_leader_or_admin():
          return redirect(url_for('login'))
     elif session['role'] not in ('Event Leaders','Administrators'):
          return render_template('access_denied.html'), 403

     user_id = session['user_id']

     with db.get_cursor() as cursor:
          if session['role'] == 'Administrators':
               cursor.execute('SELECT * FROM events WHERE event_id = %s;', (event_id,))
          else:
               cursor.execute(
                   'SELECT * FROM events WHERE event_id = %s AND event_leader_id = %s;',
                   (event_id, user_id))
          if not cursor.fetchone():
               flash('Event not found or you do not have permission.', 'danger')
               return redirect(url_for('staff_home'))

          # Delete all registrations and feedbacks associated with the event
          cursor.execute('DELETE FROM feedback WHERE event_id = %s;', (event_id,))
          cursor.execute('DELETE FROM eventregistrations WHERE event_id = %s;', (event_id,))
          cursor.execute('DELETE FROM eventoutcomes WHERE event_id = %s;', (event_id,))
          cursor.execute('DELETE FROM events WHERE event_id = %s;', (event_id,))

     flash('Event cancelled and removed.', 'success')
     return redirect(url_for('staff_home'))

@app.route('/staff/event/<int:event_id>/volunteer/<int:volunteer_id>/remove', methods=['POST'])
def remove_volunteer(event_id, volunteer_id):
     """Remove a volunteer from an event."""
     if not check_leader_or_admin():
          return redirect(url_for('login'))
     elif session['role'] not in ('Event Leaders','Administrators'):
          return render_template('access_denied.html'), 403

     user_id = session['user_id']

     with db.get_cursor() as cursor:
          if session['role'] == 'Administrators':
               cursor.execute('SELECT * FROM events WHERE event_id = %s;', (event_id,))
          else:
               cursor.execute(
                   'SELECT * FROM events WHERE event_id = %s AND event_leader_id = %s;',
                   (event_id, user_id))
          if not cursor.fetchone():
               flash('Event not found or you do not have permission.', 'danger')
               return redirect(url_for('staff_home'))

          # Delete registration
          cursor.execute(
              'DELETE FROM eventregistrations WHERE event_id = %s AND volunteer_id = %s;',
              (event_id, volunteer_id))
          # Also delete any feedback from this volunteer for this event
          cursor.execute(
              'DELETE FROM feedback WHERE event_id = %s AND volunteer_id = %s;',
              (event_id, volunteer_id))

     flash('Volunteer removed from event.', 'success')
     return redirect(url_for('event_detail', event_id=event_id))

@app.route('/staff/event/<int:event_id>/attendance', methods=['GET', 'POST'])
def manage_attendance(event_id):
     """Track and update volunteer attendance."""
     if not check_leader_or_admin():
          return redirect(url_for('login'))
     elif session['role'] not in ('Event Leaders','Administrators'):
          return render_template('access_denied.html'), 403

     user_id = session['user_id']

     with db.get_cursor() as cursor:
          cursor.execute(
              'SELECT * FROM events WHERE event_id = %s AND event_leader_id = %s;',
              (event_id, user_id))
          event = cursor.fetchone()
          if not event:
               flash('Event not found or you do not have permission.', 'danger')
               return redirect(url_for('staff_home'))

          if request.method == 'POST':
               # Update attendance for each volunteer
               cursor.execute(
                   'SELECT volunteer_id FROM eventregistrations WHERE event_id = %s;',
                   (event_id,))
               volunteers = cursor.fetchall()
               for vol in volunteers:
                    vol_id = vol['volunteer_id']
                    attendance = request.form.get(f'attendance_{vol_id}')
                    if attendance:
                         cursor.execute(
                             'UPDATE eventregistrations SET attendance = %s '
                             'WHERE event_id = %s AND volunteer_id = %s;',
                             (attendance, event_id, vol_id))
               flash('Attendance updated successfully!', 'success')
               return redirect(url_for('event_detail', event_id=event_id))

          # Fetch volunteers with current attendance
          cursor.execute(
              '''
              SELECT t3.registration_id, t1.user_id AS volunteer_id, t1.username, t1.full_name,
                     t3.attendance
              FROM eventregistrations t3
              JOIN users t1 ON t3.volunteer_id = t1.user_id
              WHERE t3.event_id = %s
              ORDER BY t1.username;
              ''',
              (event_id,))
          volunteers = cursor.fetchall()

     return render_template('manage_attendance.html', event=event, volunteers=volunteers)

@app.route('/staff/event/<int:event_id>/outcome', methods=['GET', 'POST'])
def record_outcome(event_id):
     """Record event outcomes (attendees, bags, recyclables)."""
     if not check_leader_or_admin():
          return redirect(url_for('login'))
     elif session['role'] not in ('Event Leaders','Administrators'):
          return render_template('access_denied.html'), 403

     user_id = session['user_id']
     errors = {}

     with db.get_cursor() as cursor:
          cursor.execute(
              'SELECT * FROM events WHERE event_id = %s AND event_leader_id = %s;',
              (event_id, user_id))
          event = cursor.fetchone()
          if not event:
               flash('Event not found or you do not have permission.', 'danger')
               return redirect(url_for('staff_home'))

          cursor.execute('SELECT * FROM eventoutcomes WHERE event_id = %s;', (event_id,))
          outcome = cursor.fetchone()

     if request.method == 'POST':
          num_attendees = request.form.get('num_attendees', '').strip()
          bags_collected = request.form.get('bags_collected', '').strip()
          recyclables_sorted = request.form.get('recyclables_sorted', '').strip()
          other_achievements = request.form.get('other_achievements', '').strip()

          try:
               num_attendees = int(num_attendees) if num_attendees else None
               bags_collected = int(bags_collected) if bags_collected else None
               recyclables_sorted = int(recyclables_sorted) if recyclables_sorted else None
          except:
               errors['general'] = 'Numbers must be integers'

          if not errors:
               with db.get_cursor() as cursor:
                    if outcome:
                         cursor.execute(
                             'UPDATE eventoutcomes SET num_attendees = %s, '
                             'bags_collected = %s, recyclables_sorted = %s, '
                             'other_achievements = %s, recorded_at = NOW() '
                             'WHERE event_id = %s;',
                             (num_attendees, bags_collected, recyclables_sorted,
                              other_achievements, event_id))
                    else:
                         cursor.execute(
                             'INSERT INTO eventoutcomes '
                             '(event_id, num_attendees, bags_collected, recyclables_sorted, '
                             'other_achievements, recorded_by, recorded_at) '
                             'VALUES (%s, %s, %s, %s, %s, %s, NOW());',
                             (event_id, num_attendees, bags_collected, recyclables_sorted,
                              other_achievements, user_id))
               flash('Event outcome recorded successfully!', 'success')
               return redirect(url_for('event_detail', event_id=event_id))

     return render_template('record_outcome.html', event=event, outcome=outcome, errors=errors)

@app.route('/staff/volunteer/<int:volunteer_id>/history')
def volunteer_history(volunteer_id):
     """View a volunteer's participation history."""
     if not check_leader_or_admin():
          return redirect(url_for('login'))
     elif session['role'] not in ('Event Leaders','Administrators'):
          return render_template('access_denied.html'), 403

     with db.get_cursor() as cursor:
          cursor.execute('SELECT * FROM users WHERE user_id = %s;', (volunteer_id,))
          volunteer = cursor.fetchone()
          if not volunteer:
               flash('Volunteer not found.', 'danger')
               return redirect(url_for('staff_home'))

          cursor.execute(
              '''
              SELECT t4.*, t3.attendance, t3.registered_at,
                     f.rating, f.comments
              FROM eventregistrations t3
              JOIN events t4 ON t3.event_id = t4.event_id
              LEFT JOIN feedback f ON f.event_id = t4.event_id AND f.volunteer_id = %s
              WHERE t3.volunteer_id = %s
              ORDER BY t4.event_date DESC;
              ''',
              (volunteer_id, volunteer_id))
          events = cursor.fetchall()

     return render_template('volunteer_history.html', volunteer=volunteer, events=events)

@app.route('/staff/event/<int:event_id>/send-reminder', methods=['POST'])
def send_reminder(event_id):
     """Send event reminder to registered volunteers."""
     if not check_leader_or_admin():
          return redirect(url_for('login'))
     elif session['role'] not in ('Event Leaders','Administrators'):
          return render_template('access_denied.html'), 403

     user_id = session['user_id']

     with db.get_cursor() as cursor:
          cursor.execute(
              'SELECT * FROM events WHERE event_id = %s AND event_leader_id = %s;',
              (event_id, user_id))
          event = cursor.fetchone()
          if not event:
               flash('Event not found or you do not have permission.', 'danger')
               return redirect(url_for('staff_home'))

          # Fetch registered volunteers
          cursor.execute(
              'SELECT t1.email FROM eventregistrations t3 '
              'JOIN users t1 ON t3.volunteer_id = t1.user_id '
              'WHERE t3.event_id = %s;',
              (event_id,))
          volunteers = cursor.fetchall()

     # In a real implementation, send emails here
     # For now, just flash a message
     if volunteers:
          flash(f'Reminder sent to {len(volunteers)} volunteer(s) for {event["event_name"]}.', 'success')
     else:
          flash('No registered volunteers to send reminder to.', 'info')

     return redirect(url_for('event_detail', event_id=event_id))

@app.route('/staff/event/<int:event_id>/feedbacks')
def view_feedbacks(event_id):
     """View all feedbacks for an event."""
     if not check_leader_or_admin():
          return redirect(url_for('login'))
     elif session['role'] not in ('Event Leaders','Administrators'):
          return render_template('access_denied.html'), 403

     user_id = session['user_id']

     with db.get_cursor() as cursor:
          cursor.execute(
              'SELECT * FROM events WHERE event_id = %s AND event_leader_id = %s;',
              (event_id, user_id))
          event = cursor.fetchone()
          if not event:
               flash('Event not found or you do not have permission.', 'danger')
               return redirect(url_for('staff_home'))

          cursor.execute(
              '''
              SELECT t2.*, t1.username, t1.full_name
              FROM feedback t2
              JOIN users t1 ON t2.volunteer_id = t1.user_id
              WHERE t2.event_id = %s
              ORDER BY t2.submitted_at DESC;
              ''',
              (event_id,))
          feedbacks = cursor.fetchall()

     return render_template('view_feedbacks.html', event=event, feedbacks=feedbacks)
