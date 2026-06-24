from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from app import db
from app.models import ContactMessage, Student

main = Blueprint('main', __name__)

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/health')
def health():
    """Diagnostic endpoint to check app and database status."""
    from app import db
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "OK"
    except Exception as e:
        db_status = f"ERROR: {str(e)}"
    return f"<h2>Estado del sistema</h2><p>App: OK</p><p>Base de datos: {db_status}</p>", 200


# ─────────────────────────────────────────────────────────────────────────────
# API CONTACTO
# ─────────────────────────────────────────────────────────────────────────────

@main.route('/api/contacto', methods=['POST'])
def api_contacto():
    try:
        data = request.get_json() or {}
        nombre = data.get('nombre', '').strip()
        email = data.get('email', '').strip()
        servicio = data.get('servicio', '').strip()
        whatsapp = data.get('whatsapp', '').strip()
        mensaje = data.get('mensaje', '').strip()

        if not nombre or not email or not servicio or not mensaje:
            return jsonify({'success': False, 'message': 'Por favor, rellena todos los campos requeridos.'}), 400

        msg = ContactMessage(
            name=nombre,
            email=email,
            service=servicio,
            whatsapp=whatsapp,
            message=mensaje
        )
        db.session.add(msg)
        db.session.commit()

        return jsonify({'success': True, 'message': '¡Tu consulta ha sido enviada con éxito! Te responderemos lo antes posible.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al procesar la solicitud: {str(e)}'}), 500


# ─────────────────────────────────────────────────────────────────────────────
# ÁREA DE ESTUDIANTES — Autenticación
# ─────────────────────────────────────────────────────────────────────────────

@main.route('/api/estudiante/login', methods=['POST'])
def api_estudiante_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'success': False, 'message': 'Introduce tu correo y contraseña.'}), 400

    student = Student.query.filter_by(email=email).first()

    if not student:
        return jsonify({'success': False, 'message': 'No se encontró una cuenta con ese correo.'}), 404

    if not student.check_password(password):
        return jsonify({'success': False, 'message': 'Contraseña incorrecta. Inténtalo de nuevo.'}), 401

    if not student.is_active:
        return jsonify({
            'success': False,
            'message': 'Tu cuenta está en proceso de validación. Contacta con secretaría académica por WhatsApp.'
        }), 403

    session['student_id'] = student.id
    session['student_name'] = student.name
    return jsonify({'success': True, 'redirect': url_for('main.student_panel')})


@main.route('/estudiante/panel')
def student_panel():
    if not session.get('student_id'):
        return redirect(url_for('main.index'))
    student = Student.query.get(session['student_id'])
    if not student or not student.is_active:
        session.pop('student_id', None)
        session.pop('student_name', None)
        return redirect(url_for('main.index'))
    return render_template('student_panel.html', student=student)


@main.route('/estudiante/logout')
def student_logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    return redirect(url_for('main.index'))


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN — Login / Logout
# ─────────────────────────────────────────────────────────────────────────────

@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('main.admin_mensajes'))

    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'elvis2026':
            session['admin_logged_in'] = True
            return redirect(url_for('main.admin_mensajes'))
        else:
            error = 'Contraseña incorrecta. Inténtalo de nuevo.'

    return render_template('admin_login.html', error=error)


@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('main.admin_login'))


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN — Mensajes de Contacto
# ─────────────────────────────────────────────────────────────────────────────

@main.route('/admin/mensajes')
def admin_mensajes():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.admin_login'))
    mensajes = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin_dashboard.html', mensajes=mensajes)


@main.route('/admin/mensajes/<int:id>/eliminar', methods=['POST'])
def admin_eliminar_mensaje(id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'No autorizado.'}), 403

    msg = ContactMessage.query.get_or_404(id)
    try:
        db.session.delete(msg)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Mensaje eliminado.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN — Gestión de Estudiantes
# ─────────────────────────────────────────────────────────────────────────────

@main.route('/admin/estudiantes')
def admin_estudiantes():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.admin_login'))
    estudiantes = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('admin_students.html', estudiantes=estudiantes)


@main.route('/admin/estudiantes/nuevo', methods=['POST'])
def admin_nuevo_estudiante():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'No autorizado.'}), 403

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    course = data.get('course', '').strip()

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Nombre, correo y contraseña son obligatorios.'}), 400

    if Student.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Ya existe un estudiante con ese correo.'}), 409

    try:
        student = Student(name=name, email=email, course=course)
        student.set_password(password)
        db.session.add(student)
        db.session.commit()
        return jsonify({'success': True, 'message': f'Estudiante {name} creado correctamente.', 'student': student.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@main.route('/admin/estudiantes/<int:id>/toggle', methods=['POST'])
def admin_toggle_estudiante(id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'No autorizado.'}), 403

    student = Student.query.get_or_404(id)
    try:
        student.is_active = not student.is_active
        db.session.commit()
        estado = 'activada' if student.is_active else 'desactivada'
        return jsonify({'success': True, 'message': f'Cuenta {estado}.', 'is_active': student.is_active})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@main.route('/admin/estudiantes/<int:id>/eliminar', methods=['POST'])
def admin_eliminar_estudiante(id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'No autorizado.'}), 403

    student = Student.query.get_or_404(id)
    try:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Estudiante eliminado.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
