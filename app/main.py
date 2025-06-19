from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import MySQLdb
import time

app = Flask(__name__)
app.secret_key = 'ajl'

def connect_db():
    while True:
        try:
            db = MySQLdb.connect(
                host="mysql_db",
                user="root",
                passwd="root",
                db="simples_api",
                charset='utf8mb4'
            )
            print("✅ Conectado ao MySQL com sucesso!")
            return db
        except MySQLdb.OperationalError:
            print("❌ Falha na conexão com o MySQL, tentando novamente em 3 segundos...")
            time.sleep(3)

def get_db():
    if 'db' not in g:
        g.db = connect_db()
    return g.db

def get_cursor():
    db = get_db()
    return db.cursor()

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Rota Home - mostra itens e mensagem flash
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = get_cursor()
    cursor.execute("SELECT id, title FROM items WHERE user_id = %s", (session['user_id'],))
    items = cursor.fetchall()
    cursor.close()

    return render_template('index.html', items=items)

# Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor = get_cursor()
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close()
            flash('Email já cadastrado. Faça login.', 'error')
            return redirect(url_for('login'))

        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        get_db().commit()
        cursor.close()
        flash('Registro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = get_cursor()
        cursor.execute("SELECT id, password FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and user[1] == password:
            session['user_id'] = user[0]
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha inválidos.', 'error')

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você saiu da sessão.', 'success')
    return redirect(url_for('login'))

# Adicionar item
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        cursor = get_cursor()
        cursor.execute("INSERT INTO items (title, user_id) VALUES (%s, %s)", (title, session['user_id']))
        get_db().commit()
        cursor.close()
        flash('Item adicionado com sucesso!')
        return redirect(url_for('index'))

    return render_template('add_item.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
