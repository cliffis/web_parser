# Developer: Seriakov Igor
#######################################################################################################
# Script for parsing the menu from the restaurant website(https://www.teletal.hu/etlap/19).
# The script searches for all offered dishes containing a component named "csirkemell" (chicken breast),
# and then outputs the result of the cheapest dish for each day of the week to a file.
#######################################################################################################
# Sample output:
#  Day: Péntek
#  Date: 05.13
#  Name: Majonézes burgonya, natúr csirkemell csíkokkal
#  Price: 620 Ft
#######################################################################################################


#libraries
import os
import re
import time
from selenium import webdriver
from bs4 import BeautifulSoup as BS


#links
url = 'https://www.teletal.hu/etlap/19'
tempfile = "index.html"


def load_webpage(url):
    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(3)
    scroll_pause_time = 1
    screen_height = driver.execute_script("return window.screen.height;")
    i = 1

    while True:
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
        i += 1
        time.sleep(scroll_pause_time)
        scroll_height = driver.execute_script("return document.body.scrollHeight;")
        if (screen_height) * i > scroll_height:
            break

    with open(tempfile, "w", encoding="utf-8") as file:
        file.write(driver.page_source)

    driver.quit()
    return open_file(tempfile)


def open_file(tempfile):
    with open(tempfile, encoding="utf-8") as file:
        file = file.read()
    return get_menu(file)


def get_menu(file):
    html = BS(file, 'html.parser')
    items = html.find("div", class_="menu-days menu-days-5 uk-grid-collapse uk-child-width-1-6 uk-text-uppercase tm-text-xxsmall uk-subnav-divider uk-grid").findAll("div", class_="menu-days-active")
    weekdays = []
    for item in items:
        weekdays.append(
            {
                'day': item.find("strong").text,
                'date': item.find("span").text.replace('| ', '')
            }
        )

    items_menu = html.findAll("div", class_="menu-card menu-card-5-day uk-card-small")
    menu = []
    for item in items_menu:
        try:
            menu.append(
                {
                    'dayofweak': item.find("a", class_="menu-info-button menu-info-button-hover").get('nap'),
                    'name': item.find("div", class_="menu-cell-text uk-card-body").find("div", class_="menu-cell-text-row uk-text-break").text.strip(),
                    'price': ''.join(re.findall(r'\d', item.find("strong").text))
                }
            )
        except AttributeError:
            pass
    return sort_menu(menu, weekdays)


def sort_menu(menu, weekdays):
    new_menu = []

    for item in menu:
        if re.search(r"""csirkemell""", item['name'], re.I):
            new_menu.append(item)

    monday_menu = []
    tuesday_menu = []
    wednesday_menu = []
    thursday_menu = []
    friday_menu = []

    for item in new_menu:
        if item['dayofweak'] == "1":
            monday_menu.append(item)
        if item['dayofweak'] == "2":
            tuesday_menu.append(item)
        if item['dayofweak'] == "3":
            wednesday_menu.append(item)
        if item['dayofweak'] == "4":
            thursday_menu.append(item)
        if item['dayofweak'] == "5":
            friday_menu.append(item)

    min_price_for_monday = min(monday_menu, key=lambda m: int(m['price']))
    monday = f'Day: {weekdays[0]["day"]}\nDate: {weekdays[0]["date"]}\nName: {min_price_for_monday["name"]}\nPrice: {min_price_for_monday["price"]} Ft\n'

    min_price_for_tuesday = min(tuesday_menu, key=lambda t: int(t['price']))
    tuesday = f'Day: {weekdays[1]["day"]}\nDate: {weekdays[1]["date"]}\nName: {min_price_for_tuesday["name"]}\nPrice: {min_price_for_tuesday["price"]} Ft\n'

    min_price_for_wednesday = min(wednesday_menu, key=lambda w: int(w['price']))
    wednesday = f'Day: {weekdays[2]["day"]}\nDate: {weekdays[2]["date"]}\nName: {min_price_for_wednesday["name"]}\nPrice: {min_price_for_wednesday["price"]} Ft\n'

    min_price_for_thursday = min(thursday_menu, key=lambda th: int(th['price']))
    thursday = f'Day: {weekdays[3]["day"]}\nDate: {weekdays[3]["date"]}\nName: {min_price_for_thursday["name"]}\nPrice: {min_price_for_thursday["price"]} Ft\n'

    min_price_for_friday = min(friday_menu, key=lambda fr: int(fr['price']))
    friday = f'Day: {weekdays[4]["day"]}\nDate: {weekdays[4]["date"]}\nName: {min_price_for_friday["name"]}\nPrice: {min_price_for_friday["price"]} Ft'

    return save_results(monday, tuesday, wednesday, thursday, friday)


def save_results(monday, tuesday, wednesday, thursday, friday):
    with open("results.txt", "w", encoding="utf-8") as file:
        data = ['Dishes with the lowest price:\n', monday, '\n', tuesday, '\n', wednesday, '\n', thursday, '\n', friday]
        file.writelines(data)
        return del_temp_file(tempfile)


def del_temp_file(tempfile):
    os.remove(tempfile)


if __name__ == "__main__":
    load_webpage(url)
