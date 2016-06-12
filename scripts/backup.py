#!/usr/bin/python

import os
import subprocess
import sys
from datetime import datetime

BACKUP_DIR = os.environ["BACKUP_DIR"]
DB_NAME = os.environ["DB_NAME"]
DB_PASS = os.environ["DB_PASS"]
DB_USER = os.environ["DB_USER"]
DB_HOST = os.environ["DB_HOST"]
MAIL_TO = os.environ.get("MAIL_TO")
MAIL_FROM = os.environ.get("MAIL_FROM")
WEBHOOK = os.environ.get("WEBHOOK")
WEBHOOK_METHOD = os.environ.get("WEBHOOK_METHOD") or "GET"

dt = datetime.now()
file_name = DB_NAME + "_" + dt.strftime("%Y-%m-%d")
backup_file = os.path.join(BACKUP_DIR, file_name)


def cmd(command):
    try:
        subprocess.check_output([command], shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        sys.stderr.write("\n".join([
            "Command execution failed. Output:",
            "-"*80,
            e.output,
            "-"*80,
            ""
        ]))
        raise

def backup_exists():
    return os.path.exists(backup_file)

def take_backup():
    #if backup_exists():
    #    sys.stderr.write("Backup file already exists!\n")
    #    sys.exit(1)
    
    # trigger postgres-backup
    cmd("env PGPASSWORD=%s pg_dump -Fc -h %s -U %s %s > %s" % (DB_PASS, DB_HOST, DB_USER, DB_NAME, backup_file))

def prune_local_backup_files():
    cmd("find %s -type f -prune -mtime +7 -exec rm -f {} \;" % BACKUP_DIR)

def send_email(to_address, from_address, subject, body):
    """
    Super simple, doesn't do any escaping
    """
    mail = """echo "From: %(from)s\r\nDate: $(date)\r\nSubject: %(subject)s\r\nMIME-Version: 1.0\r\nContent-Type: text/html; charset=utf-8\r\n\r\n%(body)s" | ssmtp %(to)s""" % {
        "to": to_address,
        "from": from_address,
        "subject": subject,
        "body": body,
    }
    cmd(mail)

def log(msg):
    print "[%s]: %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def main():
    start_time = datetime.now()

    log("Dumping database")
    take_backup()

    log("Pruning local backup copies")
    prune_local_backup_files()
    
    if MAIL_TO and MAIL_FROM:
        log("Sending mail to %s" % MAIL_TO)
        send_email(
            MAIL_TO,
            MAIL_FROM,
            "Backup complete: %s - %s " % (DB_NAME, file_name) ,
            "File generated: %s <br>Size: %s <br>Took %.2f seconds" % (
                backup_file, 
                sizeof_fmt(os.path.getsize(backup_file)),
                (datetime.now() - start_time).total_seconds()),
            )
    
    if WEBHOOK:
        log("Making HTTP %s request to webhook: %s" % (WEBHOOK_METHOD, WEBHOOK))
        cmd("curl -X %s %s" % (WEBHOOK_METHOD, WEBHOOK))
    
    log("Backup complete, took %.2f seconds" % (datetime.now() - start_time).total_seconds())


if __name__ == "__main__":
    main()