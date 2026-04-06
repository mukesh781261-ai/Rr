import requests
import json
import os

# --- CONFIGURATION ---
JWT_API_URL = "https://only-jwt.vercel.app/token"
GUEST_FILE = "Guest.json"
TOKEN_FILE = "token_ind.json"
VISIT_FILE = "token_ind_visit.json"

def get_new_jwt(uid, password):
    """Calls the external JWT Giver API."""
    try:
        res = requests.get(JWT_API_URL, params={"uid": uid, "password": password}, timeout=10)
        if res.status_code == 200:
            return res.json().get("token")
    except Exception as e:
        print(f"JWT API Error: {e}")
    return None

def update_local_storage(uid, new_token):
    """Updates both JSON files with the fresh token."""
    try:
        # 1. Update token_ind.json
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                data = json.load(f)
            for item in data:
                if str(item['uid']) == str(uid):
                    item['token'] = new_token
            with open(TOKEN_FILE, 'w') as f:
                json.dump(data, f, indent=4)

        # 2. Update token_ind_visit.json (Visitor/Checker)
        # Assuming this file stores the most recent active token
        visit_data = [{"uid": str(uid), "token": new_token}]
        with open(VISIT_FILE, 'w') as f:
            json.dump(visit_data, f, indent=4)
            
        return True
    except Exception as e:
        print(f"File Update Error: {e}")
        return False

def handle_auto_refresh(uid, password):
    """The main function to fix an expired account."""
    print(f"🔄 Refreshing account {uid}...")
    new_token = get_new_jwt(uid, password)
    
    if new_token:
        if update_local_storage(uid, new_token):
            print(f"✅ Account {uid} is now ACTIVE and files are synced.")
            return new_token
    return None
