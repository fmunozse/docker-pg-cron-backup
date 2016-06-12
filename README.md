# pg-cron-backup

## Description
This docker basically is a cron trigger to perform backups of a postgresql ddbb.  It has been done from 
[heyman/docker-postgres-backup](https://github.com/heyman/docker-postgres-backup)

The image is generated from `FROM postgres:9.5.1`

The backup is manage by a phyton script backup.py and the backup is done in several steps:

1. dump of ddbb ...  
```python
env PGPASSWORD=%s pg_dump -Fc -h %s -U %s %s > %s" % (DB_PASS, DB_HOST, DB_USER, DB_NAME, backup_file))
```
2. prune the old backups
```python
"find %s -type f -prune -mtime +7 -exec rm -f {} \;" % BACKUP_DIR
```
3. Send notification mail in case is set up.  The email contains the name of file, size and time take it.
4. Call to a webhook in case that is set up.


## Volumn expose
This docker expose the volumn `/data/backups/` folder where is located the backups done. 

## Environment

Variables to can set up for the docker.

| environment variables | Example 						| Description 						| 
| --------------------- | ------- 						| ----------- 						|
| DB_HOST				| 11.222.333.444				| Host where is located the ddbb    |
| DB_NAME 				| postgres						| Name of ddbb 						|
| DB_USER				| myUser						| ddbb User   						|
| DB_PASS				| myPassword					| ddbb Password						|
| CRON_SCHEDULE			| 0 23 * * * 					| cron set up (example everyDay 23:00)|
| MAIL_GMAIL_USER		| myUser@gmail.com 				| Optional: gmail User				|
| MAIL_GMAIL_PWD		| myPwdGmail	 				| Optional: gmail Password 			|
| MAIL_TO				| myAccount@gmail.com 			| Optional: destination when is done the backup |
| MAIL_FROM				| myAccount@gmail.com 			| Optional: from  					|
| WEBHOOK				| http://xxxx.xxx.xx/aaa 		| Optional: web hook when is done the backup 	|
| WEBHOOK_METHOD		| GET 							| Optional: method to call web hook  |


## Run 

### Using docker-compose

Command line:
` docker-compose up `

Example of the configuration:
```yaml
version: '2'
services:
    postgresql-backup:
        container_name: postgresql-backup
        image: fmunozse/pg-cron-backups
        volumes:
          - ~/volumes/postgresql_backups/:/data/backups/
        environment:
          - DB_HOST=11.222.333.444
          - DB_NAME=postgres
          - DB_USER=myUser
          - DB_PASS=myPassword
          - CRON_SCHEDULE=0 23 * * *
          - MAIL_GMAIL_USER=myUser@gmail.com
          - MAIL_GMAIL_PWD=myPassword
          - MAIL_TO=myUser@gmail.com
          - MAIL_FROM=myUser@gmail.com

```

### Others commands useful

Access to inside of docker:
`docker exec -it postgresql-backup  bash`

Build the image:
`docker build -t fmunozse/pg-cron-backups .`   or just run `build.sh`

Stop the docker-compose:
` docker-compose stop `



## Issue in case gmail
In case that you have this issue during the email notification
```
send-mail: Authorization failed (534 5.7.14 https://support.google.com/mail/bin/answer.py?answer=78754 ni5sm3908366pbc.83 - gsmtp)
```

See this http://serverfault.com/questions/635139/how-to-fix-send-mail-authorization-failed-534-5-7-14

