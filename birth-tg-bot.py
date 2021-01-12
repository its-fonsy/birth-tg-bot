#!/usr/bin/env python3

import datetime
import pytz
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

# name of the database
BIRTHDAYS_DATABASE = "bday.dat"

# check all the required file exist
try:
    with open("token", "r") as token_file:
        TOKEN = token_file.read().strip()
except IOError:
    logger.info("ERROR: token file missing. Exiting")
    quit()

try:
    with open("chat_id", "r") as id_file:
        CHAT_ID = int(id_file.read().strip())
except IOError:
    logger.info("ERROR: chat_id file missing. Exiting")
    quit()

try:
    with open(BIRTHDAYS_DATABASE, "r") as id_file:
        pass
except IOError:
    logger.info("ERROR: birthday database missing. Exiting")
    quit()

# dict used to convert the month from name to number
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


class Person( object ):

    def __init__(self, m:int, d:int, n:str, s:str):
        self.month = m
        self.day = d
        self.name = n
        self.surname = s


    def is_birthday(self) -> bool:
        """
        return if True if today it's his/her birthday
        """
        now = datetime.datetime.now()
        return (now.month == self.month) and (now.day == self.day)


    def string(self) -> str:
        """
        return string of the person
        Example: January 1 Mario Rossi
        """
        for month in month_conv:
            if month_conv[month] == self.month:
                birth = month; break

        birth += " " + str(self.day) + " "
        birth += self.name + " "
        birth += self.surname
        return birth


    def __eq__(self:object, other:object) -> bool:
        return self.month == other.month and \
            self.day == other.day and \
            self.name == other.name and \
            self.surname == other.surname


    def __gt__(self:object, other:object) -> bool:
        if self.month != other.month:
            return self.month > other.month
        else:
            return self.day > other.day


    def __lt__(self:object, other:object) -> bool:
        return not self.__gt__(other)


class BirthdayBot( object ):

    def __init__(self):
        self.updater = Updater(token=TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.birthday_list = []
        self.create_birthday_list()

        start_handler = CommandHandler('start', self.start)
        list_handler = CommandHandler('list', self.listing)
        update_handler = CommandHandler('update', self.update)
        next_handler = CommandHandler('next', self.next)

        # constant used to handle conversation with the bot
        # to add a birthday via telegram
        self.MONTH, self.DAY, self.NAME, self.RECAP, self.CONFIRM = range(5)
        self.person_to_add = Person(1, 1, "a", "a")
        add_handler = ConversationHandler(
                entry_points=[CommandHandler('add', self.add)],
                states={
                    self.MONTH: [MessageHandler(Filters.text, self.add_month)],
                    self.DAY: [MessageHandler(Filters.text, self.add_day)],
                    self.RECAP: [MessageHandler(Filters.text, self.add_recap)],
                    self.CONFIRM: [MessageHandler(Filters.text, self.add_confirm)],
                },
                fallbacks=[CommandHandler('cancel', self.add_cancel)],
        )

        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(list_handler)
        self.dispatcher.add_handler(update_handler)
        self.dispatcher.add_handler(next_handler)
        self.dispatcher.add_handler(add_handler)
        self.updater.job_queue.run_daily(
            callback=self.birthday_message,
            time=datetime.time(hour=0, minute=1, tzinfo=pytz.timezone('Europe/Rome')),
            days=tuple(range(7))
        )

        # start the main loop
        self.updater.start_polling()
        self.updater.idle()


    def create_birthday_list(self) -> None:
        """
        Function that generate the list with all the birthdays
        """
        with open(BIRTHDAYS_DATABASE, 'r') as birth_file:
            for line in birth_file:
                month, day, name, surname = line.strip().split(' ')
                day   = int(day)
                month = month_conv[month]

                self.birthday_list.append(Person(month, day, name, surname))


    def add_birthday(self, p:Person) -> None:
        """ Add a birthday to the list and database """
        self.update_list()
        self.birthday_list.append(p)
        self.birthday_list.sort()
        with open(BIRTHDAYS_DATABASE, 'w') as birth_file:
            for birth in self.birthday_list:
                line = birth.string()
                birth_file.write(line)
                birth_file.write('\n')


    def start(self, update: Update, context:CallbackContext) -> None:
        if update.effective_chat.id == CHAT_ID:
            context.bot.send_message(chat_id=CHAT_ID, text="Hi Fonsy!")


    def birthday_message(self, context:CallbackContext) -> None:
        logger.info("Checking birthday of the day")

        # get the list of todays birthdays
        today_birthdays = []
        for person in self.birthday_list:
            if person.is_birthday():
                today_birthdays.append(person)

        # write the message based on the lenght of the list
        if today_birthdays:
            if len(today_birthdays) > 1:
                message = f"Today is the birthday of:\n"
                for person in today_birthdays:
                    message += f" - {person.name} {person.surname}\n"
                    logger.info("Today is the birthday of %s %s", person.name, person.surname)
            else:
                person = today_birthdays[0]
                message = f"Today is the birthday of {person.name} {person.surname}!"
                logger.info("Today is the birthday of %s %s", person.name, person.surname)

            context.bot.send_message(chat_id=CHAT_ID, text=message)
        else:
            context.bot.send_message(chat_id=CHAT_ID, text="Today there aren't any birthday")
            logger.info("There aren't any birthday today")


    def add(self, update: Update, context:CallbackContext) -> int:
        if update.effective_chat.id == CHAT_ID:
            logger.info("Requested to add a person")
            reply_keyboard = [
               ['January', 'February', 'March', 'April' ],
               ['May', 'June', 'July', 'August'],
               ['September', 'October', 'November', 'December']
            ]
            update.message.reply_text(
                'Add a birthday! Select the month',
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
            )

        return self.MONTH


    def add_month(self, update: Update, context:CallbackContext) -> int:
        user = update.message.from_user
        self.person_to_add.month = month_conv[update.message.text]

        logger.info("Month of the person to add: %s", update.message.text)

        if update.effective_chat.id == CHAT_ID:
            update.message.reply_text(
                'Select the day',
                reply_markup=ReplyKeyboardRemove(),
        )

        return self.DAY


    def add_day(self, update: Update, context:CallbackContext) -> int:
        user = update.message.from_user

        self.person_to_add.day = int(update.message.text)

        logger.info("Day of the person to add: %s", update.message.text)

        if update.effective_chat.id == CHAT_ID:
            update.message.reply_text(
                'Name and surname of the person to add',
                reply_markup=ReplyKeyboardRemove(),
            )

        return self.RECAP


    def add_recap(self, update: Update, context:CallbackContext) -> int:
        user = update.message.from_user
        name, surname = update.message.text.split()

        self.person_to_add.name = name
        self.person_to_add.surname = surname

        if update.effective_chat.id == CHAT_ID:
            reply_keyboard = [['Yes', 'No']]
            update.message.reply_text('Confirm?',
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True), )

        return self.CONFIRM


    def add_confirm(self, update: Update, context:CallbackContext) -> int:
        user = update.message.from_user
        reply_markup = ReplyKeyboardRemove(),

        if update.effective_chat.id == CHAT_ID:
            if update.message.text == 'Yes':
                self.add_birthday(self.person_to_add)
                update.message.reply_text('Person added!', reply_markup=ReplyKeyboardRemove())
                logger.info("Added \"%s %s\" to the database",
                            self.person_to_add.name,
                            self.person_to_add.surname)
            else:
                update.message.reply_text('Person not added!', reply_markup=ReplyKeyboardRemove())
                logger.info("Not added \"%s %s\" to the database",
                            self.person_to_add.name,
                            self.person_to_add.surname)


        return ConversationHandler.END


    def add_cancel(self, update: Update, context:CallbackContext) -> int:
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.first_name)
        update.message.reply_text(
            'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END


    def listing(self, update: Update, context:CallbackContext) -> None:
        if update.effective_chat.id == CHAT_ID:
            logger.info("Requested list of birthday")
            message = ""
            for person in self.birthday_list:
                message += person.string() + "\n"

            context.bot.send_message(chat_id=CHAT_ID, text=message)


    def update_list(self) -> None:
        with open(BIRTHDAYS_DATABASE, 'r') as birth_file:
            for line in birth_file:
                month, day, name, surname = line.strip().split(' ')
                day   = int(day)
                month = month_conv[month]
                dummy = Person(month, day, name, surname)

                if dummy not in self.birthday_list:
                    logger.info("Added %s %s to the list", dummy.name, dummy.surname)
                    self.birthday_list.append(dummy)
                    self.birthday_list.sort()


    def update(self, update: Update, context:CallbackContext) -> None:
        logger.info("Updating the list of birthday")
        if update.effective_chat.id == CHAT_ID:
            self.update_list()

        context.bot.send_message(chat_id=CHAT_ID, text="List updated!")


    def next(self, update: Update, context:CallbackContext) -> None:
        """
        Show the 4 next birthday
        """
        if update.effective_chat.id == CHAT_ID:
            logger.info("Sending the next four birthday")
            now = datetime.datetime.now()
            dummy = Person(now.month, now.day, "A", "B")

            # create the list with the next 4 birthday
            next_birthday = []
            n_birthday = 4
            for person in self.birthday_list:
                if (person > dummy) and (len(next_birthday) < n_birthday):
                    next_birthday.append(person)

            # deal when you are between december and january 
            if len(next_birthday) < n_birthday:
                for p in range(n_birthday - len(next_birthday)):
                    next_birthday.append(self.birthday_list[p])

            # create the message and send it
            message = "The next four birthday are:\n"
            for person in next_birthday:
                message += f" - {person.string()}\n"
            context.bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = BirthdayBot()


if __name__ == "__main__":
    main()
