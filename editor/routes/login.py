from flask import (Blueprint, request, redirect, render_template, flash)
from flask_login import login_user, logout_user, login_required

import editor.db
from editor.auth import User

bp = Blueprint("login", __name__)
  
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user_record = editor.db.get_user(request.form['username'])
    
        if user_record:
            user=User(user_record['user_id'], user_record['user_password'], user_record['user_name'], user_record['user_role'])
            if user.check_password(request.form['password']):
                login_user(user)
                return redirect('/')
        
        flash('Invalid credentials', 'danger')
    return render_template("login/login.html")

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
