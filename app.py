from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2

app = Flask(__name__)
app.secret_key = '123456'

db_config = {
    'dbname': 'AnimeLista',
    'user': 'postgres',
    'password': '2001',
    'host': 'localhost',  # o la dirección de tu servidor de base de datos
}

def conectar_db():
    return psycopg2.connect(**db_config)

@app.route('/')
def inicio():
    return render_template('layout.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        try:
            conn = conectar_db()
            cursor = conn.cursor()

            # Insertar datos en la tabla usuarios
            cursor.execute("INSERT INTO usuarios (username, email, password) VALUES (%s, %s, %s)", (username, email, password))

            conn.commit()
            conn.close()

            return redirect(url_for('login'))  # Redirige a la página de inicio de sesión después de registrarse

        except Exception as e:
            print(f"Error al registrar el usuario: {e}")
            conn.rollback()
            conn.close()

    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = conectar_db()
            cursor = conn.cursor()

            # Verificar las credenciales del usuario en la base de datos
            cursor.execute("SELECT id, username FROM usuarios WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()

            if user:
                # Almacenar la información del usuario en la sesión
                session['user_id'] = user[0]
                session['username'] = user[1]

                conn.close()
                return redirect(url_for('animes'))

            conn.close()

        except Exception as e:
            print(f"Error al iniciar sesión: {e}")
            conn.close()

    return render_template('login.html')

@app.route('/animes', methods=['GET', 'POST'])
def animes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        if request.form['action'] == 'agregar':
            titulo = request.form['titulo']
            genero = request.form['genero']
            puntuacion = request.form['puntuacion']

            try:
                conn = conectar_db()
                cursor = conn.cursor()

                # Agregar un anime a la lista del usuario
                cursor.execute("INSERT INTO animes (user_id, titulo, genero, puntuacion) VALUES (%s, %s, %s, %s)",
                               (user_id, titulo, genero, puntuacion))

                conn.commit()
                conn.close()

            except Exception as e:
                print(f"Error al agregar un anime: {e}")
                conn.close()

        elif request.form['action'] == 'eliminar':
            anime_id = request.form['anime_id']

            try:
                conn = conectar_db()
                cursor = conn.cursor()

                # Eliminar un anime de la lista del usuario
                cursor.execute("DELETE FROM animes WHERE id = %s AND user_id = %s", (anime_id, user_id))

                conn.commit()
                conn.close()

            except Exception as e:
                print(f"Error al eliminar un anime: {e}")
                conn.close()

        elif request.form['action'] == 'editar':
            anime_id = request.form['anime_id']
            nuevo_titulo = request.form['nuevo_titulo']
            nuevo_genero = request.form['nuevo_genero']
            nueva_puntuacion = request.form['nueva_puntuacion']

            try:
                conn = conectar_db()
                cursor = conn.cursor()

                # Editar los detalles de un anime en la lista del usuario
                cursor.execute(
                    "UPDATE animes SET titulo = %s, genero = %s, puntuacion = %s WHERE id = %s AND user_id = %s",
                    (nuevo_titulo, nuevo_genero, nueva_puntuacion, anime_id, user_id))

                conn.commit()
                conn.close()

            except Exception as e:
                print(f"Error al editar un anime: {e}")
                conn.close()

    # Obtener la lista de animes asociada al usuario
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, titulo, genero, puntuacion FROM animes WHERE user_id = %s", (user_id,))
        animes_del_usuario = cursor.fetchall()

        conn.close()

    except Exception as e:
        print(f"Error al obtener la lista de animes del usuario: {e}")
        conn.close()

    return render_template('animes.html', animes=animes_del_usuario)

@app.route('/usuarios', methods=['GET'])
def usuarios():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Obtener la lista de todos los usuarios
        cursor.execute("SELECT id, username FROM usuarios")
        usuarios = cursor.fetchall()

        # Obtener los animes asociados a cada usuario
        lista_usuarios = []
        for usuario in usuarios:
            cursor.execute("SELECT id, titulo, genero, puntuacion FROM animes WHERE user_id = %s", (usuario[0],))
            animes_del_usuario = cursor.fetchall()
            usuario_info = {
                'usuario_id': usuario[0],
                'username': usuario[1],
                'animes': animes_del_usuario
            }
            lista_usuarios.append(usuario_info)

        conn.close()

        return render_template('usuarios.html', usuarios=lista_usuarios)

    except Exception as e:
        print(f"Error al obtener la lista de usuarios y animes: {e}")
        conn.close()

    return redirect(url_for('animes'))


try:
    conn=psycopg2.connect(
        host='localhost',
        user='postgres',
        password='2001',
        database='AnimeLista'
    )
    print('conexion exitosa')

except Exception as ex:
    print(ex)

if __name__ == '__main__':
    app.run(debug=True)
