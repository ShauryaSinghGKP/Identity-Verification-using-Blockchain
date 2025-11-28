from flask import Flask, render_template, request, jsonify
from blockchain import Blockchain
from hasher import hash_data
import re
import json
import os
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
USERS_FILE = "users.json"

def load_users():
    default_admins = {
        "gov": {"password": "secure_gov", "role": "admin", "org": "Ministry of Electronics"},
        "bank": {"password": "secure_bank", "role": "admin", "org": "Reserve Bank"},
        "ngo": {"password": "secure_ngo", "role": "admin", "org": "Civil Society"}
    }

    if not os.path.exists(USERS_FILE):
        save_users(default_admins)
        return default_admins
    
    try:
        with open(USERS_FILE, 'r') as f:
            data = json.load(f)
            for admin, details in default_admins.items():
                if admin not in data:
                    data[admin] = details
            return data
    except:
        return default_admins

def save_users(data):
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving DB: {e}")

users = load_users()
save_users(users) 
my_blockchain = Blockchain()

def validate_id_number(id_number):
    return bool(re.match(r"^\d{12}$", id_number))

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role_attempt = data.get('role')

    global users
    users = load_users()

    if username in users and users[username]['password'] == password:
        user_role = users[username]['role']
        
        if role_attempt != user_role:
             return jsonify({"status": "error", "message": f"Access Denied: You cannot login as {role_attempt}"}), 403

        user_data = {
            "username": username,
            "role": user_role,
            "aadhar": users[username].get('aadhar'),
            "status": users[username].get('status', 'none')
        }
        
        if user_role == 'admin':
            user_data['org'] = users[username].get('org', 'Unknown')
            
        return jsonify({"status": "success", "user": user_data})
    
    return jsonify({"status": "error", "message": "Invalid Credentials"}), 401

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    global users
    users = load_users() 
    
    if username in users:
        return jsonify({"status": "error", "message": "User already exists"}), 400
        
    users[username] = {
        "password": password, 
        "role": "user", 
        "aadhar": None, 
        "status": "none",
        "application_data": None 
    }
    save_users(users)
    
    return jsonify({"status": "success", "message": "Account created! Please login."})



@app.route('/register_aadhar', methods=['POST'])
def register_aadhar():
   
    if my_blockchain.is_chain_valid() != -1:
         return jsonify({"status": "error", "message": "SYSTEM HALTED: Blockchain compromised."}), 503

    data = request.json
    username = data.get('username')
    id_number = data.get('id_number')

    if not validate_id_number(id_number):
        return jsonify({"status": "error", "message": "Invalid Aadhar. Must be 12 digits."}), 400

    global users
    users = load_users()

    if users[username].get('aadhar'):
        return jsonify({"status": "error", "message": "You already have a registered ID."}), 409

    
    id_hash = hash_data(id_number)
    if my_blockchain.verify_identity(id_hash):
        return jsonify({"status": "error", "message": "This ID is already on the blockchain."}), 409

    
    users[username]['status'] = 'pending'
    users[username]['application_data'] = {
        "id_number": id_number,
        "hash": id_hash,
        "timestamp": str(my_blockchain.get_last_block()['timestamp']) 
    }
    save_users(users)
    
    return jsonify({"status": "success", "message": "Application Saved. Waiting for Admin."})



@app.route('/get_pending', methods=['GET'])
def get_pending():
    global users
    users = load_users()
    
    
    pending_list = []
    for uname, udata in users.items():
        if udata.get('status') == 'pending' and udata.get('application_data'):
            pending_list.append({
                "username": uname,
                "id_number": udata['application_data']['id_number'],
                "hash": udata['application_data']['hash']
            })
            
    return jsonify(pending_list)

@app.route('/approve_request', methods=['POST'])
def approve_request():
    if my_blockchain.is_chain_valid() != -1:
         return jsonify({"status": "error", "message": "System compromised. Approvals disabled."}), 503

    data = request.json
    username = data.get('username')
    
    global users
    users = load_users()
    
    user = users.get(username)
    if not user or user['status'] != 'pending':
        return jsonify({"status": "error", "message": "Request invalid or not found"}), 404

    
    app_data = user['application_data']
    my_blockchain.add_block(app_data['hash'])
    
    
    users[username]['aadhar'] = app_data['id_number']
    users[username]['status'] = 'approved'
    users[username]['application_data'] = None 
    save_users(users)

    return jsonify({"status": "success", "message": "Identity Minted to Blockchain."})

@app.route('/chain_data', methods=['GET'])
def chain_data():
    validity = my_blockchain.is_chain_valid()
    return jsonify({
        "chain": my_blockchain.blockchain,
        "is_valid": validity == -1,
        "tampered_block_index": validity if validity != -1 else None
    })

@app.route('/repair', methods=['POST'])
def repair():
    my_blockchain.repair_chain()
    return jsonify({"status": "success", "message": "Blockchain Repaired."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)