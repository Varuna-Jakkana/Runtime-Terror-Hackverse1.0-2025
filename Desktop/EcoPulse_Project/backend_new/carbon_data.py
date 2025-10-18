# carbon_data.py

# --- 1. CARBON COEFFICIENTS (in grams of CO2 equivalent per unit) ---
# Low CO2 = Low coefficient. High CO2 = High coefficient.
CARBON_COEFFICIENTS = {
    'Car': 400,
    'Bus': 100,
    'Bike': 0,
    'Vegan': 200,
    'Beef': 3000,
}


# --- 2. GAMIFICATION LOGIC DATA (Refined for Motivation) ---
# High points for low-impact (to reward the effort)
ECO_POINTS_AWARD = {
    'Bike': 100,
    'Bus': 50,
    'Vegan': 150,
    
    # Low points for high-impact (to discourage stagnation/cheating)
    'Car': 10,  
    'Beef': 15, 
}

# Tiers for Titles/Badges (based on total accumulated points)
ACHIEVEMENT_TIERS = {
    0: "New Earthling",
    500: "Bronze Eco-Racer",
    2000: "Silver Earth Saver",
    5000: "Gold Climate Champion",
}

# Threshold for triggering aggressive Insight/Suggestion (in grams)
HIGH_IMPACT_THRESHOLD_G = 1500