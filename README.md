# Telegram bot to remind birthdays
This is a simple telegram bot that send message when is someone birthday.

## Requirements
You need to create your own telegram bot
[[guide here](https://core.telegram.org/bots#3-how-do-i-create-a-bot)]
and know your chat ID [use [@userinfobot](https://telegram.me/userinfobot)].

## Install
Clone the repo
	
	git clone https://github.com/its-fonsy/birth-tg-bot.git

`cd` into it and install the requirements

	cd birth-tg-bot
	pip install -r requirements.txt

create the files to store the `token` of your bot, the `chat_id` of your profile and
the database with all the birthdays

	touch token chat_id bdays.dat

fill for each file the required information then start the bot

	python3 birth-tg-bot.py

## Database
The database has this format

	May 5 Henry Cavill
	June 1 Tom Holland
	June 9 Natalie Portman
	August 15 Jennifer Lawrence
	September 2 Keanu Reeves

**Important**: They must be ordered in month and day.

You can use the `bday.template` file to start adding your birthdays.

## Usage
Once the bot is running you can send with telegram this command to the bot:

- `\list` to list all the birthday of your database
- `\add` to add a birthday to your database
