import sqlite3
from datetime import datetime
import hashlib
import os

DATABASE = 'database.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            plan_name TEXT NOT NULL DEFAULT 'Básico',
            plan_status TEXT NOT NULL DEFAULT 'active'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage (
            email TEXT,
            year INTEGER,
            month INTEGER,
            photo_count INTEGER DEFAULT 0,
            PRIMARY KEY (email, year, month),
            FOREIGN KEY (email) REFERENCES users(email)
        )
    ''')
    
    cursor.execute('SELECT email FROM users WHERE email = ?', ('admin@admin.com',))
    if not cursor.fetchone():
        password = 'admin123'
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('INSERT INTO users (email, name, password_hash, created_at, plan_name, plan_status) VALUES (?, ?, ?, ?, ?, ?)',
                       ('admin@admin.com', 'Administrador', password_hash, datetime.now().isoformat(), 'Premium', 'active'))
    
    conn.commit()
    conn.close()

def register_user(name, email, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return False
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    created_at = datetime.now().isoformat()
    cursor.execute('INSERT INTO users (email, name, password_hash, created_at, plan_name, plan_status) VALUES (?, ?, ?, ?, ?, ?)',
                   (email, name, password_hash, created_at, 'Básico', 'active'))
    
    conn.commit()
    conn.close()
    return True

def authenticate_user(email, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT password_hash, plan_name, plan_status FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return {'success': False, 'message': 'E-mail não encontrado.'}
    
    password_hash, plan_name, plan_status = user
    if hashlib.sha256(password.encode()).hexdigest() != password_hash:
        conn.close()
        return {'success': False, 'message': 'Senha incorreta.'}
    
    conn.close()
    return {
        'success': True,
        'email': email,
        'plan_name': plan_name,
        'plan_status': plan_status
    }

def get_user_name(email):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else 'Usuário Desconhecido'

def is_admin(email):
    return email == 'admin@admin.com'

def get_all_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT email, name, created_at, plan_name, plan_status FROM users WHERE email != ?', ('admin@admin.com',))
    users = cursor.fetchall()
    
    conn.close()
    return [{'email': email, 'name': name, 'created_at': created_at, 'plan_name': plan_name, 'plan_status': plan_status}
            for email, name, created_at, plan_name, plan_status in users]

def get_usage(email, year, month):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT plan_name FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    
    if result is None:
        conn.close()
        return {
            'success': False,
            'message': 'Usuário não encontrado.'
        }
    
    plan_name = result[0]
    
    cursor.execute('SELECT photo_count FROM usage WHERE email = ? AND year = ? AND month = ?', (email, year, month))
    result = cursor.fetchone()
    photo_count = result[0] if result else 0
    
    limits = {
        'Básico': 300,
        'Pro': 5000,
        'Premium': float('inf')
    }
    limit = limits.get(plan_name, 300)
    remaining = limit - photo_count if limit != float('inf') else 'ilimitadas'
    
    conn.close()
    return {
        'success': True,
        'photo_count': photo_count,
        'limit': limit,
        'remaining': remaining
    }

def increment_usage(email, year, month, count):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Verificar se o usuário existe
        cursor.execute('SELECT plan_name FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        if result is None:
            conn.close()
            return False, "Usuário não encontrado."
        
        plan_name = result[0]
        
        # Inserir ou atualizar o contador de uso
        cursor.execute('INSERT OR IGNORE INTO usage (email, year, month, photo_count) VALUES (?, ?, ?, 0)', (email, year, month))
        cursor.execute('UPDATE usage SET photo_count = photo_count + ? WHERE email = ? AND year = ? AND month = ?', (count, email, year, month))
        
        # Obter o novo contador
        cursor.execute('SELECT photo_count FROM usage WHERE email = ? AND year = ? AND month = ?', (email, year, month))
        new_count = cursor.fetchone()[0]
        
        # Verificar o limite do plano
        limits = {
            'Básico': 300,
            'Pro': 5000,
            'Premium': float('inf')
        }
        limit = limits.get(plan_name, 300)
        
        conn.commit()
        conn.close()
        
        if limit != float('inf') and new_count > limit:
            return False, f"Limite de fotos excedido para o plano {plan_name}. Limite: {limit}, Uso atual: {new_count}"
        return True, "Uso atualizado com sucesso."
    except sqlite3.Error as e:
        if conn:
            conn.close()
        return False, f"Erro no banco de dados: {str(e)}"

def update_user_plan(email, new_plan):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET plan_name = ? WHERE email = ?', (new_plan, email))
    affected_rows = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return affected_rows > 0