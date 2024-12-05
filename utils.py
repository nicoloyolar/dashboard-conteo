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
