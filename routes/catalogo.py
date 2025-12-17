from flask import Blueprint, render_template, current_app, request
from bson.objectid import ObjectId
from flask_mail import Message # Importante para el envío de correos

# ==========================================================================
# CONFIGURACIÓN DEL BLUEPRINT (Módulo Público)
# ==========================================================================
catalogo_bp = Blueprint("catalogo", __name__)

def get_db():
    """ Helper para obtener la conexión a la base de datos. """
    return current_app.db

# ==========================================================================
# 1. PÁGINA DE INICIO
# ==========================================================================
@catalogo_bp.route("/")
def home():
    return render_template("catalogo/index.html")

# ==========================================================================
# 2. CATÁLOGO DE PRODUCTOS (Con Filtros)
# ==========================================================================
@catalogo_bp.route("/catalogo")
def catalogo():
    db = get_db()
    
    # 1. Filtro por categoría
    categoria_filter = request.args.get('categoria')
    query = {}
    if categoria_filter:
        query['categoria'] = categoria_filter
        
    # 2. Búsqueda en BD
    productos = list(db.productos.find(query))
    
    # 3. Lista de categorías para el menú
    todas_categorias = db.productos.distinct("categoria")
    
    return render_template(
        "catalogo/catalogo.html", 
        productos=productos, 
        categorias=todas_categorias, 
        cat_actual=categoria_filter
    )

# ==========================================================================
# 3. DETALLE DE PRODUCTO
# ==========================================================================
@catalogo_bp.route("/producto/<id>")
def producto(id):
    try:
        producto = get_db().productos.find_one({"_id": ObjectId(id)})
    except:
        producto = None
    return render_template("catalogo/producto.html", producto=producto)

# ==========================================================================
# 4. PÁGINAS INFORMATIVAS
# ==========================================================================
@catalogo_bp.route("/servicios")
def servicios():
    return render_template("servicios.html")

@catalogo_bp.route("/quienes-somos")
def quienes_somos():
    return render_template("quienes_somos.html")

# ==========================================================================
# 5. CONTACTO (Formulario y Envío de Correo)
# ==========================================================================
@catalogo_bp.route("/contacto", methods=["GET", "POST"])
def contacto():
    """
    Maneja tanto la vista del formulario (GET) 
    como el procesamiento del envío del correo (POST).
    """
    if request.method == "POST":
        # 1. Obtener datos del formulario HTML
        nombre = request.form.get("nombre")
        empresa = request.form.get("empresa")
        email = request.form.get("email")
        telefono = request.form.get("telefono")
        mensaje = request.form.get("mensaje")

        # 2. Configurar el asunto y cuerpo del correo
        subject = f"Nuevo Mensaje Web de: {nombre}"
        body = f"""
        Haz recibido una nueva solicitud de contacto desde la web:
        
        Nombre: {nombre}
        Empresa: {empresa}
        Email: {email}
        Teléfono: {telefono}
        
        Mensaje:
        {mensaje}
        """

        # 3. Intentar enviar el correo usando Flask-Mail
        try:
            msg = Message(subject, 
                          sender=current_app.config['MAIL_USERNAME'], 
                          recipients=[current_app.config['MAIL_RECIPIENT']])
            msg.body = body
            current_app.mail.send(msg)
            
            # Si todo sale bien, recargamos la página con variable de éxito
            print("Correo enviado con éxito")
            return render_template("contacto.html", success=True)
            
        except Exception as e:
            # Si falla (ej: mala contraseña), mostramos error
            print(f"Error enviando correo: {e}")
            return render_template("contacto.html", error=True)

    # Si es GET (solo ver la página), mostramos el formulario limpio
    return render_template("contacto.html")