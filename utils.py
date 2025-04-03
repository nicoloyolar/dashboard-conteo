rtsp_url = "rtsp://admin:admin123@192.168.31.108:554/cam/realmonitor?channel=6&subtype=0"


def generar_tabla_html_y_mensaje(cantidad_por_hora, estancamientos):
    tabla_html = """
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr>
                <th>Hora</th>
                <th>1kg</th>
                <th>500grs</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
    """
    mensaje_whatsapp = "Reporte de conteo de productos por hora:\n"

    for hora, cantidades in cantidad_por_hora.items():
        total = cantidades['1kg'] + cantidades['500grs']
        tabla_html += f"""
        <tr>
            <td>{hora}:00</td>
            <td>{cantidades['1kg']}</td>
            <td>{cantidades['500grs']}</td>
            <td>{total}</td>
        </tr>
        """
        mensaje_whatsapp += f"{hora}:00 - 1kg: {cantidades['1kg']}, 500grs: {cantidades['500grs']}, Total: {total}\n"

    tabla_html += f"""
        </tbody>
        <tfoot>
            <tr>
                <td colspan="3">Estancamientos</td>
                <td>{estancamientos}</td>
            </tr>
        </tfoot>
    </table>
    """
    mensaje_whatsapp += f"\nEstancamientos detectados: {estancamientos}."

    return tabla_html, mensaje_whatsapp

def format_number(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return value  

def generar_resumen_turno_noche(cantidad_por_hora, estancamientos):

    total_1kg = 0
    total_500grs = 0

    for hora in range(0, 8):  
        if hora in cantidad_por_hora:
            total_1kg += cantidad_por_hora[hora]['1kg']
            total_500grs += cantidad_por_hora[hora]['500grs']

    total_500grs_kg = total_500grs / 2
    total_general = total_1kg + total_500grs_kg

    html = f"""
    <h2>Resumen del Turno de Noche (00:00 - 07:59)</h2>
    <table border="1">
        <tr>
            <th>Formato 1 Kg (kgs)</th>
            <th>Formato 500 Grs (kgs)</th>
            <th>Total (kgs)</th>
        </tr>
        <tr>
            <td>{total_1kg}</td>
            <td>{total_500grs_kg:.2f}</td>
            <td>{total_general:.2f} kg</td>
        </tr>
    </table>
    <p><strong>Estancamientos:</strong> {estancamientos}</p>
    """

    mensaje_whatsapp = f"""
    Resumen del Turno de Noche (00:00 - 07:59)
    Formato 1 Kg: {total_1kg} kg
    Formato 500 Grs: {total_500grs_kg:.2f} kg
    Total: {total_general:.2f} kg
    Estancamientos: {estancamientos}
    """

    return html, mensaje_whatsapp