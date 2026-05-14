from flask import Flask, render_template, request, redirect
from flask import send_file
from database import crear_base, get_connection

app = Flask(__name__)
app.secret_key = "clave_secreta"

crear_base()

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# Rutas

# Página de inicio
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/instrumentos")
def instrumentos():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM instrumentos")
    instrumentos = cursor.fetchall()

    conn.close()

    return render_template(
        "instrumentos.html",
        instrumentos=instrumentos
    )


# Crear nuevo instrumento
@app.route("/instrumentos/nuevo", methods=["GET", "POST"])
def nuevo_instrumento():

    if request.method == "POST":

        nombre = request.form["nombre"]
        tipo = request.form["tipo"]
        ubicacion = request.form["ubicacion"]
        descripcion = request.form["descripcion"]
        tolerancia = request.form["tolerancia"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO instrumentos
            (
                nombre,
                tipo,
                ubicacion,
                descripcion,
                tolerancia
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            nombre,
            tipo,
            ubicacion,
            descripcion,
            tolerancia
        ))

        conn.commit()
        conn.close()

        return redirect("/instrumentos")

    return render_template("nuevo_instrumento.html")

# Editar instrumento
@app.route("/instrumentos/editar/<int:id>", methods=["GET", "POST"])
def editar_instrumento(id):

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        tipo = request.form["tipo"]
        ubicacion = request.form["ubicacion"]
        descripcion = request.form["descripcion"]
        tolerancia = request.form["tolerancia"]


        cursor.execute("""
            UPDATE instrumentos
            SET nombre = ?,
                tipo = ?,
                ubicacion = ?,
                descripcion = ?
            WHERE id = ?
        """, (
            nombre,
            tipo,
            ubicacion,
            descripcion,
            id
        ))

        conn.commit()
        conn.close()

        return redirect("/instrumentos")

    cursor.execute(
        "SELECT * FROM instrumentos WHERE id = ?",
        (id,)
    )

    instrumento = cursor.fetchone()

    conn.close()

    return render_template(
        "editar_instrumento.html",
        instrumento=instrumento
    )


# Eliminar instrumento
@app.route("/instrumentos/eliminar/<int:id>")
def eliminar_instrumento(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM instrumentos WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/instrumentos")

# Página de calibraciones de un instrumento
@app.route("/calibraciones/<int:instrumento_id>")
def calibraciones(instrumento_id):

    conn = get_connection()
    cursor = conn.cursor()

    # Instrumento
    cursor.execute(
        "SELECT * FROM instrumentos WHERE id = ?",
        (instrumento_id,)
    )

    instrumento = cursor.fetchone()

    # Calibraciones
    cursor.execute("""
        SELECT * FROM calibraciones
        WHERE instrumento_id = ?
        ORDER BY id DESC
    """, (instrumento_id,))

    calibraciones = cursor.fetchall()

    conn.close()

    return render_template(
        "calibraciones.html",
        instrumento=instrumento,
        calibraciones=calibraciones
    )

# Crear nueva calibración
@app.route(
    "/calibraciones/nueva/<int:instrumento_id>",
    methods=["GET", "POST"]
)
def nueva_calibracion(instrumento_id):

    conn = get_connection()
    cursor = conn.cursor()

    # Obtener instrumento
    cursor.execute(
        "SELECT * FROM instrumentos WHERE id = ?",
        (instrumento_id,)
    )

    instrumento = cursor.fetchone()

    if request.method == "POST":

        fecha = request.form["fecha"]
        responsable = request.form["responsable"]
        observaciones = request.form["observaciones"]

        cursor.execute("""
            INSERT INTO calibraciones
            (
                instrumento_id,
                fecha,
                responsable,
                observaciones
            )
            VALUES (?, ?, ?, ?)
        """, (
            instrumento_id,
            fecha,
            responsable,
            observaciones
        ))

        conn.commit()
        conn.close()

        return redirect(f"/calibraciones/{instrumento_id}")

    conn.close()

    return render_template(
        "nueva_calibracion.html",
        instrumento=instrumento
    )

# Página de mediciones de una calibración
@app.route("/mediciones/<int:calibracion_id>")
def mediciones(calibracion_id):

    conn = get_connection()
    cursor = conn.cursor()

    # Calibración
    cursor.execute("""
        SELECT * FROM calibraciones
        WHERE id = ?
    """, (calibracion_id,))

    calibracion = cursor.fetchone()

    # Instrumento asociado
    cursor.execute("""
        SELECT * FROM instrumentos
        WHERE id = ?
    """, (calibracion["instrumento_id"],))

    instrumento = cursor.fetchone()

    # Mediciones
    cursor.execute("""
        SELECT * FROM mediciones
        WHERE calibracion_id = ?
        ORDER BY id ASC
    """, (calibracion_id,))

    mediciones = cursor.fetchall()

    conn.close()

    return render_template(
        "mediciones.html",
        calibracion=calibracion,
        instrumento=instrumento,
        mediciones=mediciones
    )

# Crear nueva medición
@app.route(
    "/mediciones/nueva/<int:calibracion_id>",
    methods=["GET", "POST"]
)
def nueva_medicion(calibracion_id):

    conn = get_connection()
    cursor = conn.cursor()

    # Obtener calibración
    cursor.execute("""
        SELECT * FROM calibraciones
        WHERE id = ?
    """, (calibracion_id,))

    calibracion = cursor.fetchone()

    # Obtener instrumento
    cursor.execute("""
        SELECT * FROM instrumentos
        WHERE id = ?
    """, (calibracion["instrumento_id"],))

    instrumento = cursor.fetchone()

    if request.method == "POST":

        valor_patron = float(
            request.form["valor_patron"]
        )

        valor_medido = float(
            request.form["valor_medido"]
        )

        # Calcular error automáticamente
        error = valor_medido - valor_patron

        cursor.execute("""
            INSERT INTO mediciones
            (
                calibracion_id,
                valor_patron,
                valor_medido,
                error
            )
            VALUES (?, ?, ?, ?)
        """, (
            calibracion_id,
            valor_patron,
            valor_medido,
            error
        ))

        conn.commit()
        conn.close()

        return redirect(
            f"/mediciones/{calibracion_id}"
        )

    conn.close()

    return render_template(
        "nueva_medicion.html",
        calibracion=calibracion,
        instrumento=instrumento
    )


# Exportar PDF de una calibración
@app.route("/pdf/<int:calibracion_id>")
def exportar_pdf(calibracion_id):

    conn = get_connection()
    cursor = conn.cursor()

    # Calibración
    cursor.execute("""
        SELECT * FROM calibraciones
        WHERE id = ?
    """, (calibracion_id,))

    calibracion = cursor.fetchone()

    # Instrumento
    cursor.execute("""
        SELECT * FROM instrumentos
        WHERE id = ?
    """, (calibracion["instrumento_id"],))

    instrumento = cursor.fetchone()

    # Mediciones
    cursor.execute("""
        SELECT * FROM mediciones
        WHERE calibracion_id = ?
        ORDER BY id ASC
    """, (calibracion_id,))

    mediciones = cursor.fetchall()

    conn.close()

    # Nombre PDF
    filename = f"calibracion_{calibracion_id}.pdf"

    # Crear documento
    doc = SimpleDocTemplate(filename)

    elementos = []

    estilos = getSampleStyleSheet()

    # Título
    titulo = Paragraph(
        "CERTIFICADO DE CALIBRACIÓN",
        estilos["Title"]
    )

    elementos.append(titulo)
    elementos.append(Spacer(1, 20))

    # Datos principales
    datos = f"""
    <b>Instrumento:</b> {instrumento['nombre']}<br/>
    <b>Fecha:</b> {calibracion['fecha']}<br/>
    <b>Responsable:</b> {calibracion['responsable']}<br/>
    """

    elementos.append(
        Paragraph(datos, estilos["BodyText"])
    )

    elementos.append(Spacer(1, 20))

    # Tabla
    data = [
        ["Patrón", "Medido", "Error"]
    ]

    for medicion in mediciones:

        data.append([
            medicion["valor_patron"],
            medicion["valor_medido"],
            medicion["error"]
        ])

    tabla = Table(data)

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

        ("BOTTOMPADDING", (0,0), (-1,0), 12),
    ]))

    elementos.append(tabla)

    # Generar PDF
    doc.build(elementos)

    return send_file(
        filename,
        as_attachment=True
    )




if __name__ == "__main__":
    app.run(debug=True)