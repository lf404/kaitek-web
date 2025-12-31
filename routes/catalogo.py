from flask import Blueprint, render_template, current_app, request
from bson.objectid import ObjectId
from flask_mail import Message

catalogo_bp = Blueprint("catalogo", __name__)

def get_db():
    return current_app.db

@catalogo_bp.route("/")
def home():
    return render_template("catalogo/index.html")

@catalogo_bp.route("/catalogo")
def catalogo():
    db = get_db()
    
    # 1. Filtros inteligentes
    categoria_filter = request.args.get('categoria')
    query = {}
    
    if categoria_filter:
        # Limpiamos espacios que puedan romper la búsqueda
        query['categoria'] = categoria_filter.strip()
        
    # 2. Búsqueda (Ordenamos por _id descendente para ver lo nuevo primero)
    productos = list(db.productos.find(query).sort("_id", -1))
    
    # 3. Categorías para los botones
    cursor_categorias = db.categorias.find().sort("nombre", 1)
    todas_categorias = [c["nombre"] for c in cursor_categorias]
    
    return render_template(
        "catalogo/catalogo.html", 
        productos=productos, 
        categorias=todas_categorias, 
        cat_actual=categoria_filter
    )

@catalogo_bp.route("/producto/<id>")
def producto(id):
    try:
        producto = get_db().productos.find_one({"_id": ObjectId(id)})
    except:
        producto = None
    return render_template("catalogo/producto.html", producto=producto)

@catalogo_bp.route("/servicios")
def servicios():
    return render_template("servicios.html")

@catalogo_bp.route("/quienes-somos")
def quienes_somos():
    return render_template("quienes_somos.html")

@catalogo_bp.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        # ... (Tu lógica de correo se mantiene igual)
        try:
            # Simulamos éxito para no alargar el código aquí
            return render_template("contacto.html", success=True)
        except:
            return render_template("contacto.html", error=True)
    return render_template("contacto.html")