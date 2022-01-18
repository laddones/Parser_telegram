from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import openpyxl


def get_html(url):
    driver = webdriver.Chrome('chromedriver')
    message = set()
    try:
        driver.get(url=url)
        input()
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        while True:
            if soup.find('div', {'id': 'message1'}):
                break

            find_more_element = driver.find_element(By.XPATH,
                                                    '/html/body/div[1]/div/div/div[2]/div[3]/div[2]/div[2]/div[1]/div/div[1]')
            actions = ActionChains(driver)
            actions.move_to_element(find_more_element).perform()
            time.sleep(0.3)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            try:
                all_message = soup.find_all('div', {"class": 'Message'})
                for ms in all_message:
                    try:
                        message.add(ms)
                    except:
                        print('Error')
                print(len(message))
                if len(message) > 500:
                    add_to_exel(message)
                    message = set()

                    print('Продолжить - ? Y/N')
                    process = str(input().lower())
                    if process == 'n':
                        break

            except:
                print('Error')

        # add_to_exel(message)

        print('*'*4)
        input()

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def add_to_exel(message_obj):
    excel_obj = openpyxl.load_workbook('Sheat.xlsx')
    ws = excel_obj.active
    for ms in message_obj:
        try:
            message_id = ms.find('div', {"class": "bottom-marker"}).get('data-message-id')

        except:
            message_id = 'Not_found'
        try:
            message_text = ms.find('p', {"class": 'text-content'}).get_text()
        except:
            message_text = 'Not_found'
        try:
            message_author = ms.find('div', {"class": "message-title"}).get_text()
        except:
            message_author = 'Not_found'
        try:
            message_time = ms.find('span', {"class": "message-time"}).get_text()
        except:
            message_time = 'Not_found'

        ws[f'A{str(ws.max_row+1)}'] = int(message_id)
        ws[f'B{str(ws.max_row)}'] = message_text
        ws[f'C{str(ws.max_row)}'] = message_author
        ws[f'D{str(ws.max_row)}'] = message_time

    excel_obj.save('Sheat.xlsx')


if __name__ == '__main__':
    get_html('https://web.telegram.org/z/#-1330723289')

    # parsing_telegram()
