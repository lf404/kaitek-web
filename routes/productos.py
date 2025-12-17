import os
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from werkzeug.utils import secure_filename
from bson import ObjectId

# ==========================================================================
# CONFIGURACIÓN DEL BLUEPRINT (Módulo de Gestión de Productos)
# ==========================================================================
# El prefijo '/admin/productos' agrupa todas las rutas de este archivo.
productos_bp = Blueprint("productos", __name__, url_prefix="/admin/productos")

# --- FUNCIONES AUXILIARES (HELPERS) ---

def get_db():
    #Obtiene la conexión activa a la base de datos MongoDB. 
    return current_app.db

def allowed_file(filename):
    
    #Verifica si el archivo subido tiene una extensión permitida 
    #(definida en Config.ALLOWED_EXTENSIONS). 
    
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

# ==========================================================================
# 1. LISTAR PRODUCTOS (READ)
# ==========================================================================
@productos_bp.route("/")
def listar_productos():
    #Muestra la tabla con todos los productos registrados en el admin. 
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    
    # Obtenemos todos los documentos de la colección 'productos'
    productos = list(get_db().productos.find())
    return render_template("admin/productos.html", productos=productos)

# ==========================================================================
# 2. CREAR NUEVO PRODUCTO (CREATE)
# ==========================================================================
@productos_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    #Maneja la creación de un producto y la subida inicial de fotos. 
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    
    if request.method == "POST":
        imagenes = []
        
        # Procesamos la lista de imágenes seleccionadas en el formulario
        if "imagenes" in request.files:
            files = request.files.getlist("imagenes")
            for file in files:
                # Verificamos que el archivo sea válido
                if file and file.filename != '' and allowed_file(file.filename):
                    # Limpiamos el nombre del archivo para evitar caracteres extraños
                    filename = secure_filename(file.filename)
                    # Definimos la ruta física donde se guardará en el servidor
                    ruta = os.path.join(current_app.config["UPLOAD_FOLDER"], "productos", filename)
                    # Guardamos el archivo físico
                    file.save(ruta)
                    # Guardamos la ruta relativa para la base de datos
                    imagenes.append(f"productos/{filename}")
        
        # Insertamos el nuevo documento en MongoDB
        get_db().productos.insert_one({
            "nombre": request.form["nombre"],
            "categoria": request.form["categoria"],
            "precio": request.form["precio"],
            "descripcion": request.form["descripcion"],
            "imagenes": imagenes
        })
        return redirect(url_for("productos.listar_productos"))
        
    return render_template("admin/producto_form.html", producto=None)

# ==========================================================================
# 3. EDITAR PRODUCTO (UPDATE)
# ==========================================================================
@productos_bp.route("/editar/<id>", methods=["GET", "POST"])
def editar_producto(id):
    #Maneja la actualización de datos y la adición de nuevas fotos. 
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    
    db = get_db()
    # Buscamos el producto actual por su ID único
    producto = db.productos.find_one({"_id": ObjectId(id)})
    
    if request.method == "POST":
        # Recuperamos la lista de imágenes que ya tiene el producto
        imagenes_existentes = producto.get("imagenes", [])
        nuevas_imagenes = []

        # Procesamos las NUEVAS imágenes subidas en este envío
        if "imagenes" in request.files:
            files = request.files.getlist("imagenes")
            for file in files:
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    ruta = os.path.join(current_app.config["UPLOAD_FOLDER"], "productos", filename)
                    file.save(ruta)
                    nuevas_imagenes.append(f"productos/{filename}")

        # IMPORTANTE: Combinamos las fotos viejas con las nuevas para no perder nada
        imagenes_totales = imagenes_existentes + nuevas_imagenes

        # Actualizamos el documento en la base de datos
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

    return render_template("admin/producto_form.html", producto=producto)

# ==========================================================================
# 4. ELIMINAR PRODUCTO COMPLETO (DELETE)
# ==========================================================================
@productos_bp.route("/eliminar/<id>")
def eliminar_producto(id):
    #Elimina un producto definitivamente de la base de datos. 
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
        
    get_db().productos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("productos.listar_productos"))

# ==========================================================================
# 5. GESTIÓN INDIVIDUAL DE IMÁGENES
# ==========================================================================
@productos_bp.route("/eliminar-imagen/<id>/<path:filename>")
def eliminar_imagen(id, filename):
    
    #Elimina una sola imagen específica de un producto, 
    #tanto del servidor como del registro en la base de datos. 
    
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))
    
    # 1. Intentamos borrar el archivo físico del disco duro
    try:
        full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception as e:
        print(f"Advertencia: No se pudo borrar el archivo físico: {e}")

    # 2. Quitamos la referencia de la imagen del array 'imagenes' en MongoDB
    # El operador $pull busca el valor exacto dentro de la lista y lo extrae.
    get_db().productos.update_one(
        {"_id": ObjectId(id)},
        {"$pull": {"imagenes": filename}} 
    )

    # 3. Recargamos la página de edición para ver los cambios
    return redirect(url_for("productos.editar_producto", id=id))