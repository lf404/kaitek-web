from flask import Blueprint, render_template, current_app, request
from bson.objectid import ObjectId
from flask_mail import Message

# ==========================================================================
# CONFIGURACIÓN DEL BLUEPRINT (Módulo Público)
# ==========================================================================
catalogo_bp = Blueprint("catalogo", __name__)

def get_db():
    return current_app.db

# ==========================================================================
# 1. PÁGINA DE INICIO
# ==========================================================================
@catalogo_bp.route("/")
def home():
    return render_template("catalogo/index.html")

# ==========================================================================
# 2. CATÁLOGO DE PRODUCTOS (Con Filtros y Correcciones)
# ==========================================================================
@catalogo_bp.route("/catalogo")
def catalogo():
    db = get_db()
    
    # 1. Obtener el filtro de la URL (Ej: ?categoria=Pernos)
    categoria_filter = request.args.get('categoria')
    query = {}
    
    # 2. Si hay filtro, lo limpiamos y lo agregamos a la consulta
    if categoria_filter:
        # .strip() elimina espacios en blanco al inicio o final que causan errores
        categoria_limpia = categoria_filter.strip()
        query['categoria'] = categoria_limpia
        
    # 3. Búsqueda de Productos
    # .sort("_id", -1) hace que los productos NUEVOS aparezcan PRIMERO
    productos = list(db.productos.find(query).sort("_id", -1))
    
    # 4. Obtener lista de categorías para el menú de botones
    # Usamos las categorías creadas en el Admin para asegurar coincidencia
    cursor_categorias = db.categorias.find().sort("nombre", 1)
    todas_categorias = [c["nombre"] for c in cursor_categorias]
    
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
        # Buscamos el producto por su ID único
        producto = get_db().productos.find_one({"_id": ObjectId(id)})
    except:
        # Si el ID no es válido o hay error, devolvemos None
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
    if request.method == "POST":
        nombre = request.form.get("nombre")
        empresa = request.form.get("empresa")
        email = request.form.get("email")
        telefono = request.form.get("telefono")
        mensaje = request.form.get("mensaje")

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

        try:
            msg = Message(subject, 
                          sender=current_app.config['MAIL_USERNAME'], 
                          recipients=[current_app.config['MAIL_RECIPIENT']])
            msg.body = body
            current_app.mail.send(msg)
            return render_template("contacto.html", success=True)
            
        except Exception as e:
            print(f"Error enviando correo: {e}")
            return render_template("contacto.html", error=True)

    return render_template("contacto.html")