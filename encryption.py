import json
from logging.handlers import RotatingFileHandler
import os
import logging
from cryptography.fernet import Fernet, InvalidToken

KEY_FILE_PATH = os.path.join(os.getenv('APPDATA'), 'ReleaseNotes', 'key.key')
DATA_FILE_PATH = os.path.join(os.getenv('APPDATA'), 'ReleaseNotes', 'data.bin')


# Create the directory for your files, if it doesn't already exist
os.makedirs(os.path.join(os.getenv('APPDATA'), 'ReleaseNotes'), exist_ok=True)

log_file = os.path.join(os.getenv('APPDATA'), 'ReleaseNotes', 'app.log')

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a rotating file handler
handler = RotatingFileHandler(log_file, maxBytes=5000, backupCount=5)

# Create a logging format
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


def create_key():
    key = Fernet.generate_key()
    with open(KEY_FILE_PATH, 'wb') as key_file:
        key_file.write(key)


def load_key():
    try:
        with open(KEY_FILE_PATH, 'rb') as key_file:
            return key_file.read()
    except FileNotFoundError:
        logging.info("Key file not found. Creating new key...")
        create_key()  # Generate a new key if the key file does not exist
        with open(KEY_FILE_PATH, 'rb') as key_file:  # Try to read the key file again
            return key_file.read()
    except Exception as e:
        logging.error("Error occurred while loading the key: " + str(e))
    return None


def save_encrypted_data(data):
    key = load_key()
    if key:
        f = Fernet(key)
        encrypted_data = f.encrypt(json.dumps(data).encode())
        try:
            with open(DATA_FILE_PATH, 'wb') as data_file:
                data_file.write(encrypted_data)
            logging.info("Data has been written to the file.")
        except Exception as e:
            logging.error(
                "Error occurred while writing the data file: " + str(e))


def load_decrypted_data():
    try:
        with open(DATA_FILE_PATH, "rb") as f:
            data = f.read()
            key = load_key()
            if data and key:
                fernet = Fernet(key)
                decrypted_data = fernet.decrypt(data)
                return json.loads(decrypted_data.decode())
    except FileNotFoundError:
        logging.error("Data file not found.")
    except InvalidToken:
        logging.error("Invalid key or data file.")
    except Exception as e:
        logging.error(
            "Error occurred while loading the decrypted data: " + str(e))
    return {}


def delete_files():
    try:
        # Close log file if it's open
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()

        # Close encrypted data file if it's open
        with open(DATA_FILE_PATH, 'a') as f:
            f.close()

        # Close key file if it's open
        with open(KEY_FILE_PATH, 'a') as f:
            f.close()

        # Delete the encrypted data file
        if os.path.isfile(DATA_FILE_PATH):
            os.remove(DATA_FILE_PATH)
            logging.info("Encrypted data file deleted.")

        # Delete the key file
        if os.path.isfile(KEY_FILE_PATH):
            os.remove(KEY_FILE_PATH)
            logging.info("Key file deleted.")
    except Exception as e:
        logging.error("Error occurred while deleting files: " + str(e))
