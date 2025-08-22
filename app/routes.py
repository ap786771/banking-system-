from flask import request, jsonify
from app import app
from app.models import load_data, save_data
import uuid
from datetime import datetime

data = load_data()

@app.route("/create_account", methods=["POST"])
def create_account():
    name = request.json.get("name")
    balance = request.json.get("balance", 0)
    account_id = str(uuid.uuid4())
    data["accounts"][account_id] = {
        "name": name,
        "balance": balance,
        "transactions": []
    }
    save_data(data)
    return jsonify({"account_id": account_id, "message": "Account created successfully"})

@app.route("/deposit", methods=["POST"])
def deposit():
    account_id = request.json.get("account_id")
    amount = request.json.get("amount", 0)
    if account_id in data["accounts"]:
        data["accounts"][account_id]["balance"] += amount
        data["accounts"][account_id]["transactions"].append({
            "type": "deposit",
            "amount": amount,
            "time": str(datetime.now())
        })
        save_data(data)
        return jsonify({"balance": data["accounts"][account_id]["balance"]})
    return jsonify({"error": "Account not found"}), 404

@app.route("/withdraw", methods=["POST"])
def withdraw():
    account_id = request.json.get("account_id")
    amount = request.json.get("amount", 0)
    if account_id in data["accounts"]:
        if data["accounts"][account_id]["balance"] >= amount:
            data["accounts"][account_id]["balance"] -= amount
            data["accounts"][account_id]["transactions"].append({
                "type": "withdraw",
                "amount": amount,
                "time": str(datetime.now())
            })
            save_data(data)
            return jsonify({"balance": data["accounts"][account_id]["balance"]})
        return jsonify({"error": "Insufficient funds"}), 400
    return jsonify({"error": "Account not found"}), 404

@app.route("/transfer", methods=["POST"])
def transfer():
    from_id = request.json.get("from_account")
    to_id = request.json.get("to_account")
    amount = request.json.get("amount", 0)
    if from_id in data["accounts"] and to_id in data["accounts"]:
        if data["accounts"][from_id]["balance"] >= amount:
            data["accounts"][from_id]["balance"] -= amount
            data["accounts"][to_id]["balance"] += amount
            now = str(datetime.now())
            data["accounts"][from_id]["transactions"].append({"type": "transfer_out", "amount": amount, "to": to_id, "time": now})
            data["accounts"][to_id]["transactions"].append({"type": "transfer_in", "amount": amount, "from": from_id, "time": now})
            save_data(data)
            return jsonify({"message": "Transfer successful"})
        return jsonify({"error": "Insufficient funds"}), 400
    return jsonify({"error": "Account not found"}), 404

@app.route("/account/<account_id>", methods=["GET"])
def get_account(account_id):
    if account_id in data["accounts"]:
        return jsonify(data["accounts"][account_id])
    return jsonify({"error": "Account not found"}), 404
