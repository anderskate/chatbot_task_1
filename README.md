# Chat bot for task check notifications

A bot is useful for [Devman](https://dvmn.org/modules/) students. It sends you notification in Telegram chat if the task is verified. 

The bot uses [Devman API](https://dvmn.org/api/docs/) and [python-telegram-bot](https://pypi.org/project/python-telegram-bot/).

# How to install
The script uses enviroment file with Devman and Telegram authorization data. The file '.env' must include following data:
- DEVMAN_USER_TOKEN, individual token of Devman API
- TELEGRAM_TOKEN, Telegram bot token
- TG_CHAT_ID, an ID of a Telegram user who get the notification
- TG_ADMIN_CHAT_ID, an ID of bot administrator in Telegram to send logging notifications

Python 3 should be already installed. Then use pip3 (or pip) to install dependencies:

```bash
pip3 install -r requirements.txt
```

# How to launch
The Example of launch in Ubuntu is:

```bash
$ python3 main.py 
```

It is better to launch the script on a remote server, [Heroku](https://devcenter.heroku.com/articles/how-heroku-works), for example. It provides that it will work around the clock. A "Procfile" is need to launch correctly on Heroku.

# Project Goals

The code is written for educational purposes on online-course for web-developers dvmn.org, module [Chat Bots with Python](https://dvmn.org/modules/chat-bots/lesson/devman-bot/#review-tabs).
