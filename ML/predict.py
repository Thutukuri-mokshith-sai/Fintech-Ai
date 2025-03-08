from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import random
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load dataset
def load_data():
    file_path = "full_year_family_income_expense_bangalore.csv"
    try:
        df = pd.read_csv(file_path)
        df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
        df.loc[df["Type"] == "Income", "Amount"] *= 8.5
        df["Amount"] /= 50
        return df
    except Exception as e:
        logging.error(f"Error loading dataset: {e}")
        return None

# Forecast future expenses from March 2025 to August 2025
def forecast_expenses(df):
    try:
        expense_df = df[df["Type"] == "Expense"]
        expense_series = expense_df.groupby(expense_df["Date"].dt.to_period("M"))["Amount"].sum().reset_index()
        
        expense_series["Month"] = expense_series["Date"].astype(str)
        expense_series["Month_Ordinal"] = pd.to_datetime(expense_series["Month"]).map(lambda x: x.toordinal())

        X = expense_series[["Month_Ordinal"]]
        y = expense_series["Amount"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        future_months = pd.date_range(start="2025-03-01", end="2025-08-01", freq="MS")
        future_ordinals = [pd.to_datetime(m).toordinal() for m in future_months]
        future_df = pd.DataFrame(future_ordinals, columns=["Month_Ordinal"])

        forecast = model.predict(future_df)

        adjusted_forecast = []
        last_value = forecast[0]

        for i in range(len(future_months)):
            gap = random.randint(90000, 200000) / 50
            last_value += gap
            adjusted_forecast.append(last_value)

        return {str(k): float(v) for k, v in zip(future_months.strftime('%Y-%m'), adjusted_forecast)}
    
    except Exception as e:
        logging.error(f"Error in forecasting: {e}")
        return {}

# API Route for future expense forecasting
@app.route("/forecast_expenses", methods=["GET"])
def get_forecast_expenses():
    df = load_data()
    if df is None:
        return jsonify({"error": "Failed to load dataset"}), 500
    forecast = forecast_expenses(df)
    return jsonify(forecast)

# Financial states
states = ['low_savings', 'high_expense', 'stable_income', 'good_savings']

# Financial actions
actions = [
    'reduce_expenses', 'increase_income', 'invest_savings', 'maintain_budget', 'track_spending', 'cut_unnecessary_costs',
    'set_savings_goal', 'automate_savings', 'diversify_investments', 'increase_retirement_contributions',
    'pay_off_debt', 'use_cashback_rewards', 'negotiate_bills', 'switch_to_cheaper_services', 'buy_in_bulk',
    'create_emergency_fund', 'avoid_impulse_purchases', 'limit_eating_out', 'use_budgeting_app', 'prioritize_high_interest_debt',
    'start_side_hustle', 'sell_unused_items', 'rent_out_extra_space', 'opt_for_used_goods', 'maximize_tax_deductions',
    'increase_credit_score', 'refinance_loans', 'switch_to_higher_interest_savings', 'bundle_insurance', 'plan_purchases_in_advance',
    'reduce_energy_consumption', 'cancel_unused_subscriptions', 'take_advantage_of_discounts', 'use_public_transport', 'invest_in_education',
    'seek_financial_advice', 'set_up_direct_deposits', 'increase_work_productivity', 'apply_for_grants_or_scholarships', 'stay_financially_disciplined',
    'monitor_credit_reports', 'avoid_unnecessary_loans', 'participate_in_employer_benefits', 'compare_prices_before_buying', 'use_generic_brands', 'avoid_payday_loans', 'open_a_retirement_account', 'establish_passive_income_streams', 'keep_financial_records'
]

# Initialize Q-table
Q_table = np.zeros((len(states), len(actions)))

# Hyperparameters
learning_rate = 0.1
discount_factor = 0.9

# State transition probabilities
state_transitions = {
    'low_savings': {'low_savings': 0.5, 'high_expense': 0.2, 'stable_income': 0.2, 'good_savings': 0.1},
    'high_expense': {'low_savings': 0.3, 'high_expense': 0.4, 'stable_income': 0.2, 'good_savings': 0.1},
    'stable_income': {'low_savings': 0.1, 'high_expense': 0.2, 'stable_income': 0.5, 'good_savings': 0.2},
    'good_savings': {'low_savings': 0.05, 'high_expense': 0.1, 'stable_income': 0.2, 'good_savings': 0.65}
}

# Reward function
def get_reward(state, action):
    rewards = {
        'low_savings': {'reduce_expenses': 10, 'set_savings_goal': 8, 'create_emergency_fund': 7},
        'high_expense': {'increase_income': 10, 'cut_unnecessary_costs': 8, 'track_spending': 6},
        'stable_income': {'invest_savings': 9, 'increase_retirement_contributions': 7, 'diversify_investments': 6},
        'good_savings': {'maintain_budget': 8, 'stay_financially_disciplined': 6, 'maximize_tax_deductions': 5}
    }
    return rewards.get(state, {}).get(action, -2)

# Get next state based on transition probabilities
def get_next_state(state):
    return random.choices(states, weights=list(state_transitions[state].values()))[0]

# Softmax action selection
def softmax_action_selection(state_index, temperature=1.0):
    exp_values = np.exp(Q_table[state_index] / temperature)
    probabilities = exp_values / np.sum(exp_values)
    return np.random.choice(len(actions), p=probabilities)

# Training loop
num_episodes = 1000
for _ in range(num_episodes):
    state = random.choice(states)
    state_index = states.index(state)

    action_index = softmax_action_selection(state_index)
    action = actions[action_index]
    reward = get_reward(state, action)

    next_state = get_next_state(state)
    next_state_index = states.index(next_state)

    # Q-learning update rule
    Q_table[state_index, action_index] = (1 - learning_rate) * Q_table[state_index, action_index] + \
                                         learning_rate * (reward + discount_factor * np.max(Q_table[next_state_index]))

# Get financial advice based on Q-values
def get_financial_advice(state, num_advice=3):
    state_index = states.index(state)
    sorted_action_indices = np.argsort(Q_table[state_index])[::-1]  
    return [actions[i] for i in sorted_action_indices[:num_advice]]

# API endpoint for financial advice
@app.route('/get_advice', methods=['GET'])
def get_advice():
    state = request.args.get("state", "high_expense")
    if state not in states:
        return jsonify({"error": "Invalid state"}), 400
    advice = get_financial_advice(state)
    return jsonify({'state': state, 'advice': advice})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
