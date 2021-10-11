import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common import action_chains
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
from urllib.parse import unquote
import json

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 YaBrowser/21.8.3.614 Yowser/2.5 Safari/537.36'
}

def get_source_html(url):
    #Options
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 YaBrowser/21.8.3.614 Yowser/2.5 Safari/537.36')

    driver = webdriver.Chrome(executable_path = 'D:\Python\Git\spb.zoon.ru\chromedriver.exe', options = options)
    driver.maximize_window()

    try:
        driver.get(url = url)
        time.sleep(3)

        while True:
            find_more_element = driver.find_element_by_class_name('catalog-button-showMore')

            if driver.find_elements_by_class_name('hasmore-text'):
                with open('index.html', 'w', encoding = 'utf-8') as file:
                    file.write(driver.page_source)
                break
            else:
                actions = ActionChains(driver)
                actions.move_to_element(find_more_element).perform()
                time.sleep(2)

    except Exception as _ex:
        print(_ex)

    finally:
        driver.close()
        driver.quit()
    
def get_items_urls(file_path):
    with open(file_path, encoding = 'utf-8') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    items_divs = soup.find_all('div', class_ = 'minicard-item__info')

    urls_list = []
    for item in items_divs:
        item_url = item.find('h2').find('a').get('href')
        urls_list.append(item_url)

    with open('items_urls.txt', 'w') as file:
        for url in urls_list:
            file.write(f'{url}\n')
    
    return 'Urls collected successfully!'

def get_data(file_path):
    with open(file_path) as file:
        urls_list = [url.strip() for url in file.readlines()]
    
    count = 1
    urls_count = len(urls_list)
    result_list = []
    for url in urls_list:
        res = requests.get(url = url, headers = HEADERS)
        soup = BeautifulSoup(res.text, 'lxml')

        try:
            item_name = soup.find('span', {'itemprop': 'name'}).text.strip()
        except Exception as _ex:
            item_name = None
        
        item_phones_list = []
        try:
            item_phones = soup.find('div', class_ = 'service-phones-list').find_all('a', class_ = 'js-phone-number')
            for number in item_phones:
                item_phone = number.get('href').split(':')[-1].strip()
                item_phones_list.append(item_phone)
        except Exception as _ex:
            item_phones_list = None

        try:
            item_address = soup.find('address', class_ = 'iblock').text.strip()
        except Exception as _ex:
            item_address = None

        try:
            item_site = soup.find(text = re.compile('Сайт|Официальный сайт')).find_next().text.strip()
        except Exception as _ex:
            item_site = None

        social_networks_list = []
        try:
            item_social_networks = soup.find(text = re.compile('Страница в соцсетях')).find_next().find_all('a')
            for sn in item_social_networks:
                sn_url = sn.get('href')
                sn_url = unquote(sn_url.split('?to=')[1].split('&')[0])
                social_networks_list.append(sn_url)
        except Exception as _ex:
            social_networks_list = None

        result_list.append(
            {
                'item_name': item_name,
                'item_url': url,
                'item_phones_list': item_phones_list,
                'item_address': item_address,
                'item_site': item_site,
                'social_networks_list': social_networks_list
            }
        )

        print(f'Processed: {count}/{urls_count}...')
        count += 1
    
    with open('data.json', 'w', encoding = 'utf-8') as file:
        json.dump(result_list, file, indent = 4, ensure_ascii = False)

    return '[INFO] Data collected succesfully!'

def main():
    get_source_html(url = 'https://spb.zoon.ru/medical/type/detskaya_poliklinika/')
    print(get_items_urls(file_path = 'D:\Python\Git\spb.zoon.ru\index.html'))
    print(get_data(file_path = 'D:\Python\Git\spb.zoon.ru\items_urls.txt'))

if __name__ == '__main__':
    main()