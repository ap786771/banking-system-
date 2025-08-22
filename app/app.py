from flask import Flask, jsonify, request
from app.models import load_data, save_data
from datetime import datetime
import uuid

app = Flask(__name__)
data = load_data()

# Home route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Banking System API"}), 200

# Create new account
@app.route('/create_account', methods=['POST'])
def create_account():
    name = request.json.get('name')
    balance = request.json.get('balance', 0)
    if not name:
        return jsonify({"error": "Name is required"}), 400

    account_id = str(uuid.uuid4())[:8]  # Short UUID for simplicity
    data["accounts"][account_id] = {
        "name": name,
        "balance": balance,
        "transactions": [
            {
                "type": "deposit",
                "amount": balance,
                "time": str(datetime.now())
            }
        ] if balance > 0 else []
    }
    save_data(data)
    return jsonify({"account_id": account_id, "message": "Account created successfully"}), 201

# Deposit money
@app.route('/deposit', methods=['POST'])
def deposit():
    account_id = request.json.get('account_id')
    amount = request.json.get('amount', 0)
    if account_id not in data["accounts"]:
        return jsonify({"error": "Account not found"}), 404
    if amount <= 0:
        return jsonify({"error": "Deposit amount must be positive"}), 400

    data["accounts"][account_id]["balance"] += amount
    data["accounts"][account_id]["transactions"].append({
        "type": "deposit",
        "amount": amount,
        "time": str(datetime.now())
    })
    save_data(data)
    return jsonify({"balance": data["accounts"][account_id]["balance"]}), 200

# Withdraw money
@app.route('/withdraw', methods=['POST'])
def withdraw():
    account_id = request.json.get('account_id')
    amount = request.json.get('amount', 0)
    if account_id not in data["accounts"]:
        return jsonify({"error": "Account not found"}), 404
    if amount <= 0:
        return jsonify({"error": "Withdrawal amount must be positive"}), 400
    if data["accounts"][account_id]["balance"] < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    data["accounts"][account_id]["balance"] -= amount
    data["accounts"][account_id]["transactions"].append({
        "type": "withdraw",
        "amount": amount,
        "time": str(datetime.now())
    })
    save_data(data)
    return jsonify({"balance": data["accounts"][account_id]["balance"]}), 200

# Transfer money between accounts
@app.route('/transfer', methods=['POST'])
def transfer():
    from_id = request.json.get('from_account')
    to_id = request.json.get('to_account')
    amount = request.json.get('amount', 0)

    if from_id not in data["accounts"] or to_id not in data["accounts"]:
        return jsonify({"error": "One or both accounts not found"}), 404
    if amount <= 0:
        return jsonify({"error": "Transfer amount must be positive"}), 400
    if data["accounts"][from_id]["balance"] < amount:
        return jsonify({"error": "Insufficient funds in sender account"}), 400

    data["accounts"][from_id]["balance"] -= amount
    data["accounts"][to_id]["balance"] += amount
    now = str(datetime.now())
    data["accounts"][from_id]["transactions"].append({
        "type": "transfer_out",
        "amount": amount,
        "to": to_id,
        "time": now
    })
    data["accounts"][to_id]["transactions"].append({
        "type": "transfer_in",
        "amount": amount,
        "from": from_id,
        "time": now
    })
    save_data(data)
    return jsonify({"message": "Transfer successful"}), 200

# Get account details
@app.route('/account/<account_id>', methods=['GET'])
def get_account(account_id):
    if account_id not in data["accounts"]:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(data["accounts"][account_id]), 200

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "UP"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
