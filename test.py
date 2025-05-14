import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Prueba de correo simple")
msg['Subject'] = "Prueba SMTP desde script"
msg['From'] = "desarrollosti@standrews.cl"
msg['To'] = "nicolas.iloyolar@gmail.com"

try:
    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login("desarrollosti@standrews.cl", "Desarrollos2025#$%")
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        print("Correo enviado correctamente.")
except Exception as e:
    print("Error:", e)
