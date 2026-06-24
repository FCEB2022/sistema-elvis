import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Path to write local logs of sent emails
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'emails_sent.log')

def log_email_locally(to_email, subject, body_html):
    """Fallback function to log emails to a file when SMTP is not configured."""
    try:
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = (
            f"========================================================================\n"
            f"TIMESTAMP: {timestamp}\n"
            f"TO: {to_email}\n"
            f"SUBJECT: {subject}\n"
            f"------------------------------------------------------------------------\n"
            f"{body_html}\n"
            f"========================================================================\n\n"
        )
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Also print to standard output/logs
        print(f"[MAIL LOG] Email registered to local file: {to_email} - Subject: {subject}")
    except Exception as e:
        print(f"[MAIL LOG ERROR] Could not write email to local file: {e}")

def send_email(to_email, subject, body_html):
    """Sends email via SMTP if configured, or falls back to writing to a local file."""
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = os.environ.get('SMTP_PORT')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    smtp_from = os.environ.get('SMTP_FROM', 'no-reply@aslyonva.soluciones.com')

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        # Fallback to local file logging
        log_email_locally(to_email, subject, body_html)
        return True

    try:
        port = int(smtp_port)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_from
        msg['To'] = to_email

        part = MIMEText(body_html, 'html', 'utf-8')
        msg.attach(part)

        # Connect to SMTP server
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_host, port)
        else:
            server = smtplib.SMTP(smtp_host, port)
            server.ehlo()
            if port == 587:
                server.starttls()
                server.ehlo()
        
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_from, [to_email], msg.as_string())
        server.quit()
        print(f"[MAIL SMTP] Email successfully sent to {to_email}")
        return True
    except Exception as e:
        print(f"[MAIL SMTP ERROR] Failed to send via SMTP: {e}. Falling back to file.")
        log_email_locally(to_email, subject, body_html)
        return False

def send_enrollment_approved_email(to_email, name, service):
    subject = f"¡Inscripción Aprobada! Bienvenido/a a ASLYON_va SOLUCIONES"
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e2d4e; background-color: #f4f6fb; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e5e9f0; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div style="text-align: center; border-bottom: 2px solid #e5e9f0; padding-bottom: 20px; margin-bottom: 20px;">
                <h2 style="color: #0b2452; margin: 0;">ASLYON_va <span style="color: #d7a928;">SOLUCIONES</span></h2>
                <p style="font-size: 14px; color: #6b7280; margin: 5px 0 0 0;">Formación · Orientación · Crecimiento</p>
            </div>
            
            <p>Hola, <strong>{name}</strong>,</p>
            
            <p>Nos complace informarte que tu solicitud de inscripción para el servicio de <strong>{service}</strong> ha sido aprobada con éxito.</p>
            
            <p>A partir de este momento, tu cuenta de acceso ya se encuentra activa en nuestra plataforma académica. Puedes ingresar utilizando las siguientes credenciales:</p>
            
            <div style="background-color: #f8faff; border-left: 4px solid #0b2452; padding: 15px; margin: 20px 0; border-radius: 4px;">
                <p style="margin: 5px 0;"><strong>Usuario / Correo:</strong> {to_email}</p>
                <p style="margin: 5px 0;"><strong>Contraseña:</strong> <em>La que especificaste al momento de tu registro</em></p>
            </div>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="https://sistema-elvis.onrender.com" target="_blank" style="background-color: #d7a928; color: #ffffff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">Acceder al Área de Estudiantes</a>
            </p>
            
            <p>Si tienes alguna consulta o necesitas ayuda para ingresar, no dudes en ponerte en contacto con nosotros escribiéndonos directamente por WhatsApp.</p>
            
            <p style="margin-top: 30px; border-top: 1px solid #e5e9f0; padding-top: 20px; font-size: 13px; color: #6b7280;">
                Este correo fue enviado de manera automática por el sistema de gestión académica de ASLYON_va SOLUCIONES.
            </p>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, body_html)

def send_enrollment_rejected_email(to_email, name, service):
    subject = f"Actualización sobre tu solicitud de inscripción en ASLYON_va SOLUCIONES"
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #1e2d4e; background-color: #f4f6fb; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e5e9f0; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <div style="text-align: center; border-bottom: 2px solid #e5e9f0; padding-bottom: 20px; margin-bottom: 20px;">
                <h2 style="color: #0b2452; margin: 0;">ASLYON_va <span style="color: #d7a928;">SOLUCIONES</span></h2>
                <p style="font-size: 14px; color: #6b7280; margin: 5px 0 0 0;">Formación · Orientación · Crecimiento</p>
            </div>
            
            <p>Hola, <strong>{name}</strong>,</p>
            
            <p>Agradecemos tu interés en el servicio de <strong>{service}</strong> de ASLYON_va SOLUCIONES.</p>
            
            <p>Lamentamos informarte que en esta ocasión no ha sido posible validar tu solicitud de matrícula directa a través del sistema web.</p>
            
            <p>Para conocer los motivos o completar cualquier documentación o trámite restante que falte para tu aprobación, te recomendamos ponerte en contacto con secretaría académica o con tu tutor asignado lo antes posible.</p>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="https://wa.me/34641123456?text=Hola,%20quisiera%20consultar%20sobre%20el%20estado%20de%20mi%20inscripcion%20a%20{service}" target="_blank" style="background-color: #0b7a8a; color: #ffffff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">Contactar por WhatsApp</a>
            </p>
            
            <p style="margin-top: 30px; border-top: 1px solid #e5e9f0; padding-top: 20px; font-size: 13px; color: #6b7280;">
                Este correo fue enviado de manera automática por el sistema de gestión académica de ASLYON_va SOLUCIONES.
            </p>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, body_html)
