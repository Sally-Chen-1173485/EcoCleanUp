from loginapp import app
from loginapp import db
from flask import redirect, render_template, session, url_for, request, flash

# reuse staff views for event management
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

    with db.get_cursor() as cursor:
        cursor.execute('SELECT * FROM events ORDER BY event_date ASC;')
        events = cursor.fetchall()
    return render_template('staff_home.html', events=events)


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
    return render_template('admin_users.html', users=users, q=q)


@app.route('/admin/users/<int:user_id>/status', methods=['POST'])
def admin_update_status(user_id):
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403

    status = request.form.get('status')
    if status in ('active', 'nonactive', 'banned', 'suspended'):
        with db.get_cursor() as cursor:
            cursor.execute('UPDATE users SET status = %s WHERE user_id = %s;', (status, user_id))
        flash('User status updated.', 'success')
    else:
        flash('Invalid status value.', 'danger')
    return redirect(url_for('admin_users'))


@app.route('/admin/reports')
def admin_reports():
    if not check_admin():
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return render_template('access_denied.html'), 403

    with db.get_cursor() as cursor:
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
    return render_template('admin_reports.html', total_events=total_events,
                           total_volunteers=total_volunteers,
                           total_leaders=total_leaders,
                           total_feedbacks=total_feedbacks,
                           avg_rating=avg_rating,
                           attendance_counts=attendance_counts,
                           engagement=engagement)


