from datetime import datetime
from flask import Flask, render_template, request
from flask import Flask, request, jsonify
from datetime import datetime
from database import logger, insertar_conteo, fetch_por_hora, fetch_total_ultimo_dia, fetch_ult_15_min, fetch_ult_45_min, fetch_turno_noche
from send_mail import enviar_correo, enviar_mensaje_whatsapp, generar_resumen_turno_noche, generar_tabla_html_y_mensaje
from utils import format_number

cantidad_por_hora = {i: {'1kg': 0, '500grs': 0, 'estancamiento': 0, 'total': 0} for i in range(24)}
ultima_hora_envio = None

app = Flask(__name__)
app.template_filter('format_number')(format_number)

@app.route('/api/actualizar_conteo', methods=['POST'])
def actualizar_conteo():
    """Actualiza el conteo e inyecta los datos en la base de datos y envía un correo de resumen."""
    
    try:
        data            = request.get_json()
        p_c_1kg         = data.get('p_c_1kg', 0)
        p_c_500grs      = data.get('p_c_500grs', 0)
        timestamp_str   = data.get('timestamp')

        if not timestamp_str:
            return jsonify({'error': 'Falta el campo timestamp'}), 400

        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')

        if p_c_1kg > 0:
            insertar_conteo('1kg', p_c_1kg, timestamp)
        
        if p_c_500grs > 0:
            insertar_conteo('500grs', p_c_500grs, timestamp)

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': 'Error al procesar la solicitud'}), 400

ultimo_envio_minuto = None

ultima_hora_enviada = None

@app.route('/enviar_correo', methods=['GET'])
def enviar_correo_periodico():
    try:
        global ultima_hora_enviada, ultimo_resumen_enviado
        
        hora_actual = datetime.now()
        minuto_actual = hora_actual.minute
        hora_actual_simple = hora_actual.hour
        dia_semana = hora_actual.weekday()  

        if dia_semana >= 5 or not (8 <= hora_actual_simple <= 18):
            return jsonify({'status': 'Fuera de horario o día no permitido para envío'}), 200

        if minuto_actual == 59 and hora_actual_simple != ultima_hora_enviada:
            ultima_hora_enviada = hora_actual_simple  

            datos_ultima_hora = fetch_por_hora()
            datos_turno_noche = fetch_turno_noche()

            cantidad_por_hora = {}
            for row in datos_ultima_hora:
                hora = row[2]
                peso = row[1]
                cantidad = row[0]

                if hora not in cantidad_por_hora:
                    cantidad_por_hora[hora] = {'1kg': 0, '500grs': 0}

                if peso == '1kg':
                    cantidad_por_hora[hora]['1kg'] += cantidad
                elif peso == '500grs':
                    cantidad_por_hora[hora]['500grs'] += cantidad

            estancamientos = 0  

            tabla_html, mensaje_whatsapp = generar_tabla_html_y_mensaje(
                cantidad_por_hora=cantidad_por_hora,
                estancamientos=estancamientos
            )

            enviar_correo(
                asunto="Reporte Conteo Productos",
                cuerpo_html=tabla_html,
                destinatarios=["nicolas.iloyolar@gmail.com", "sanmaglass@gmail.com", "afaundez@standrews.cl"],
                cc=["desarrollosti@standrews.cl"]
            )

        if hora_actual_simple == 8 and minuto_actual == 00: 
            datos_turno_noche = fetch_turno_noche()
            print("Datos turno noche:", datos_turno_noche)

            total_kilos = 0

            for row in datos_turno_noche:
                peso = row[0]  
                cantidad = row[1]  

                if peso == '1kg':
                    total_kilos += cantidad
                elif peso == '500grs':
                    total_kilos += cantidad / 2  

            html_resumen, mensaje_whatsapp = generar_resumen_turno_noche(total_kilos, estancamientos=0)

            enviar_correo(
                asunto="Resumen Turno Noche",
                cuerpo_html=html_resumen,
                destinatarios=["nicolas.iloyolar@gmail.com", "sanmaglass@gmail.com", "afaundez@standrews.cl"],
                cc=["desarrollosti@standrews.cl"]
            )

            return jsonify({'status': 'Correo turno noche enviado exitosamente'}), 200

        else:
            return jsonify({'status': 'No es el minuto 59 o correo ya enviado para esta hora.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    global ultima_hora_envio

    try:
        total_ultimo_dia        = fetch_total_ultimo_dia()
        cantidad_ult_15_min     = fetch_ult_15_min()
        cantidad_ult_45_min     = fetch_ult_45_min()
        cantidad_por_hora       = fetch_por_hora()

        total_1kg = 0
        total_500grs = 0

        cantidad_ult_15_min_dict = {'1kg': 0, '500grs': 0}
        cantidad_ult_45_min_dict = {'1kg': 0, '500grs': 0}
        cantidad_por_hora_dict = {}

        for row in total_ultimo_dia:
            if row[1] == '1kg':
                total_1kg = row[0]
            elif row[1] == '500grs':
                total_500grs = row[0]

        for row in cantidad_ult_15_min:
            etiqueta = row[1]
            cantidad = row[0]
            if etiqueta == '1kg':
                cantidad_ult_15_min_dict['1kg'] += cantidad
            elif etiqueta == '500grs':
                cantidad_ult_15_min_dict['500grs'] += cantidad

        for row in cantidad_ult_45_min:
            etiqueta = row[1]
            cantidad = row[0]
            if etiqueta == '1kg':
                cantidad_ult_45_min_dict['1kg'] += cantidad
            elif etiqueta == '500grs':
                cantidad_ult_45_min_dict['500grs'] += cantidad

        for row in cantidad_por_hora:
            hora = row[2]
            etiqueta = row[1]
            cantidad = row[0]

            if hora not in cantidad_por_hora_dict:
                cantidad_por_hora_dict[hora] = {'1kg': 0, '500grs': 0}

            if etiqueta == '1kg':
                cantidad_por_hora_dict[hora]['1kg'] += cantidad
            elif etiqueta == '500grs':
                cantidad_por_hora_dict[hora]['500grs'] += cantidad

        velocidad_ult_15_min        = (cantidad_ult_15_min_dict['1kg'] + (cantidad_ult_15_min_dict['500grs'] / 2)) * 4
        velocidad_ult_45_min        = (cantidad_ult_45_min_dict['1kg'] + cantidad_ult_45_min_dict['500grs']) * 4
        velocidad_promedio_turno    = (total_1kg + (total_500grs / 2)) / 10
        
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return "Error al ejecutar la consulta."

    return render_template(
        'home.html', 
        total_1kg=total_1kg, 
        total_500grs=total_500grs,
        velocidad_promedio_turno=velocidad_promedio_turno,
        cantidad_1kg_ult_15min=cantidad_ult_15_min_dict['1kg'],
        cantidad_500grs_ult_15min=cantidad_ult_15_min_dict['500grs'],
        cantidad_1kg_ult_45min=cantidad_ult_45_min_dict['1kg'],
        cantidad_500grs_ult_45min=cantidad_ult_45_min_dict['500grs'],
        velocidad_ult_15_min=velocidad_ult_15_min,
        velocidad_ult_45_min=velocidad_ult_45_min,
        cantidad_por_hora=cantidad_por_hora_dict
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
