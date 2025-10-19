# carbon_data.py

# --- 1. CARBON COEFFICIENTS (in grams of CO2 equivalent per unit) ---
# These are the multipliers for your calculations.

CARBON_COEFFICIENTS = {
    # Transportation (per mile/km)
    'Car': 400,   # High impact per mile
    'Bus': 100,
    'Bike': 0,
    'Walk': 0,

    # Food (per meal/serving)
    'Beef': 3000, # Very high impact
    'Chicken': 1000,
    'Vegan': 200,

    # Energy/Digital (per kWh or per hour)
    # Average U.S. grid is ~400g CO2/kWh. We'll use 400 for electricity calculation.
    'Electricity_Daily_KWh': 400, 
    # Phone/Streaming/Gaming (per hour) - very low but good for demo
    'Digital_Hour': 50, 
}


# --- 2. GAMIFICATION LOGIC DATA ---
# These define points and achievement tiers.

# Points awarded for various actions
ECO_POINTS_AWARD = {
    'Bike': 50,
    'Walk': 50,
    'Vegan': 75,
    'Chicken': 25,
    'Car': 5,      # Still get a little for tracking!
    'Bus': 15,
    'Digital_Hour': 10,
}

# Tiers for Titles/Badges (based on total accumulated points)
ACHIEVEMENT_TIERS = {
    0: "New Earthling",
    100: "Bronze Eco-Racer",
    500: "Silver Earth Saver",
    2000: "Gold Climate Champion",
}