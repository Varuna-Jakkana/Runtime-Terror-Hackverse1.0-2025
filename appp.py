# app.py

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from carbon_data import CARBON_COEFFICIENTS, ECO_POINTS_AWARD, ACHIEVEMENT_TIERS

# --- 1. APP CONFIGURATION ---
app = Flask(__name__)
# Configure the SQLite database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecotrack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 2. DATABASE MODELS (Tables) ---

class User(db.Model):
    """Stores user stats for Gamification and Leaderboard."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    
    # Gamification Fields
    total_eco_points = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    last_login = db.Column(db.Date, default=date.today())

    # Relationship to activities
    activities = db.relationship('ActivityLog', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class ActivityLog(db.Model):
    """Stores every tracked action and its calculated carbon footprint."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Activity Data
    category = db.Column(db.String(50), nullable=False) # e.g., 'Transport', 'Food'
    activity_type = db.Column(db.String(50), nullable=False) # e.g., 'Car', 'Beef', 'Electricity_Daily_KWh'
    input_value = db.Column(db.Float, nullable=False) # e.g., 5.0 (miles), 1.0 (meal), 230.0 (kWh)

    # Output Data
    co2_footprint_g = db.Column(db.Integer, default=0)
    eco_points_earned = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Activity {self.category}/{self.activity_type}>'

# --- 3. HELPER FUNCTIONS (The Core Logic) ---

def get_user_title(points):
    """Determines the user's title based on total points."""
    title = ACHIEVEMENT_TIERS[0]
    # Find the highest tier the user qualifies for
    for tier_points, tier_title in sorted(ACHIEVEMENT_TIERS.items(), reverse=True):
        if points >= tier_points:
            title = tier_title
            break
    return title

def calculate_co2_and_points(activity_type, input_value):
    """Calculates carbon footprint and eco points for a given activity."""
    
    # Get the carbon coefficient (in g CO2 per unit)
    coefficient = CARBON_COEFFICIENTS.get(activity_type)
    
    if not coefficient:
        return 0, 0 # Return 0 if the activity type is unknown

    # Calculate CO2 footprint (in grams)
    if activity_type == 'Electricity_Daily_KWh':
        # Calculate daily CO2 for monthly input (assuming input_value is monthly kWh)
        # Monthly CO2 = input_value * coefficient. Daily CO2 = Monthly CO2 / 30
        co2_g = int((input_value * coefficient) / 30)
    else:
        # Standard calculation (e.g., miles * coefficient)
        co2_g = int(input_value * coefficient)

    # Determine eco points
    points = ECO_POINTS_AWARD.get(activity_type, 0)
    
    # Scale points for digital activities based on hours, otherwise fixed per entry
    if activity_type in ['Digital_Hour']:
        points = int(points * input_value)
    
    return co2_g, points

# --- 4. DATABASE INITIALIZATION ---

@app.cli.command("init-db")
def init_db():
    """Command to initialize (create) the database tables and add a dummy user."""
    with app.app_context():
        db.create_all()
        print("Database tables created.")
        
        # Add a dummy user for testing
        if not User.query.filter_by(username='demo_user').first():
            demo_user = User(username='demo_user', total_eco_points=50, current_streak=1)
            db.session.add(demo_user)
            db.session.commit()
            print("Demo user 'demo_user' added.")

# --- 5. RUN THE SERVER ---

if __name__ == '__main__':
    # You must run 'flask init-db' in the terminal once to create the database file!
    app.run(debug=True)
# --- 6. API ENDPOINTS (Tracking) ---

@app.route('/api/track/<int:user_id>', methods=['POST'])
def track_activity(user_id):
    """Handles POST requests to log a new user activity."""
    data = request.get_json()
    
    # 1. Input Validation
    if not data or not all(key in data for key in ['category', 'type', 'value']):
        return jsonify({"error": "Invalid input data"}), 400

    category = data['category']
    activity_type = data['type']
    input_value = data['value']
    
    # Check if user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 2. Calculation
    co2_g, points = calculate_co2_and_points(activity_type, input_value)

    # 3. Create and Save Activity Log
    new_activity = ActivityLog(
        user_id=user_id,
        category=category,
        activity_type=activity_type,
        input_value=input_value,
        co2_footprint_g=co2_g,
        eco_points_earned=points
    )

    # 4. Update User Stats (Simplified Streak Logic)
    user.total_eco_points += points
    
    today = date.today()
    if user.last_login < today:
        if user.last_login == today - timedelta(days=1):
            user.current_streak += 1
        else:
            user.current_streak = 1
        user.last_login = today


    db.session.add(new_activity)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Activity logged. CO2: {co2_g}g, Points: {points}",
        "co2_g": co2_g,
        "new_total_points": user.total_eco_points
    }), 201
# --- 7. API ENDPOINTS (Summary and Insights) ---

@app.route('/api/summary/<int:user_id>', methods=['GET'])
def get_user_summary(user_id):
    """Returns the user's total daily footprint, stats, and suggestion."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Correctly filter activities for the current day
    today_start = datetime.combine(date.today(), datetime.min.time())
    
    daily_activities = ActivityLog.query.filter(
        ActivityLog.user_id == user_id,
        ActivityLog.timestamp >= today_start
    ).all()
    
    total_co2_g = sum(a.co2_footprint_g for a in daily_activities)
    
    # Simple Insight/Suggestion Logic (same as previous plan)
    suggestion = "Keep up the great work today!"
    high_impact_activities = [a for a in daily_activities if a.co2_footprint_g > 1500]
    if high_impact_activities:
        worst_activity = max(high_impact_activities, key=lambda a: a.co2_footprint_g)
        if worst_activity.activity_type in ['Car', 'Bus']:
            suggestion = "Your travel footprint is high. Try to bike or walk for your next short trip!"
        elif worst_activity.activity_type == 'Beef':
            suggestion = "That Beef meal had a big impact! Try a Vegan option for dinner to balance it out."
    
    # Breakdown by category for frontend charts
    breakdown = {}
    for a in daily_activities:
        breakdown[a.category] = breakdown.get(a.category, 0) + a.co2_footprint_g

    return jsonify({
        "username": user.username,
        "total_co2_kg": round(total_co2_g / 1000, 2), # Convert grams to KG
        "eco_points": user.total_eco_points,
        "current_streak": user.current_streak,
        "title": get_user_title(user.total_eco_points),
        "insight_suggestion": suggestion,
        "activity_breakdown": breakdown
    })
# --- 8. API ENDPOINTS (Gamification) ---

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Returns the top users sorted by total eco points."""
    top_users = User.query.order_by(User.total_eco_points.desc()).limit(10).all()
    
    leaderboard_data = []
    for rank, user in enumerate(top_users, 1):
        leaderboard_data.append({
            "rank": rank,
            "username": user.username,
            "points": user.total_eco_points,
            "title": get_user_title(user.total_eco_points)
        })
        
    return jsonify(leaderboard_data)