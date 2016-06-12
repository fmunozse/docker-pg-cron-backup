#!/bin/bash
set -e

if [ -z "$CRON_SCHEDULE" ]; then
    echo "WARNING: CRON_SCHEDULE not set!"
fi

# Write cron schedule
echo "#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
$CRON_SCHEDULE root . /backup/backups.sh >> /backup.log 2>&1
" > /etc/cron.d/postgresql-backup

# Write ssmtp configuration
echo "
root=$MAIL_GMAIL_USER
mailhub=smtp.gmail.com:587
AuthUser=$MAIL_GMAIL_USER
AuthPass=$MAIL_GMAIL_PWD
UseTLS=YES
UseSTARTTLS=YES
FromLineOverride=YES
#hostname=$MAIL_FROM
" > /etc/ssmtp/ssmtp.conf

echo "
root:$MAIL_GMAIL_USER:smtp.gmail.com:587
" > /etc/ssmtp/revaliases

# Env variables that can be imported from backup script, 
# since cron jobs doesn't get the environment set
echo "#!/bin/bash
export BACKUP_DIR=$BACKUP_DIR
export DB_NAME=$DB_NAME
export DB_PASS=$DB_PASS
export DB_USER=$DB_USER
export DB_HOST=$DB_HOST
export MAIL_TO=$MAIL_TO
export MAIL_FROM=$MAIL_FROM
export MAIL_GMAIL_USER=$MAIL_GMAIL_USER
export MAIL_GMAIL_PWD=$MAIL_GMAIL_PWD
export WEBHOOK=$WEBHOOK
export WEBHOOK_METHOD=$WEBHOOK_METHOD
" > /env.sh
chmod +x /env.sh

echo "Start script running with these environment options"
cat /env.sh

exec "$@"