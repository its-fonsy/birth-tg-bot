#!/usr/bin/env python3

import datetime

BIRTHDAYS_DATABASE = "bday.dat"


def convert_month(month):
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
              'December'  : 12, }

    return month_conv[month]


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
            month = convert_month(month)

            if (current_day == day) and (current_month == month):
                print("added ", name)
                birthday_list.append([name, surname.strip()])

    return birthday_list

print(check_birthday())

