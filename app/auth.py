from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            flash("Logged in!", "success")
            return redirect(url_for('main.index'))
        flash("Invalid credentials", "danger")
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form['username']).first()
        if u:
            flash("User exists!", "danger")
            return redirect(url_for('auth.register'))
        new = User(username=request.form['username'])
        new.set_password(request.form['password'])
        db.session.add(new)
        db.session.commit()
        flash("Account created!", "success")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for('auth.login'))
