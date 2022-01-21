from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import json
import pandas as pd


def get_html_json(url, counter=100000):
    driver = webdriver.Chrome('chromedriver')
    message = set()
    j = 0
    try:
        driver.get(url=url)
        print('Ввойдите в телеграм. Выберите чат для сбора информации.')
        input()
        while True:

            find_more_element = driver.find_element(By.CLASS_NAME, 'sticky_sentinel--top')

            actions = ActionChains(driver)
            actions.move_to_element(find_more_element).perform()
            time.sleep(0.3)

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            try:
                all_message = soup.find_all('div', {"class": 'bubble'})
                for ms in all_message:
                    try:
                        message.add(ms)
                    except:
                        print('Error')
                print('Message: ' + str(len(message)))
            except:
                print('Error')
            if len(message) > 1000:
                add_to_json(message)
                message = set()
                j += 1
            if j == 50:
                add_to_json(message)
                message = set()
                print('Продолжить - ? Y/N')
                process = str(input().lower())
                j = 0
                if process == 'n':
                    break
            if j*1000 >= counter:
                break
        add_to_json(message)

        input()

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def add_to_json(message_obj):
    with open('telegram.json', 'r', encoding='utf-8') as file:
        telega = json.load(file)

    for ms in message_obj:
        try:
            user_id = ms.find('div', {"class": "name"}).get('data-peer-id')
        except:
            user_id = 'Not_found'
        try:
            message_data = ms.find('span', {"class": 'time'}).get('title')
            message_data_text = str(message_data)
            if message_data.find('Edited') != -1:
                message_data_edited_index = message_data.find('Edited')
                message_data_text = message_data[:message_data_edited_index]
                if message_data.find('Original') != -1:
                    message_data_original = message_data[message_data.find('Original'):]
                    message_data_edited = message_data[message_data_edited_index:message_data.find('Original')]
                else:
                    message_data_edited = message_data[message_data_edited_index:]
                    message_data_original = 'Not_found'
            elif message_data.find('Original') != -1:
                message_data_original = message_data[message_data.find('Original'):]
                message_data_text = message_data[:message_data.find('Original')]
                message_data_edited = 'Not_found'
            else:
                message_data_edited = 'Not_found'
                message_data_original = 'Not_found'
        except:
            message_data = 'Not_found'
            message_data_text = 'Not_found'
            message_data_edited = 'Not_found'
            message_data_original = 'Not_found'
        try:
            name = ms.find('div', {"class": "name"}).text
        except:
            name = 'Not_found'
        try:
            article = ms.find('div', {"class": 'message'}).text
        except:
            article = 'Not_found'
        try:
            reply_name_id = ms.find('div', {"class": 'reply-title'}).find('span', {"class": "peer-title"}).get('data-peer-id')
        except:
            reply_name_id = 'Not_found'
        try:
            reply_name = ms.find('div', {"class": 'reply-title'}).find('span', {"class": "peer-title"}).get_text()
        except:
            reply_name = 'Not_found'
        try:
            reply_article = ms.find('div', {"class": "reply-subtitle"}).get_text()
        except:
            reply_article = 'Not_found'
        try:
            service_msg_all = ms.find('div', {"class": "service-msg"}).find("span", {"class": "i18n"}).find_all('span')
            service_msg = []
            for i in service_msg_all:
                service_msg.append(i)

            invited_user = 'Not_found'
            inviting_user = 'Not_found'
            invited_user_id = 'Not_found'
            inviting_user_id = 'Not_found'

            if len(service_msg) == 1:
                invited_user = service_msg[0].get_text()
                inviting_user = 'Link'
                try:
                    invited_user_id = service_msg[0].get('data-peer-id')
                except:
                    invited_user = 'Not_found'
                    inviting_user = 'Not_found'
                    invited_user_id = 'Not_found'
                    inviting_user_id = 'Not_found'

            elif len(service_msg) == 2:
                invited_user = service_msg[1].get_text()
                inviting_user = service_msg[0].get_text()
                try:
                    invited_user_id = service_msg[1].get('data-peer-id')
                    inviting_user_id = service_msg[0].get('data-peer-id')
                except:
                    invited_user = 'Not_found'
                    inviting_user = 'Not_found'
                    invited_user_id = 'Not_found'
                    inviting_user_id = 'Not_found'
        except:
            invited_user = 'Not_found'
            inviting_user = 'Not_found'
            invited_user_id = 'Not_found'
            inviting_user_id = 'Not_found'

        telega.append({
            "user_id": user_id,
            "name": name,
            "article": article,
            "reply_name_id": reply_name_id,
            "reply_name": reply_name,
            "reply_article": reply_article,
            "message_data_text": message_data_text,
            "message_data_edited": re.sub(r'\w+\: ', '', message_data_edited),
            "message_data_original": re.sub(r'\w+\: ', '', message_data_original),
            "invited_user": invited_user,
            "inviting_user": inviting_user,
            "invited_user_id": invited_user_id,
            "inviting_user_id": inviting_user_id
        })

        if len(telega) % 100 == 0:
            print('Add to exel: ' + str(len(telega)))

    with open('telegram.json', 'w', encoding='utf-8') as json_file:
        try:
            json.dump(telega, json_file, ensure_ascii=False,
                      indent=4,
                      separators=(',', ': '))
        except Exception as ex:
            print('Hear error')
            print(ex)


if __name__ == '__main__':
    print('Для версии Google Chrome: 97.0.4692.71')
    print('Если программа не запускаеться то нужно скачать Chrome driver версии Chrome браузера. Потом заменить Chrome driver в папке.')
    print('Введите сколько сообщений нужно: ')
    json_created = []
    with open('telegram.json', 'w', encoding='utf-8') as json_file:
        json.dump(json_created, json_file)
    counter = int(input())
    get_html_json('https://xn--80affa3aj0al.xn--80asehdb/', counter)

    df_json = pd.read_json('telegram.json')
    df_json.to_excel('TELEGRAM.xlsx')
