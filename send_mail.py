from datetime import datetime
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twilio.rest import Client
import os

from database import fetch_turno_noche

def enviar_correo(asunto, cuerpo_html, destinatarios, cc=None):
    """Envía correos mediante el protocolo SMTP"""
    smtp_server     = "smtp.office365.com"
    smtp_port       = 587
    smtp_username   = "desarrollosti@standrews.cl"
    smtp_password   = "Desarrollos2025#$%" 

    msg = MIMEMultipart()
    msg['From']     = smtp_username
    msg['To']       = ", ".join(destinatarios)
    msg['Subject']  = asunto
    msg.attach(MIMEText(cuerpo_html, 'html'))

    if cc:
        msg['Cc'] = ", ".join(cc)
        to_addresses = destinatarios + cc  
    else:
        to_addresses = destinatarios 

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, to_addresses, msg.as_string())
            print("Correo enviado exitosamente.")
            
    except Exception as e:
        print("Error al enviar el correo:", e)
        traceback.print_exc()

def generar_tabla_html_y_mensaje(cantidad_por_hora, estancamientos):
    hora_actual = datetime.now().hour

    cantidades_actuales = cantidad_por_hora.get(hora_actual, {'1kg': 0, '500grs': 0})
    total_actual = cantidades_actuales['1kg'] + (cantidades_actuales['500grs'] / 2)

    html = f"""
    <h2>Resumen de Productos para la Hora Actual ({hora_actual}:00)</h2>
    <table border="1">
        <tr>
            <th>Hora</th>
            <th>Formato 1 Kg (kgs)</th>
            <th>Formato 500 Grs (kgs)</th>
            <th>Total (kgs)</th>
        </tr>
        <tr>
            <td>{hora_actual}:00</td>
            <td>{cantidades_actuales['1kg']}</td>
            <td>{cantidades_actuales['500grs'] / 2:.2f}</td>
            <td>{total_actual:.2f} kg</td>
        </tr>
    </table>
    <p><strong>Estancamientos:</strong> {estancamientos}</p>
    """

    mensaje_whatsapp = f"""
    Resumen de Productos para la Hora {hora_actual}:00
    Formato 1 Kg: {cantidades_actuales['1kg']} kg
    Formato 500 Grs: {cantidades_actuales['500grs'] / 2:.2f} kg
    Total: {total_actual:.2f} kg
    Estancamientos: {estancamientos}
    """
    return html, mensaje_whatsapp

def enviar_mensaje_whatsapp(mensaje_body):
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        to_whatsapp_list = [
            "whatsapp:+56975878696",
            "whatsapp:+56991023906",
            "whatsapp:+56941290435"
        ]
        from_whatsapp = "whatsapp:+14155238886"  

        client = Client(account_sid, auth_token)

        for to_whatsapp in to_whatsapp_list:
            try:
                message = client.messages.create(
                    body=mensaje_body,
                    from_=from_whatsapp,
                    to=to_whatsapp
                )
            except Exception as e:
                print(f"Error al enviar el mensaje a {to_whatsapp}: {e}")

    except Exception as e:
        print("Error al enviar el mensaje de WhatsApp:", e)
    
def generar_resumen_turno_noche(total_kilos, estancamientos):

    html = f"""
    <h2>Resumen del Turno de Noche (00:00 - 07:59)</h2>
    <table border="1">
        <tr>
            <th>Total Producción (kgs)</th>
        </tr>
        <tr>
            <td>{total_kilos:.2f} kg</td>
        </tr>
    </table>
    <p><strong>Estancamientos:</strong> {estancamientos}</p>
    """

    mensaje_whatsapp = f"""
    Resumen del Turno de Noche (00:00 - 07:59)
    Total Producción: {total_kilos:.2f} kg
    Estancamientos: {estancamientos}
    """

    return html, mensaje_whatsapp
