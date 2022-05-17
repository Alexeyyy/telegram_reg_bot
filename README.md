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

Or use some Cloud Hosting Solutions like Heroku or others. For instance, the bot perfectly works on Heroku (procfile and the article how to tune Heroku server are included in the files and the source code).

FYI: The bot can store data either in database and raw file. The first approach is more applicable, especially when some cloud hostings are used. The most cloud solutions have the feature of killing and restore instances time to time ==> it causes the flush of the raw file because the fresh instance takes the raw file.
