import tkinter as tk
from gui import Application
from encryption import save_encrypted_data
import logging

def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

    data = {
        "pat": app.shared_pat,
        "org_url": app.shared_org_url,
        "projects": app.projects
    }

    try:
        save_encrypted_data(data)
        logging.info("Encrypted data has been saved.")
    except Exception as e:
        logging.error(
            "Error occurred while saving the encrypted data: " + str(e))


if __name__ == '__main__':
    main()
