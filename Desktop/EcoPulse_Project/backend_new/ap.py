# app.py

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS # Must be imported and enabled
from datetime import datetime, date, timedelta
from carbon_data import (
    CARBON_COEFFICIENTS, ECO_POINTS_AWARD, ACHIEVEMENT_TIERS, HIGH_IMPACT_THRESHOLD_G
)

# --- 1. APP CONFIGURATION ---
app = Flask(__name__)
# Enable CORS for frontend integration (Port 3000 -> Port 5000)
CORS(app) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecotrack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 2. DATABASE MODELS (Tables) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    total_eco_points = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    # last_login is critical for streak logic
    last_login = db.Column(db.Date, default=date.today())

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False) 
    activity_type = db.Column(db.String(50), nullable=False) # e.g., 'Car', 'Vegan'
    input_value = db.Column(db.Float, nullable=False) 
    co2_footprint_g = db.Column(db.Integer, default=0)
    eco_points_earned = db.Column(db.Integer, default=0)


# --- 3. HELPER FUNCTIONS ---
def get_user_title(points):
    title = ACHIEVEMENT_TIERS[0]
    for tier_points, tier_title in sorted(ACHIEVEMENT_TIERS.items(), reverse=True):
        if points >= tier_points:
            title = tier_title
            break
    return title

def calculate_co2_and_points(activity_type, input_value):
    coefficient = CARBON_COEFFICIENTS.get(activity_type, 0)
    co2_g = int(input_value * coefficient)
    points = ECO_POINTS_AWARD.get(activity_type, 0)
    return co2_g, points


# --- 4. DATABASE CLI COMMANDS ---
@app.cli.command("init-db")
def init_db():
    with app.app_context():
        db.create_all()
        # Create a single demo user for testing (ID 1)
        if not User.query.filter_by(username='demo_user').first():
            demo_user = User(username='demo_user', total_eco_points=100, current_streak=1)
            db.session.add(demo_user)
            db.session.commit()
            print("Demo user 'demo_user' added (ID 1).")
        print("Database initialized.")


# --- 5. API ENDPOINTS (The Logic) ---

@app.route('/api/track/<int:user_id>', methods=['POST'])
def track_activity(user_id):
    # This simulates the automated or one-tap input.
    data = request.get_json()
    if not data or not all(key in data for key in ['category', 'type', 'value']):
        return jsonify({"error": "Invalid input data"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    co2_g, points = calculate_co2_and_points(data['type'], data['value'])
    
    # Save Activity
    new_activity = ActivityLog(user_id=user_id, category=data['category'], 
                               activity_type=data['type'], input_value=data['value'],
                               co2_footprint_g=co2_g, eco_points_earned=points)
    
    # Update User Stats
    user.total_eco_points += points
    user.last_login = date.today() # Update login to ensure streak is maintained

    db.session.add(new_activity)
    db.session.commit()

    return jsonify({"status": "success", "points": points, "new_total_points": user.total_eco_points}), 201

@app.route('/api/summary/<int:user_id>', methods=['GET'])
def get_user_summary(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    today_start = datetime.combine(date.today(), datetime.min.time())
    daily_activities = ActivityLog.query.filter(
        ActivityLog.user_id == user_id,
        ActivityLog.timestamp >= today_start
    ).all()
    
    total_co2_g = sum(a.co2_footprint_g for a in daily_activities)
    
    # --- Personalized Insight Logic (Addressing User Motivation) ---
    suggestion = "Keep up the great work today!"
    high_impact_activities = [a for a in daily_activities if a.co2_footprint_g > HIGH_IMPACT_THRESHOLD_G]
    
    if high_impact_activities:
        worst_activity = max(high_impact_activities, key=lambda a: a.co2_footprint_g)
        if worst_activity.activity_type in ['Car', 'Bus']:
            suggestion = "You relied on fuel-based travel. Go for the **Bike** option next for a massive point boost!"
        elif worst_activity.activity_type == 'Beef':
            suggestion = "That high-carbon meal is stalling your rank! Log a **Vegan** meal next for triple bonus points."
    
    # Build response breakdown
    breakdown = {}
    for a in daily_activities:
        breakdown[a.category] = breakdown.get(a.category, 0) + a.co2_footprint_g

    return jsonify({
        "username": user.username,
        "total_co2_kg": round(total_co2_g / 1000, 2),
        "eco_points": user.total_eco_points,
        "current_streak": user.current_streak,
        "title": get_user_title(user.total_eco_points),
        "insight_suggestion": suggestion,
        "activity_breakdown": breakdown
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    # Simple leaderboard for the demo
    top_users = User.query.order_by(User.total_eco_points.desc()).limit(10).all()
    
    leaderboard_data = [{"rank": rank, "username": user.username, 
                         "points": user.total_eco_points, 
                         "title": get_user_title(user.total_eco_points)}
                        for rank, user in enumerate(top_users, 1)]
    return jsonify(leaderboard_data)


# --- 6. RUN THE SERVER ---
if __name__ == '__main__':
    app.run(debug=True)