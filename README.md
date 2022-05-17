# telegram_reg_bot

To use this bot you need:
1. Install Postgres on your server, create database and create table:
```
# create table <table_name> (
#    name text,
#    contact text,
#    company text,
#    rank text,
#    region text,
#    created timestamp DEFAULT current_timestamp
#);
```
2. Copy and set database cridentials and table name into the correspondent variables in the source code;
3. Install python environment on your server and download these packages via pip3:
```
pyTelegramBotAPI==4.4.1
psycopg2==2.9.3
```
4. Create Telegram Bot via Botfather and get its token;
5. Set this token into the source code and have fun!

Or use some Cloud Hosting Solutions like Heroku or others. For instance, the bot perfectly works on Heroku.
