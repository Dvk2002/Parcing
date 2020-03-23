import requests
import time
import json
import re

url_start = 'https://5ka.ru/api/v2/special_offers/'
cat_url = 'https://5ka.ru/api/v2/categories/'

headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}


def goods_from_cat(url, param_code, param_name):
    result = []
    while url:
        responce = requests.get(url, headers=headers,
                                params={'categories': param_code}) if param_code else requests.get(url, headers=headers)
        param_code = None
        data = responce.json()
        result.extend(data.get('results'))
        url = data.get('next')
        time.sleep(2)
    if result:
        with open(f'{param_name}.json', 'w') as file:
            file.write(json.dumps(result))


def dif_by_cat(cat_url, headers):
    categories = requests.get(cat_url, headers=headers).json()
    for cat in categories:
        param_code, param_name = cat['parent_group_code'], re.search('[^\n"*]+', cat['parent_group_name'])[0]
        if param_code and param_name:
            goods_from_cat(url_start, param_code, param_name)


if __name__ == '__main__':

    categories = requests.get(cat_url, headers=headers).json()
    for cat in categories:
        param_code, param_name = cat['parent_group_code'], re.search('[^"*\n]+', cat['parent_group_name'])[0]
        print(param_name)


    #dif_by_cat(cat_url, headers)

    print(1)
