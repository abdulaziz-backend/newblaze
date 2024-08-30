import json
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATABASE_FILE = 'data.txt'

def ensure_file_exists():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as file:
            json.dump({}, file, indent=4)

def load_users():
    ensure_file_exists()
    try:
        with open(DATABASE_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}

def save_users(users_data):
    ensure_file_exists()
    with open(DATABASE_FILE, 'w') as file:
        try:
            print(f"Saving users data: {json.dumps(users_data, ensure_ascii=False)}")  # Handle non-ASCII characters
        except UnicodeEncodeError:
            print("Saving user data (Unicode characters skipped).")
        json.dump(users_data, file, indent=4)

def get_user(user_id):
    users_data = load_users()
    return users_data.get(str(user_id))

def add_user(user_id, username, name):
    users_data = load_users()
    user_id_str = str(user_id)
    if user_id_str not in users_data:
        users_data[user_id_str] = {
            'user_id': user_id,
            'username': username,
            'name': name,
            'amount': 0,
            'invited_friends': 0,
            'invited_friends_usernames': []
        }
        print(f"Adding user: {users_data[user_id_str]}")  
        save_users(users_data)
    else:
        print(f"User {user_id} already exists.")  

def update_user(user_id, **kwargs):
    users_data = load_users()
    user_id_str = str(user_id)
    if user_id_str in users_data:
        users_data[user_id_str].update(kwargs)
        print(f"Updating user: {users_data[user_id_str]}")  
        save_users(users_data)


