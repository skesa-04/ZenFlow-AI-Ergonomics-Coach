from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import threading
from datetime import datetime
import posture_detection
import time  

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zenflow.db'
app.config['SECRET_KEY'] = 'zenflow_secret_789'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class DailyStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)  # e.g., "2026-03-31"
    hour = db.Column(db.Integer, nullable=False)    # e.g., 14
    total_seconds = db.Column(db.Integer, default=0)
    average_focus = db.Column(db.Integer, default=0) 
    good_seconds = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- AUTH ROUTES ---

@app.route("/")
@login_required
def home():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Registration successful"}), 200
    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home')) 
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- ANALYTICS ROUTES ---

@app.route("/stats")
@login_required
def stats_page():
    return render_template("stats.html")

@app.route("/api/hourly_stats/<date_str>")
@login_required
def get_hourly_stats(date_str):
    # This fetches data for the calendar view
    stats = DailyStats.query.filter_by(user_id=current_user.id, date=date_str).all()
    hourly_data = {f"{h:02d}:00": 0 for h in range(24)}
    for s in stats:
        score = (s.good_seconds / s.total_seconds * 100) if s.total_seconds > 0 else 0
        hour_key = f"{int(s.hour):02d}:00"
        hourly_data[hour_key] = round(score)
    
    return jsonify({
        "labels": list(hourly_data.keys()),
        "scores": list(hourly_data.values())
    })

# --- AI & CAMERA ROUTES ---

@app.route("/start_camera")
@login_required
def start():
    posture_detection.stop_detection()
    time.sleep(0.3)
    thread = threading.Thread(target=posture_detection.run_posture_detection, daemon=True)
    thread.start()
    return jsonify({"status": "Camera Started"})

@app.route("/status")
@login_required
def get_status():
    # THIS FIXES THE HEALTH CALCULATION: Index.html needs this to know if you are slouching
    return jsonify({"slouching": posture_detection.slouch_detected_global
    })

@app.route("/stop_camera")
@login_required
def stop():
    posture_detection.stop_detection()
    return jsonify({"status": "Camera Released"})

@app.route("/pause_for_yoga")
@login_required
def pause_for_yoga():
    posture_detection.stop_detection()
    return jsonify({"status": "AI Paused"})

@app.route("/save_stats", methods=['POST'])
@login_required
def save_stats():
    data = request.get_json()

    total_seconds = data.get('total_seconds', 0)
    good_seconds = data.get('good_seconds', 0)
    average_focus = data.get('average_focus', 0)

    date_str = datetime.now().strftime('%Y-%m-%d')
    hour_val = datetime.now().hour

    stat = DailyStats.query.filter_by(
        user_id=current_user.id, 
        date=date_str, 
        hour=hour_val
    ).first()
    
    if stat:
        stat.total_seconds += total_seconds
        stat.good_seconds += good_seconds
        stat.average_focus = int((stat.good_seconds / stat.total_seconds) * 100) if stat.total_seconds > 0 else 0
    else:
        stat = DailyStats(
            user_id=current_user.id,
            date=date_str,
            hour=hour_val,
            total_seconds=total_seconds,
            good_seconds=good_seconds,
            average_focus=average_focus
        )
        db.session.add(stat)
    
    db.session.commit()
    return jsonify({"status": "success"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)