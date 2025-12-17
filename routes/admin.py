from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from werkzeug.security import check_password_hash

# =========================================
# CONFIGURACIÓN DEL BLUEPRINT (Módulo Admin)
# =========================================
# Este Blueprint agrupa todas las rutas relacionadas con la administración.
# El 'url_prefix="/admin"' significa que todas las rutas aquí empezarán con /admin
# Ejemplo: /admin/ (Login), /admin/dashboard, /admin/logout
admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

def get_db():
    
    #Helper para obtener la conexión a la base de datos
    #desde la aplicación principal.
    
    return current_app.db

# =========================================
# 1. RUTA DE INICIO DE SESIÓN (LOGIN)
# =========================================
@admin_bp.route("/", methods=["GET", "POST"])
def admin_login():
    
    #Maneja el acceso al panel.
    #- GET: Muestra el formulario de login.
    #- POST: Procesa los datos, verifica usuario/contraseña y crea la sesión.
    
    db = get_db()

    # Si el usuario envió el formulario (POST)
    if request.method == "POST":
        # Buscamos al usuario en la colección 'admins' de MongoDB
        admin = db.admins.find_one({
            "username": request.form["username"]
        })

        # Verificamos dos cosas:
        # 1. Que el usuario exista (admin is not None)
        # 2. Que la contraseña coincida usando el hash seguro (check_password_hash)
        if admin and check_password_hash(admin["password"], request.form["password"]):
            
            # ¡Éxito! Guardamos una marca en la sesión del navegador
            session["admin"] = True
            
            # Redirigimos al panel de control
            return redirect(url_for("admin.dashboard"))

    # Si es GET o falló el login, mostramos el formulario de nuevo
    return render_template("admin/login.html")

# =========================================
# 2. PANEL DE CONTROL (DASHBOARD)
# =========================================
@admin_bp.route("/dashboard")
def dashboard():
    
    #Vista principal del administrador.
    #IMPORTANTE: Esta ruta está protegida.
    
    
    # --- PROTECCIÓN DE RUTA ---
    # Si la variable 'admin' no está en la sesión, expulsamos al usuario.
    if not session.get("admin"):
        return redirect(url_for("admin.admin_login"))

    # Si tiene permiso, mostramos el panel
    return render_template("admin/dashboard.html")

# =========================================
# 3. CERRAR SESIÓN (LOGOUT)
# =========================================
@admin_bp.route("/logout")
def admin_logout():
    
    #Cierra la sesión del administrador limpiando las cookies.
    
    session.clear() # Borra todos los datos de la sesión
    return redirect(url_for("admin.admin_login"))