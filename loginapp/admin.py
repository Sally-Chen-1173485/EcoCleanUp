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
)


def check_admin():
    """Return True if the current session belongs to an administrator."""
    if 'loggedin' not in session:
        return False
    return session.get('role') == 'Administrators'


@app.route('/admin/home')
def admin_home():
    """Admin Homepage endpoint with embedded users and reports."""
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403

    # prepare user listing
    q = request.args.get('q', '').strip()
    with db.get_cursor() as cursor:
        if q:
            pattern = f"%{q}%"
            cursor.execute(
                "SELECT * FROM users WHERE username ILIKE %s OR full_name ILIKE %s OR email ILIKE %s OR role ILIKE %s ORDER BY username;",
                (pattern, pattern, pattern, pattern)
            )
        else:
            cursor.execute('SELECT * FROM users ORDER BY username;')
        users = cursor.fetchall()

        # gather report statistics
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

    return render_template('admin_home.html', users=users, q=q,
                           total_events=total_events,
                           total_volunteers=total_volunteers,
                           total_leaders=total_leaders,
                           total_feedbacks=total_feedbacks,
                           avg_rating=avg_rating,
                           attendance_counts=attendance_counts,
                           engagement=engagement)


@app.route('/admin/events')
def admin_events():
    """List all cleanup events. Reuses the event leader template."""
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403

    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    location = request.args.get('location', '')
    evtype = request.args.get('event_type', '')

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
        date_to=date_to,
        location=location,
        event_type=evtype,
        past_scope='all'
    )


@app.route('/admin/event/<int:event_id>')
def admin_event_detail(event_id):
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403
    return leader_event_detail(event_id)


@app.route('/admin/event/<int:event_id>/edit', methods=['GET', 'POST'])
def admin_edit_event(event_id):
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403
    return leader_edit_event(event_id)


@app.route('/admin/event/<int:event_id>/cancel', methods=['POST'])
def admin_cancel_event(event_id):
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403
    return leader_cancel_event(event_id)


@app.route('/admin/event/<int:event_id>/attendance', methods=['GET', 'POST'])
def admin_manage_attendance(event_id):
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403
    return leader_manage_attendance(event_id)


@app.route('/admin/event/<int:event_id>/outcome', methods=['GET', 'POST'])
def admin_record_outcome(event_id):
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403
    return leader_record_outcome(event_id)


@app.route('/admin/volunteer/<int:volunteer_id>/history')
def admin_volunteer_history(volunteer_id):
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403
    return leader_volunteer_history(volunteer_id)


@app.route('/admin/event/<int:event_id>/send-reminder', methods=['POST'])
def admin_send_reminder(event_id):
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403
    return leader_send_reminder(event_id)


@app.route('/admin/event/<int:event_id>/feedbacks')
def admin_view_feedbacks(event_id):
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403
    return leader_view_feedbacks(event_id)


@app.route('/admin/users')
def admin_users():
    """Display a paginated/filterable list of all users."""
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403

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

        if q:
            pattern = f"%{q}%"
            query += (
                ' AND ('
                'username ILIKE %s OR COALESCE(full_name, \'\') ILIKE %s OR email ILIKE %s '
                'OR role::text ILIKE %s OR status::text ILIKE %s'
                ')'
            )
            params.extend([pattern, pattern, pattern, pattern, pattern])

        if role_filter:
            query += ' AND role = %s'
            params.append(role_filter)

        if status_filter:
            query += ' AND status = %s'
            params.append(status_filter)

        query += ' ORDER BY username;'
        cursor.execute(query, tuple(params))
        users = cursor.fetchall()
    return render_template(
        'admin_users.html',
        users=users,
        q=q,
        role_filter=role_filter,
        status_filter=status_filter
    )


@app.route('/admin/users/<int:user_id>/status', methods=['POST'])
def admin_update_status(user_id):
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403

    status = request.form.get('status')
    if status in ('active', 'inactive'):
        with db.get_cursor() as cursor:
            cursor.execute('UPDATE users SET status = %s WHERE user_id = %s;', (status, user_id))
        flash('User status updated.', 'success')
    else:
        flash('Invalid status value.', 'danger')
    return redirect(url_for('admin_users'))


@app.route('/admin/reports')
def admin_reports():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session.get('role') not in ('Event Leaders', 'Administrators'):
        return render_template('access_denied.html'), 403

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

            cursor.execute(
                '''
                SELECT e.event_id,
                       e.event_name,
                       e.event_date,
                       e.location_,
                       e.event_type,
                       COALESCE(u.full_name, u.username, 'Event Leader') AS leader_name,
                       COALESCE(reg.reg_count, 0) AS registered_count,
                       COALESCE(out.num_attendees, 0) AS num_attendees
                FROM events e
                LEFT JOIN users u ON e.event_leader_id = u.user_id
                LEFT JOIN (
                    SELECT event_id, COUNT(*) AS reg_count
                    FROM eventregistrations
                    GROUP BY event_id
                ) reg ON reg.event_id = e.event_id
                LEFT JOIN eventoutcomes out ON out.event_id = e.event_id
                ORDER BY e.event_date DESC, e.event_id DESC;
                '''
            )
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

        cursor.execute(
            '''
            SELECT e.event_id,
                   e.event_name,
                   e.event_date,
                   e.location_,
                   COALESCE(out.num_attendees, 0) AS num_attendees,
                   COALESCE(reg.reg_count, 0) AS registered_count,
                   COALESCE(fb.feedback_count, 0) AS feedback_count,
                   COALESCE(fb.avg_rating, 0) AS avg_rating
            FROM events e
            LEFT JOIN eventoutcomes out ON out.event_id = e.event_id
            LEFT JOIN (
                SELECT event_id, COUNT(*) AS reg_count
                FROM eventregistrations
                GROUP BY event_id
            ) reg ON reg.event_id = e.event_id
            LEFT JOIN (
                SELECT event_id, COUNT(*) AS feedback_count, AVG(rating) AS avg_rating
                FROM feedback
                GROUP BY event_id
            ) fb ON fb.event_id = e.event_id
            WHERE e.event_leader_id = %s
            ORDER BY e.event_date DESC;
            ''',
            (user_id,)
        )
        leader_event_reports = cursor.fetchall()

    return render_template(
        'admin_reports.html',
        is_admin=False,
        leader_event_reports=leader_event_reports
    )


