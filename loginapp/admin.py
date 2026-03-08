from loginapp import app
from loginapp import db
from flask import redirect, render_template, session, url_for, request, flash
from datetime import date

# reuse Event Leader's views for event management
from loginapp.staff import (
    staff_home as leader_home,
    event_detail as leader_event_detail,
    edit_event as leader_edit_event,
    cancel_event as leader_cancel_event,
    manage_attendance as leader_manage_attendance,
    record_outcome as leader_record_outcome,
    volunteer_history as leader_volunteer_history,
    send_reminder as leader_send_reminder,
    view_feedbacks as leader_view_feedbacks,
    build_upcoming_events_query,
    _ensure_logged_in_with_roles,_ensure_leader_or_admin_logged_in)

#helper function to guard admin-only routes
def _ensure_admin_logged_in():
    """Guard route access for Administrators only."""
    return _ensure_logged_in_with_roles('Administrators')


# Admin homepage 
@app.route('/admin/home')
def admin_home():
    """Admin overview page with navigation to dedicated admin tools."""
    guard_response = _ensure_admin_logged_in()
    if guard_response is not None:
        return guard_response

    return render_template('admin_home.html')

#admin views for events, reusing event leader templates where possible
@app.route('/admin/events')
def admin_events():
    """List all cleanup events. Reuses the event leader template."""
    guard_response = _ensure_admin_logged_in()
    if guard_response is not None:
        return guard_response

    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    location = request.args.get('location', '')
    evtype = request.args.get('event_type', '')

    query, params = build_upcoming_events_query(
        date_from=date_from,
        date_to=date_to,
        location=location,
        event_type=evtype)

    with db.get_cursor() as cursor:
        cursor.execute(query, params)
        upcoming_events = cursor.fetchall()

        cursor.execute(
            '''
            SELECT *
            FROM events
            WHERE event_date < %s
            ORDER BY event_date DESC;
            ''',
            (date.today(),)
        )
        past_events = cursor.fetchall()

    return render_template(
        'customer_home.html',
        upcoming_events=upcoming_events,
        registered_ids=set(),
        past_events=past_events,
        reminder_events=[],
        date_from=date_from,
        date_to=date_to)

#admin view for event details, reusing event leader template
@app.route('/admin/event/<int:event_id>')
def admin_event_detail(event_id):
    guard_response = _ensure_admin_logged_in()
    if guard_response is not None:
        return guard_response
    return leader_event_detail(event_id)

#admin views for event editing
@app.route('/admin/event/<int:event_id>/edit', methods=['GET', 'POST'])
def admin_edit_event(event_id):
    guard_response = _ensure_admin_logged_in()
    if guard_response is not None:
        return guard_response
    return leader_edit_event(event_id)

#admin view for event cancellation
@app.route('/admin/event/<int:event_id>/cancel', methods=['POST'])
def admin_cancel_event(event_id):
    guard_response = _ensure_admin_logged_in()
    if guard_response is not None:
        return guard_response
    return leader_cancel_event(event_id)

#admin view for managing event attendance(although it is block now)
@app.route('/admin/event/<int:event_id>/attendance', methods=['GET', 'POST'])
def admin_manage_attendance(event_id):
    guard_response = _ensure_admin_logged_in()
    if guard_response is not None:
        return guard_response
    return leader_manage_attendance(event_id)

#admin view for event outcome, it is blocked now but leave it here for future development 
def admin_record_outcome(event_id):
    guard_response = _ensure_admin_logged_in()
    if guard_response is not None:
        return guard_response
    return leader_record_outcome(event_id)

#admin view for volunteer history, reusing event leader template
@app.route('/admin/volunteer/<int:volunteer_id>/history')
def admin_volunteer_history(volunteer_id):
    guard_response = _ensure_admin_logged_in()
    if guard_response is not None:
        return guard_response
    return leader_volunteer_history(volunteer_id)

#admin view for sending reminders, reusing event leader template although it is not allowed for now.
@app.route('/admin/event/<int:event_id>/send-reminder', methods=['POST'])
def admin_send_reminder(event_id):
    guard_response = _ensure_admin_logged_in()
    if guard_response is not None:
        return guard_response
    return render_template('access_denied.html'), 403

#admin view for viewing feedbacks, not allowed for now but leave it here for future development
@app.route('/admin/event/<int:event_id>/feedbacks')
def admin_view_feedbacks(event_id):
    guard_response = _ensure_admin_logged_in()
    if guard_response is not None:
        return guard_response
    return leader_view_feedbacks(event_id)

#for admin manageing users
@app.route('/admin/users')
def admin_users():
    """Display a paginated/filterable list of all users."""
    guard_response = _ensure_admin_logged_in()
    if guard_response is not None:
        return guard_response

    q = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '').strip()
    status_filter = request.args.get('status', '').strip()

    valid_roles = ('Volunteers', 'Event Leaders', 'Administrators')
    valid_statuses = ('active', 'inactive')

    if role_filter not in valid_roles:
        role_filter = ''
    if status_filter not in valid_statuses:
        status_filter = ''

    with db.get_cursor() as cursor:
        query = 'SELECT * FROM users WHERE 1=1'
        params = []
    #allow search for username, full name, email, role and status,
    #and may only match for part of the field value
        if q:
            pattern = f"%{q}%"
            query += (
                ' AND ('
                'username ILIKE %s OR COALESCE(full_name, \'\') ILIKE %s OR email ILIKE %s '
                'OR role::text ILIKE %s OR status::text ILIKE %s'
                ')')
            params.extend([pattern, pattern, pattern, pattern, pattern])

        if role_filter:
            query += ' AND role = %s'
            params.append(role_filter)

        if status_filter:
            query += ' AND status = %s'
            params.append(status_filter)

        query += ' ORDER BY role DESC, username;'
        cursor.execute(query, tuple(params))
        users = cursor.fetchall()
    return render_template(
        'admin_users.html',
        users=users,
        q=q,
        role_filter=role_filter,
        status_filter=status_filter
    )

#admin to updating user status (active/inactive)
@app.route('/admin/users/<int:user_id>/status', methods=['POST'])
def admin_update_status(user_id):
    guard_response = _ensure_admin_logged_in()
    if guard_response is not None:
        return guard_response

    status = request.form.get('status')
    if status in ('active', 'inactive'):
        with db.get_cursor() as cursor:
            cursor.execute('UPDATE users SET status = %s WHERE user_id = %s;', (status, user_id))
        flash('User status updated.', 'success')
    else:
        flash('Invalid status value.', 'danger')
    return redirect(url_for('admin_users'))

#admin report view, showing different data for admin and event leaders
@app.route('/admin/reports')
def admin_reports():
    guard_response = _ensure_leader_or_admin_logged_in()
    if guard_response is not None:
        return guard_response

    is_admin = session.get('role') == 'Administrators'
    user_id = session.get('user_id')

    with db.get_cursor() as cursor:
        if is_admin:
            cursor.execute('SELECT COUNT(*) FROM events;')
            total_events = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) FROM users WHERE role='Volunteers';")
            total_volunteers = cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) FROM users WHERE role='Event Leaders';")
            total_leaders = cursor.fetchone()['count']
            cursor.execute('SELECT COUNT(*) FROM feedback;')
            total_feedbacks = cursor.fetchone()['count']
            cursor.execute('SELECT AVG(rating) FROM feedback;')
            avg_rating = cursor.fetchone()['avg'] or 0
            cursor.execute('SELECT attendance, COUNT(*) AS cnt FROM eventregistrations GROUP BY attendance;')
            attendance_counts = cursor.fetchall()
            cursor.execute(
                'SELECT t1.user_id, t1.full_name, COUNT(*) AS reg_count '
                'FROM eventregistrations t3 '
                'JOIN users t1 ON t3.volunteer_id = t1.user_id '
                'GROUP BY t1.user_id, t1.full_name '
                'ORDER BY reg_count DESC;'
            )
            engagement = cursor.fetchall()

# Admins see reports for all events
            cursor.execute(
                '''
                SELECT t4.event_id,
                       t4.event_name,
                       t4.event_date,
                       t4.location_,
                       t4.event_type,
                       COALESCE(t1.full_name, t1.username, 'Event Leader') AS leader_name,
                       COALESCE(t3.reg_count, 0) AS registered_count,
                       COALESCE(t5.num_attendees, 0) AS num_attendees
                FROM events t4
                LEFT JOIN users t1 ON t4.event_leader_id = t1.user_id
                LEFT JOIN (
                    SELECT event_id, COUNT(*) AS reg_count
                    FROM eventregistrations
                    GROUP BY event_id
                ) t3 ON t3.event_id = t4.event_id
                LEFT JOIN eventoutcomes t5 ON t5.event_id = t4.event_id
                ORDER BY t4.event_date DESC, t4.event_id DESC;
                ''')
            all_event_reports = cursor.fetchall()

            return render_template(
                'admin_reports.html',
                is_admin=True,
                total_events=total_events,
                total_volunteers=total_volunteers,
                total_leaders=total_leaders,
                total_feedbacks=total_feedbacks,
                avg_rating=avg_rating,
                attendance_counts=attendance_counts,
                engagement=engagement,
                all_event_reports=all_event_reports,
                leader_event_reports=[]
            )
 # Event leaders only see reports for their own events
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
                GROUP BY event_id
            ) t3 ON t3.event_id = t4.event_id
            LEFT JOIN (
                SELECT event_id, COUNT(*) AS feedback_count, AVG(rating) AS avg_rating
                FROM feedback
                GROUP BY event_id
            ) t2 ON t2.event_id = t4.event_id
            WHERE t4.event_leader_id = %s
            ORDER BY t4.event_date DESC;
            ''',
            (user_id,)
        )
        leader_event_reports = cursor.fetchall()

    return render_template(
        'admin_reports.html',
        is_admin=False,
        leader_event_reports=leader_event_reports)


