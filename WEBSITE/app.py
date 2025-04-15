from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from database import init_db, register_user, authenticate_user, get_user_name, is_admin, get_all_users, get_usage, increment_usage, update_user_plan
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_aqui"

init_db()

PLANOS = [
    {"nome": "Básico", "preco": "R$ 19,90/mês", "recursos": ["300 fotos/mês", "Suporte básico", "1 usuário"]},
    {"nome": "Pro", "preco": "R$ 49,90/mês", "recursos": ["5000 fotos/mês", "Suporte prioritário", "2 usuários"]},
    {"nome": "Premium", "preco": "R$ 99,90/mês", "recursos": ["Fotos ilimitadas", "Suporte 24/7", "10 usuários"]}
]

@app.route('/')
def index():
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    auth_result = authenticate_user(email, password)
    if auth_result['success']:
        now = datetime.now()
        usage = get_usage(email, now.year, now.month)
        if not usage.get('success'):
            return jsonify({'success': False, 'message': usage.get('message', 'Erro ao obter uso.')})
        auth_result['usage'] = usage
    return jsonify(auth_result)

@app.route('/api/usage', methods=['POST'])
def api_usage():
    data = request.get_json()
    email = data.get('email')
    now = datetime.now()
    usage = get_usage(email, now.year, now.month)
    return jsonify(usage)

@app.route('/api/increment_usage', methods=['POST'])
def api_increment_usage():
    data = request.get_json()
    email = data.get('email')
    count = data.get('count', 1)
    now = datetime.now()
    
    # Validar entrada
    if not email or not isinstance(count, (int, float)) or count < 0:
        return jsonify({"success": False, "message": "E-mail ou contagem inválida."}), 400
    
    success, message = increment_usage(email, now.year, now.month, count)
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        auth_result = authenticate_user(email, password)
        if auth_result['success']:
            session['user_email'] = email
            session['plan_name'] = auth_result['plan_name']
            session['plan_status'] = auth_result['plan_status']
            now = datetime.now()
            usage = get_usage(email, now.year, now.month)
            if not usage.get('success'):
                flash(usage.get('message', 'Erro ao obter uso.'), 'danger')
                return redirect(url_for('login'))
            session['photo_count'] = usage['photo_count']
            session['limit'] = usage['limit']
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(auth_result['message'], 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if register_user(name, email, password):
            flash('Registro bem-sucedido! Você foi registrado com o plano Básico. Faça login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('E-mail já registrado.', 'danger')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        flash('Faça login para acessar o dashboard.', 'warning')
        return redirect(url_for('login'))
    if is_admin(session['user_email']):
        return redirect(url_for('admin_dashboard'))
    
    user_name = get_user_name(session['user_email'])
    plan_name = session.get('plan_name', 'Básico')
    plan_status = session.get('plan_status', 'active')
    photo_count = session.get('photo_count', 0)
    limit = session.get('limit', 300)
    
    limit_display = limit if limit != float('inf') else 'ilimitadas'
    remaining = (limit - photo_count) if limit != float('inf') else 'ilimitadas'
    
    return render_template(
        'dashboard.html',
        user_name=user_name,
        planos=PLANOS,
        plan_name=plan_name,
        plan_status=plan_status,
        photo_count=photo_count,
        limit_display=limit_display,
        remaining=remaining
    )

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_email' not in session:
        flash('Faça login para acessar o dashboard.', 'warning')
        return redirect(url_for('login'))
    if not is_admin(session['user_email']):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('dashboard'))
    user_name = get_user_name(session['user_email'])
    users = get_all_users()
    return render_template('admin/admin_dashboard.html', user_name=user_name, users=users)

@app.route('/update_plan', methods=['POST'])
def update_plan():
    if 'user_email' not in session or not is_admin(session['user_email']):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('dashboard'))
    
    email = request.form.get('email')
    new_plan = request.form.get('plan_name')
    
    if not email or not new_plan:
        flash('E-mail ou plano não fornecido.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    valid_plans = ['Básico', 'Pro', 'Premium']
    if new_plan not in valid_plans:
        flash('Plano inválido.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if update_user_plan(email, new_plan):
        flash(f'Plano de {email} atualizado para {new_plan} com sucesso!', 'success')
    else:
        flash('Erro ao atualizar o plano.', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('plan_name', None)
    session.pop('plan_status', None)
    session.pop('photo_count', None)
    session.pop('limit', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)