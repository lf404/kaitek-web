from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from bson import ObjectId

# Definimos el Blueprint (agrupador de rutas)
categorias_bp = Blueprint("categorias", __name__, url_prefix="/admin/categorias")

def get_db():
    """Helper para conectar a la BD"""
    return current_app.db

# =========================================
# 1. LISTAR Y CREAR (Dashboard de Categorías)
# =========================================
@categorias_bp.route("/", methods=["GET", "POST"])
def gestionar_categorias():
    # Seguridad: Solo admin
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    
    db = get_db()

    # --- CREAR NUEVA (POST) ---
    if request.method == "POST":
        nombre_categoria = request.form.get("nombre")
        
        if nombre_categoria:
            db.categorias.insert_one({
                "nombre": nombre_categoria
            })
            return redirect(url_for("categorias.gestionar_categorias"))

    # --- LISTAR (GET) ---
    categorias = list(db.categorias.find().sort("nombre", 1))
    
    return render_template("admin/categorias.html", categorias=categorias)

# =========================================
# 2. EDITAR CATEGORÍA (NUEVO)
# =========================================
@categorias_bp.route("/editar/<id>", methods=["GET", "POST"])
def editar_categoria(id):
    # Seguridad: Solo admin
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    
    db = get_db()
    
    # --- PROCESAR CAMBIOS (POST) ---
    if request.method == "POST":
        nuevo_nombre = request.form.get("nombre")
        
        if nuevo_nombre:
            # Actualizamos el documento buscando por su _id
            db.categorias.update_one(
                {"_id": ObjectId(id)},
                {"$set": {"nombre": nuevo_nombre}}
            )
            
            # Opcional: Podrías actualizar también los productos que tenían el nombre viejo
            # pero por ahora lo dejamos simple.
            
            return redirect(url_for("categorias.gestionar_categorias"))

    # --- MOSTRAR FORMULARIO DE EDICIÓN (GET) ---
    # Buscamos la categoría actual para mostrar su nombre en el input
    categoria = db.categorias.find_one({"_id": ObjectId(id)})
    
    return render_template("admin/categoria_editar.html", categoria=categoria)

# =========================================
# 3. ELIMINAR CATEGORÍA
# =========================================
@categorias_bp.route("/eliminar/<id>")
def eliminar_categoria(id):
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
        
    get_db().categorias.delete_one({"_id": ObjectId(id)})
    
    return redirect(url_for("categorias.gestionar_categorias"))