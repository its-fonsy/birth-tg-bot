#!/usr/bin/env python3

import datetime
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

BIRTHDAYS_DATABASE = "bday.dat"

with open("token", "r") as token_file:
    TOKEN = token_file.read().strip()

with open("chat_id", "r") as id_file:
    CHAT_ID = int(id_file.read().strip())

month_conv = { 'January'   : 1,
               'February'  : 2,
               'March'     : 3,
               'April'     : 4,
               'May'       : 5,
               'June'      : 6,
               'July'      : 7,
               'August'    : 8,
               'September' : 9,
               'October'   : 10,
               'November'  : 11,
               'December'  : 12 }

MONTH, DAY, NAME, RECAP, CONFIRM = range(5)

def check_birthday():
    # get current day and month
    now = datetime.datetime.now()
    current_day = now.day
    current_month = now.month

    # list the birthdays of today
    birthday_list = []

    with open(BIRTHDAYS_DATABASE, 'r') as birth_file:
        for line in birth_file:
            month, day, name, surname = line.split(' ')
            day   = int(day)
            month = month_conv[month]

            if (current_day == day) and (current_month == month):
                birthday_list.append([name, surname.strip()])

    return birthday_list


def birthday_message(birthday_list):
    for person in birthday_list:
        name = person[0]
        surname = person[1]
        message = f"Today is the birthday of {name} {surname}!"
        print(message)


def add_birthday(month, day, name, surname):

    with open(BIRTHDAYS_DATABASE, 'r') as birth_file:
        old = birth_file.read()

    # convert month from number to text
    month_number = month
    for k in month_conv:
        if month_conv[k] == month:
            month = k

    # generate the new list of birthdays
    added = False
    old_list = old.split('\n')
    new_list = []
    for b in old_list:
        try:
            m, d, n, s = b.split(' ')
        except:
            continue
        d = int(d)
        m = month_conv[m]

        if ((month_number == m and (d >= day or day == 1)) or month_number < m) != added:
            new_list.append(f"{month} {day} {name} {surname}")
            added = True

        new_list.append(b)

    # write the new list into the file
    with open(BIRTHDAYS_DATABASE, 'w') as birth_file:
        for bir in new_list:
            birth_file.write(bir)
            birth_file.write('\n')


def start(update, context):
    if update.effective_chat.id == CHAT_ID:
        context.bot.send_message(chat_id=CHAT_ID, text="Ciao Fonsy!")


def add(update, context):
    if update.effective_chat.id == CHAT_ID:
        logger.info("Requested to add a person")
        reply_keyboard = [month_conv.keys()]
        update.message.reply_text(
            'Add a birthday! Select the month',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return MONTH


def month(update, context):
    user = update.message.from_user
    global person_to_add
    person_to_add = update.message.text

    logger.info("Month of the person to add: %s", update.message.text)

    if update.effective_chat.id == CHAT_ID:
        update.message.reply_text(
            'Select the day',
            reply_markup=ReplyKeyboardRemove(),
    )

    return DAY


def day(update, context):
    user = update.message.from_user

    global person_to_add
    person_to_add += " " + update.message.text

    logger.info("Day of the person to add: %s", update.message.text)

    if update.effective_chat.id == CHAT_ID:
        update.message.reply_text(
            'Name and surname of the person to add',
            reply_markup=ReplyKeyboardRemove(),
    )

    return RECAP


def recap(update, context):
    user = update.message.from_user

    global person_to_add
    person_to_add += " " + update.message.text

    if update.effective_chat.id == CHAT_ID:
        reply_keyboard = [['Yes', 'No']]
        update.message.reply_text('Confirm?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True), )

    return CONFIRM


def confirm(update, context):
    user = update.message.from_user
    reply_markup = ReplyKeyboardRemove(),
    global person_to_add

    if update.effective_chat.id == CHAT_ID:
        if update.message.text == 'Yes':
            m, d, n, s = person_to_add.split()
            m = month_conv[m]
            add_birthday(m, int(d), n, s)
            update.message.reply_text('Person added!')
            logger.info("added \"%s\" to the database", person_to_add)
        else:
            logger.info("not added \"%s\" to the database", person_to_add)
            update.message.reply_text('Person not added!')

    reply_keyboard = [month_conv.keys()]

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def listing(update, context):
    if update.effective_chat.id == CHAT_ID:
        with open(BIRTHDAYS_DATABASE, 'r') as birth_file:
            content = birth_file.read()
        context.bot.send_message(chat_id=CHAT_ID, text=content)

global person_to_add

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
list_handler = CommandHandler('list', listing)

add_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add)],
        states={
            MONTH: [MessageHandler(Filters.text, month)],
            DAY: [MessageHandler(Filters.text, day)],
            RECAP: [MessageHandler(Filters.text, recap)],
            CONFIRM: [MessageHandler(Filters.text, confirm)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(list_handler)
dispatcher.add_handler(add_handler)

updater.start_polling()
updater.idle()
