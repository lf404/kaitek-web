import os
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from bson import ObjectId
import cloudinary.uploader

# ==========================================================================
# CONFIGURACIÓN DEL BLUEPRINT
# ==========================================================================
productos_bp = Blueprint("productos", __name__, url_prefix="/admin/productos")

def get_db():
    return current_app.db

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

# ==========================================================================
# 1. LISTAR PRODUCTOS (READ)
# ==========================================================================
@productos_bp.route("/")
def listar_productos():
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    
    productos = list(get_db().productos.find())
    return render_template("admin/productos.html", productos=productos)

# ==========================================================================
# 2. CREAR NUEVO PRODUCTO (CREATE)
# ==========================================================================
@productos_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    
    db = get_db()

    if request.method == "POST":
        imagenes_urls = []
        
        # Procesar subida a Cloudinary
        if "imagenes" in request.files:
            files = request.files.getlist("imagenes")
            for file in files:
                if file and file.filename != '' and allowed_file(file.filename):
                    try:
                        upload_result = cloudinary.uploader.upload(
                            file, 
                            folder="kaitek_productos"
                        )
                        imagenes_urls.append(upload_result['secure_url'])
                    except Exception as e:
                        print(f"Error subiendo imagen a Cloudinary: {e}")
        
        db.productos.insert_one({
            "nombre": request.form["nombre"],
            "categoria": request.form["categoria"],
            "precio": request.form["precio"],
            "descripcion": request.form["descripcion"],
            "imagenes": imagenes_urls
        })
        return redirect(url_for("productos.listar_productos"))
    
    # IMPORTANTE: Obtenemos las categorías de la base de datos para llenar el select
    lista_categorias = list(db.categorias.find().sort("nombre", 1))

    return render_template("admin/producto_form.html", producto=None, categorias=lista_categorias)

# ==========================================================================
# 3. EDITAR PRODUCTO (UPDATE)
# ==========================================================================
@productos_bp.route("/editar/<id>", methods=["GET", "POST"])
def editar_producto(id):
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    
    db = get_db()
    producto = db.productos.find_one({"_id": ObjectId(id)})
    
    if request.method == "POST":
        imagenes_existentes = producto.get("imagenes", [])
        nuevas_imagenes = []

        if "imagenes" in request.files:
            files = request.files.getlist("imagenes")
            for file in files:
                if file and file.filename != '' and allowed_file(file.filename):
                    try:
                        upload_result = cloudinary.uploader.upload(
                            file, 
                            folder="kaitek_productos"
                        )
                        nuevas_imagenes.append(upload_result['secure_url'])
                    except Exception as e:
                        print(f"Error subiendo imagen a Cloudinary: {e}")

        imagenes_totales = imagenes_existentes + nuevas_imagenes

        db.productos.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "nombre": request.form["nombre"],
                "categoria": request.form["categoria"],
                "precio": request.form["precio"],
                "descripcion": request.form["descripcion"],
                "imagenes": imagenes_totales 
            }}
        )
        return redirect(url_for("productos.listar_productos"))

    # IMPORTANTE: También aquí obtenemos las categorías
    lista_categorias = list(db.categorias.find().sort("nombre", 1))

    return render_template("admin/producto_form.html", producto=producto, categorias=lista_categorias)

# ==========================================================================
# 4. ELIMINAR PRODUCTO COMPLETO (DELETE)
# ==========================================================================
@productos_bp.route("/eliminar/<id>")
def eliminar_producto(id):
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
        
    get_db().productos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("productos.listar_productos"))

# ==========================================================================
# 5. GESTIÓN INDIVIDUAL DE IMÁGENES
# ==========================================================================
@productos_bp.route("/eliminar-imagen/<id>")
def eliminar_imagen(id):
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    
    imagen_url = request.args.get('url')
    
    if imagen_url:
        get_db().productos.update_one(
            {"_id": ObjectId(id)},
            {"$pull": {"imagenes": imagen_url}} 
        )

    return redirect(url_for("productos.editar_producto", id=id))