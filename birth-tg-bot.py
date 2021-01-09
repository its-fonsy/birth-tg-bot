#!/usr/bin/env python3

import datetime

BIRTHDAYS_DATABASE = "bday.dat"
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



birthday_list = check_birthday()
birthday_message(birthday_list)
add_birthday(1, 1, 'Luca', 'Laurenti')
