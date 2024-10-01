import re
import string
import json
import os

# File to store user data
USER_DATA_FILE = 'users_data.json'

# Load existing user data from JSON file
def load_users_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save user data to JSON file
def save_users_data(users_db):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users_db, file, indent=4)

# Helper functions for Registration and Login
def is_valid_username(username):
    return len(username) >= 6

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[@$!%*?&]', password):
        return False
    return True

def register_user(users_db):
    while True:
        username = input("Enter username (at least 6 characters): ")
        if not is_valid_username(username):
            print("Username must be at least 6 characters.")
            continue

        password = input("Enter password (at least 8 characters, including letters, numbers, and special characters): ")
        if not is_valid_password(password):
            print("Password must be at least 8 characters with letters, numbers, and special characters.")
            continue

        users_db[username] = {
            'password': password,
            'attempts': 0,
            'log': []
        }
        save_users_data(users_db)
        print("User registered successfully!")
        break

def login_user(users_db):
    attempts_limit = 3
    while True:
        username = input("Enter username: ")
        if username not in users_db:
            print("User not found. Please register.")
            return None

        user_data = users_db[username]
        if user_data['attempts'] >= attempts_limit:
            print("Account blocked after 3 wrong attempts.")
            if restore_account(users_db, username):
                return username
            return None

        password = input("Enter password: ")
        if password == user_data['password']:
            print("Login successful!")
            return username
        else:
            user_data['attempts'] += 1
            save_users_data(users_db)
            print(f"Wrong password! Attempts left: {attempts_limit - user_data['attempts']}")
            if user_data['attempts'] >= attempts_limit:
                print("Account blocked after 3 wrong attempts.")
                return None

def restore_account(users_db, username):
    print("Would you like to restore your blocked account? (y/n)")
    if input().lower() == 'y':
        password = input("Enter your password to restore your account: ")
        if password == users_db[username]['password']:
            users_db[username]['attempts'] = 0  # Reset attempts
            save_users_data(users_db)
            print("Account restored successfully!")
            return True
        else:
            print("Incorrect password. Unable to restore account.")
            return False
    return False

# Cipher Functions
def atbash_cipher(text):
    alphabet = string.ascii_lowercase
    reversed_alphabet = alphabet[::-1]
    atbash_table = str.maketrans(alphabet + alphabet.upper(), reversed_alphabet + reversed_alphabet.upper())
    return text.translate(atbash_table)

def caesar_cipher(text, shift, decrypt=False):
    if decrypt:
        shift = -shift
    result = []
    for char in text:
        if char.isalpha():
            shift_amount = 65 if char.isupper() else 97
            result.append(chr((ord(char) - shift_amount + shift) % 26 + shift_amount))
        else:
            result.append(char)
    return ''.join(result)

def vigenere_cipher(text, key, decrypt=False):
    result = []
    key = key.lower()
    key_len = len(key)
    key_as_int = [ord(i) - ord('a') for i in key]
    for i, char in enumerate(text):
        if char.isalpha():
            shift = key_as_int[i % key_len]
            shift = -shift if decrypt else shift
            shift_amount = 65 if char.isupper() else 97
            result.append(chr((ord(char) - shift_amount + shift) % 26 + shift_amount))
        else:
            result.append(char)
    return ''.join(result)

# Log encryption and decryption to the user's data in JSON
def log_activity(users_db, username, action, original_text, result_text, cipher_type):
    log_entry = {
        'action': action,
        'cipher_type': cipher_type,
        'original_text': original_text,
        'result_text': result_text
    }
    users_db[username]['log'].append(log_entry)
    save_users_data(users_db)

def cipher_menu(users_db, username):
    print("\nAvailable Ciphers:")
    print("1. Atbash Cipher")
    print("2. Caesar Cipher")
    print("3. Vigenère Cipher")
    choice = input("Choose a cipher (1/2/3): ")

    text = input("Enter text: ")
    if choice == '1':
        encrypted = atbash_cipher(text)
        print("Encrypted Text (Atbash):", encrypted)
        log_activity(users_db, username, "Encrypt", text, encrypted, "Atbash")
    elif choice == '2':
        shift = int(input("Enter shift value for Caesar Cipher (Number Only): "))
        encrypted = caesar_cipher(text, shift)
        print("Encrypted Text (Caesar):", encrypted)
        log_activity(users_db, username, "Encrypt", text, encrypted, "Caesar")
        if input("Do you want to decrypt it? (y/n): ") == 'y':
            decrypted = caesar_cipher(encrypted, shift, decrypt=True)
            print("Decrypted Text:", decrypted)
            log_activity(users_db, username, "Decrypt", encrypted, decrypted, "Caesar")
    elif choice == '3':
        key = input("Enter key for Vigenère Cipher: ")
        encrypted = vigenere_cipher(text, key)
        print("Encrypted Text (Vigenère):", encrypted)
        log_activity(users_db, username, "Encrypt", text, encrypted, "Vigenère")
        if input("Do you want to decrypt it? (y/n): ") == 'y':
            decrypted = vigenere_cipher(encrypted, key, decrypt=True)
            print("Decrypted Text:", decrypted)
            log_activity(users_db, username, "Decrypt", encrypted, decrypted, "Vigenère")
    else:
        print("Invalid choice. Exiting.")

# Main flow
def main():
    users_db = load_users_data()

    print("Welcome to the Cipher Application!")
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        option = input("Choose an option (1/2/3): ")
        if option == '1':
            register_user(users_db)
        elif option == '2':
            user = login_user(users_db)
            if user:
                cipher_menu(users_db, user)
        elif option == '3':
            print("Exiting the application.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
