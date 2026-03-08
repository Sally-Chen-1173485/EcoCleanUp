from loginapp import app
from loginapp import db
from flask import redirect, render_template, session, url_for, request, flash
from datetime import date, datetime
from flask_bcrypt import Bcrypt

flask_bcrypt = Bcrypt(app)

# Role guard helpers reused across staff routes.
def _ensure_logged_in_with_roles(*allowed_roles):
     """Return redirect/403 response when session role is not allowed, else None."""
     if 'loggedin' not in session:
          return redirect(url_for('login'))
     if session.get('role') not in allowed_roles:
          return render_template('access_denied.html'), 403
     return None

#shared guard for both event leaders and admins since they have overlapping access to some routes
def _ensure_leader_or_admin_logged_in():
     """Guard route access for Event Leaders and Administrators."""
     return _ensure_logged_in_with_roles('Event Leaders', 'Administrators')

#guard for routes that only event leaders (not admins) should access, 
#such as event creation and volunteer management for their events.
def _ensure_event_leader_logged_in():
     """Guard route access for Event Leaders only."""
     return _ensure_logged_in_with_roles('Event Leaders')


def build_upcoming_events_query(date_from='', date_to='', location='', event_type=''):
     """Build SQL and params for upcoming events with optional filters."""
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
     if event_type:
          query += ' AND event_type ILIKE %s'
          params.append(event_type)

     query += ' ORDER BY event_date ASC'
     return query, tuple(params)

# Helper functions for staff/admin routes to read and validate event form data, reduce code duplication.
def _read_event_form_fields():
     """Read and normalize event form fields from request.form."""
     return {
          'event_name': request.form.get('event_name', '').strip(),
          'location': request.form.get('location', '').strip(),
          'event_type': request.form.get('event_type', '').strip(),
          'event_date': request.form.get('event_date', '').strip(),
          'start_time': request.form.get('start_time', '').strip(),
          'end_time': request.form.get('end_time', '').strip(),
          'duration': request.form.get('duration', '').strip(),
          'description': request.form.get('description', '').strip(),
          'supplies': request.form.get('supplies', '').strip(),
          'safety_instructions': request.form.get('safety_instructions', '').strip(),
     }

#helper function to validate event form data and return any errors along with parsed values for time and duration fields.
def _validate_event_form_fields(form_data, enforce_future_date=False):
     """Validate create/edit event form and return (errors, parsed_values)."""
     errors = {}
     start_time_value = None
     end_time_value = None
     duration_value = None

     if not form_data['event_name'] or len(form_data['event_name']) > 100:
          errors['event_name'] = 'Event name required (max 100 chars)'
     if not form_data['location'] or len(form_data['location']) > 255:
          errors['location'] = 'Location required (max 255 chars)'
     if not form_data['event_type'] or len(form_data['event_type']) > 50:
          errors['event_type'] = 'Event type required (max 50 chars)'

     if not form_data['event_date']:
          errors['event_date'] = 'Event date required'
     else:
          try:
               ed = date.fromisoformat(form_data['event_date'])
               if enforce_future_date and ed < date.today():
                    errors['event_date'] = 'Event date cannot be in the past'
          except:
               errors['event_date'] = 'Invalid date format'

     if form_data['start_time']:
          try:
               start_time_value = datetime.strptime(form_data['start_time'], '%H:%M').time()
          except:
               errors['start_time'] = 'Invalid start time format'

     if form_data['end_time']:
          try:
               end_time_value = datetime.strptime(form_data['end_time'], '%H:%M').time()
          except:
               errors['end_time'] = 'Invalid end time format'

     if start_time_value and end_time_value and start_time_value >= end_time_value:
          errors['end_time'] = 'End time must be after start time'

     if form_data['duration']:
          try:
               duration_value = int(form_data['duration'])
               if duration_value <= 0:
                    errors['duration'] = 'Duration must be a positive integer'
          except:
               errors['duration'] = 'Duration must be an integer'

     if len(form_data['description']) > 5000:
          errors['description'] = 'Description cannot exceed 5000 characters'
     if len(form_data['supplies']) > 5000:
          errors['supplies'] = 'Supplies cannot exceed 5000 characters'
     if len(form_data['safety_instructions']) > 5000:
          errors['safety_instructions'] = 'Safety instructions cannot exceed 5000 characters'

     return errors, {
          'start_time_value': start_time_value,
          'end_time_value': end_time_value,
          'duration_value': duration_value,}




# Event Leader homepage, showing their events and details about these events.

@app.route('/staff/home')
def staff_home():
     """Event Leader Homepage - lists their events.

     Methods:
     - get: Renders the homepage listing the logged-in event leader's events.

     If the user is not logged in or not an event leader (or admin), redirects or shows access denied.
     """
     guard_response = _ensure_leader_or_admin_logged_in()
     if guard_response is not None:
          return guard_response

     date_from = request.args.get('date_from', '')
     date_to = request.args.get('date_to', '')
     location = request.args.get('location', '')
     evtype = request.args.get('event_type', '')
     past_scope = request.args.get('past_scope', 'all')

     if session.get('role') == 'Event Leaders':
          if past_scope not in ('all', 'mine'):
               past_scope = 'all'
     else:
          past_scope = 'all'
     
     query, params = build_upcoming_events_query(
          date_from=date_from,
          date_to=date_to,
          location=location,
          event_type=evtype)

     with db.get_cursor() as cursor:
          cursor.execute(query, params)
          upcoming_events = cursor.fetchall()

          past_query = '''
               SELECT *
               FROM events
               WHERE event_date < %s
          '''
          past_params = [date.today()]

          # Event leaders can switch between all past events and their own managed past events.
          if session.get('role') == 'Event Leaders' and past_scope == 'mine':
               past_query += ' AND event_leader_id = %s'
               past_params.append(session['user_id'])

          past_query += ' ORDER BY event_date DESC;'
          cursor.execute(past_query, tuple(past_params))
          past_events = cursor.fetchall()
     
     return render_template(
          'customer_home.html',
          upcoming_events=upcoming_events,
          registered_ids=set(),
          past_events=past_events,
          reminder_events=[],
          date_from=date_from,
          date_to=date_to,
          location=location,
          event_type=evtype,
          past_scope=past_scope)


# Handles the report page for event leaders, 
# which shows all events led by the logged-in leader, 
# along with key metrics for each event.
@app.route('/staff/reports')
def staff_reports():
     """Event leader report page (leader-specific events only)."""
     guard_response = _ensure_leader_or_admin_logged_in()
     if guard_response is not None:
          return guard_response

     if session.get('role') == 'Administrators':
          return redirect(url_for('admin_reports'))

     user_id = session.get('user_id')
     with db.get_cursor() as cursor:
          cursor.execute(
              '''
              SELECT t4.event_id,
                     t4.event_name,
                     t4.event_date,
                     t4.location_,
                     COALESCE(t5.num_attendees, 0) AS num_attendees,
                     COALESCE(t3.reg_count, 0) AS registered_count,
                     COALESCE(t2.feedback_count, 0) AS feedback_count,
                     COALESCE(t2.avg_rating, 0) AS avg_rating
              FROM events t4
              LEFT JOIN eventoutcomes t5 ON t5.event_id = t4.event_id
              LEFT JOIN (
                  SELECT event_id, COUNT(*) AS reg_count
                  FROM eventregistrations
                  GROUP BY event_id) t3 ON t3.event_id = t4.event_id
              LEFT JOIN (
                  SELECT event_id, COUNT(*) AS feedback_count, AVG(rating) AS avg_rating
                  FROM feedback
                  GROUP BY event_id) t2 ON t2.event_id = t4.event_id
              WHERE t4.event_leader_id = %s
              ORDER BY t4.event_date DESC;
              ''',
              (user_id,))
          leader_event_reports = cursor.fetchall()

     return render_template(
          'admin_reports.html',
          is_admin=False,
          leader_event_reports=leader_event_reports)

#Handles the event creation page for event leaders, 
#allowing them to create new events and specify details about these events.
@app.route('/staff/event/create', methods=['GET', 'POST'])
def create_event():
     """Create a new cleanup event."""
     guard_response = _ensure_event_leader_logged_in()
     if guard_response is not None:
          return guard_response

     user_id = session['user_id']
     errors = {}

     if request.method == 'POST':
          form_data = _read_event_form_fields()
          errors, parsed = _validate_event_form_fields(form_data, enforce_future_date=True)

          if not errors:
               with db.get_cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO events '
                        '(event_name, event_leader_id, location_, event_type, event_date, '
                        'start_time, end_time, duration, description_, supplies, safety_instructions) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);',
                        (    form_data['event_name'], user_id, form_data['location'],
                             form_data['event_type'], form_data['event_date'],
                             parsed['start_time_value'], parsed['end_time_value'], parsed['duration_value'],
                             form_data['description'] or None, form_data['supplies'] or None,
                             form_data['safety_instructions'] or None))
                    
               flash('Event created successfully!', 'success')
               return redirect(url_for('staff_home'))

     # use unified template
     return render_template('event.html', mode='create', errors=errors,
                            today_iso=date.today().isoformat())


#Handles the event detail page for event leaders, 
# showing details about a specific event they lead.
@app.route('/staff/event/<int:event_id>')
def event_detail(event_id):
     """View event details with registered volunteers."""
     guard_response = _ensure_leader_or_admin_logged_in()
     if guard_response is not None:
          return guard_response

     user_id = session['user_id']
     is_admin = session['role'] == 'Administrators'

     with db.get_cursor() as cursor:
          cursor.execute('''
              SELECT t4.*, t1.full_name AS leader_name, t1.username AS leader_username
              FROM events t4
              LEFT JOIN users t1 ON t4.event_leader_id = t1.user_id
              WHERE t4.event_id = %s;
          ''', (event_id,))
          event = cursor.fetchone()
          if not event:
               flash('Event not found.', 'danger')
               return redirect(url_for('staff_home'))

          # Fetch registered volunteers
          cursor.execute(
              '''
               SELECT t3.registration_id, t1.user_id AS volunteer_id, t1.username, t1.full_name, t1.email,
                    t1.contact_number,
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

     can_manage_event = is_admin or (event['event_leader_id'] == user_id)


    #Determine URLs for event management actions based on user role

     if is_admin:
          manage_attendance_url = url_for('admin_manage_attendance', event_id=event_id)
          record_outcome_url = url_for('admin_record_outcome', event_id=event_id)
          send_reminder_url = url_for('admin_send_reminder', event_id=event_id)
          view_feedbacks_url = url_for('admin_view_feedbacks', event_id=event_id)
          edit_event_url = url_for('admin_edit_event', event_id=event_id)
          cancel_event_url = url_for('admin_cancel_event', event_id=event_id)
          back_url = url_for('admin_events')
     else:
          manage_attendance_url = url_for('manage_attendance', event_id=event_id)
          record_outcome_url = url_for('record_outcome', event_id=event_id)
          send_reminder_url = url_for('send_reminder', event_id=event_id)
          view_feedbacks_url = url_for('view_feedbacks', event_id=event_id)
          edit_event_url = url_for('edit_event', event_id=event_id)
          cancel_event_url = url_for('cancel_event', event_id=event_id)
          back_url = url_for('staff_home')

     return render_template(
          'event_detail.html',
          event=event,
          volunteers=volunteers,
          outcome=outcome,
          feedbacks=feedbacks,
          can_manage_event=can_manage_event,
          is_admin=is_admin,
          is_registered=False,
          manage_attendance_url=manage_attendance_url,
          record_outcome_url=record_outcome_url,
          send_reminder_url=send_reminder_url,
          view_feedbacks_url=view_feedbacks_url,
          edit_event_url=edit_event_url,
          cancel_event_url=cancel_event_url,
          back_url=back_url,
          back_label='Back to Events',
          now=datetime.now())



#handles the event editing page for event leaders, 
# allowing them to edit details about an event they lead.
@app.route('/staff/event/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
     """Edit an existing event."""
     guard_response = _ensure_leader_or_admin_logged_in()
     if guard_response is not None:
          return guard_response

     user_id = session['user_id']
     errors = {}

     with db.get_cursor() as cursor:
          #administrators can edit any event, but event leaders can only edit their own events
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
          form_data = _read_event_form_fields()
          errors, parsed = _validate_event_form_fields(form_data)

          if not errors:
               with db.get_cursor() as cursor:
                    cursor.execute(
                        'UPDATE events SET event_name = %s, location_ = %s, '
                        'event_type = %s, event_date = %s, start_time = %s, end_time = %s, '
                        'duration = %s, description_ = %s, supplies = %s, safety_instructions = %s '
                        'WHERE event_id = %s;',
                        (    form_data['event_name'], form_data['location'], form_data['event_type'],
                             form_data['event_date'], parsed['start_time_value'], parsed['end_time_value'],
                             parsed['duration_value'], form_data['description'] or None,
                             form_data['supplies'] or None, form_data['safety_instructions'] or None,
                             event_id))
               flash('Event updated successfully!', 'success')
               return redirect(url_for('event_detail', event_id=event_id))

     # unified template for edit mode
     return render_template('event.html', mode='edit', event=event, errors=errors,
                            today_iso=date.today().isoformat())




# Handles the event cancellation route for event leaders, 
# allowing them to cancel an event they lead, 
# which deletes the event and all associated registrations and feedback.
@app.route('/staff/event/<int:event_id>/cancel', methods=['POST'])
def cancel_event(event_id):
     """Cancel an event."""
     guard_response = _ensure_leader_or_admin_logged_in()
     if guard_response is not None:
          return guard_response

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


#handles remove volunteer from event route for event leaders, 
# allowing them to remove a volunteer from an event they lead, 
# which deletes the volunteer's registration and any associated feedback for that event.
@app.route('/staff/event/<int:event_id>/volunteer/<int:volunteer_id>/remove', methods=['POST'])
def remove_volunteer(event_id, volunteer_id):
     """Remove a volunteer from an event."""
     guard_response = _ensure_event_leader_logged_in()
     if guard_response is not None:
          return guard_response

     user_id = session['user_id']

     with db.get_cursor() as cursor:
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



#Handles the attendance management page for event leaders, 
# allowing them to track and update volunteer attendance for an event they lead.
@app.route('/staff/event/<int:event_id>/attendance', methods=['GET', 'POST'])
def manage_attendance(event_id):
     
     guard_response = _ensure_event_leader_logged_in()
     if guard_response is not None:
          return guard_response

     user_id = session['user_id']

     valid_attendance_statuses = ('Present', 'Absent', 'Late', 'Excused', 'Pending')

     with db.get_cursor() as cursor:
          
          cursor.execute(
                   'SELECT * FROM events WHERE event_id = %s AND event_leader_id = %s;',
                   (event_id, user_id))
          event = cursor.fetchone()

          if not event:
               flash('Event not found or you do not have permission.', 'danger')
               return redirect(url_for('staff_home'))
          
          #find all volunteers registered for this event 
          #update attendance if this is a POST request with attendance updates
          if request.method == 'POST':
               cursor.execute(
                   'SELECT registration_id FROM eventregistrations WHERE event_id = %s;',
                   (event_id,))
               volunteers = cursor.fetchall()

               for vol in volunteers:
                    registration_id = vol['registration_id']
                    attendance = request.form.get(f'attendance_{registration_id}')
                    if attendance and attendance in valid_attendance_statuses:
                         cursor.execute(
                             'UPDATE eventregistrations SET attendance = %s '
                             'WHERE event_id = %s AND registration_id = %s;',
                             (attendance, event_id, registration_id))
               flash('Attendance updated successfully!', 'success')
               return redirect(url_for('manage_attendance', event_id=event_id))

          # Fetch volunteers with current attendance
          cursor.execute(
              '''
              SELECT t3.registration_id, t1.user_id AS volunteer_id, t1.username, t1.full_name,
                     t1.email, t3.attendance
              FROM eventregistrations t3
              JOIN users t1 ON t3.volunteer_id = t1.user_id
              WHERE t3.event_id = %s
              ORDER BY t1.username;
              ''',
              (event_id,))
          volunteers = cursor.fetchall()

     return render_template('manage_attendance.html', event=event, volunteers=volunteers,
                            attendance_statuses=valid_attendance_statuses)



#Handles the event outcome recording page for event leaders, 
# allowing them to record outcomes for an event they lead,
@app.route('/staff/event/<int:event_id>/outcome', methods=['GET', 'POST'])
def record_outcome(event_id):
     """Record event outcomes (attendees, bags, recyclables)."""
     guard_response = _ensure_event_leader_logged_in()
     if guard_response is not None:
          return guard_response

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
                         # By AI. Something to do with the sequence to avoid conflict if outcome_id is ever used as a reference in the future
                         cursor.execute(
                             "SELECT setval(pg_get_serial_sequence('eventoutcomes', 'outcome_id'), "
                             "COALESCE((SELECT MAX(outcome_id) FROM eventoutcomes), 0) + 1, FALSE);")
                         # Then insert the new outcome record
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



#Handles the volunteer history page for event leaders, 
# allowing viewing a volunteer's participation history across all events,
@app.route('/staff/volunteer/<int:volunteer_id>/history')
def volunteer_history(volunteer_id):
     """View a volunteer's participation history."""
     guard_response = _ensure_event_leader_logged_in()
     if guard_response is not None:
          return guard_response

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


#Handles the event reminder sending route for event leaders, 
# allowing them to send reminders to volunteers registered for an upcoming event.
@app.route('/staff/event/<int:event_id>/send-reminder', methods=['POST'])
def send_reminder(event_id):
     """Send event reminder to registered volunteers."""
     guard_response = _ensure_event_leader_logged_in()
     if guard_response is not None:
          return guard_response

     user_id = session['user_id']
     volunteers = []

     with db.get_cursor() as cursor:
          cursor.execute(
               'SELECT * FROM events WHERE event_id = %s AND event_leader_id = %s;',
               (event_id, user_id)
          )
          event = cursor.fetchone()
          if not event:
               flash('Event not found or you do not have permission.', 'danger')
               return redirect(url_for('staff_home'))

          # Fetch registered volunteers
          cursor.execute(
              'SELECT t1.user_id, t1.email FROM eventregistrations t3 '
              'JOIN users t1 ON t3.volunteer_id = t1.user_id '
              'WHERE t3.event_id = %s;',
              (event_id,))
          volunteers = cursor.fetchall()

          if volunteers:
               reminder_message = f"Reminder: {event['event_name']} is coming up on {event['event_date'].strftime('%Y-%m-%d')}."
               cursor.execute(
                    '''
                    UPDATE eventregistrations
                    SET reminder_pending = TRUE,
                        reminder_sent_at = NOW(),
                        reminder_message = %s
                    WHERE event_id = %s;
                    ''',
                    (reminder_message, event_id)
               )

     if volunteers:
          flash(f'Reminder sent to {len(volunteers)} volunteer(s) for {event["event_name"]}.', 'success')
     else:
          flash('No registered volunteers to send reminder to.', 'info')

     return redirect(url_for('event_detail', event_id=event_id))




#handles feedback viewing page for event leaders,
@app.route('/staff/event/<int:event_id>/feedbacks')
def view_feedbacks(event_id):
     """View all feedbacks for an event."""
     guard_response = _ensure_event_leader_logged_in()
     if guard_response is not None:
          return guard_response

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
