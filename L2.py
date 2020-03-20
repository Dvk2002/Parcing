from bs4 import  BeautifulSoup as bs
import requests
import json
import re
from collections import defaultdict


url_start= 'https://geekbrains.ru/posts'
url_base = 'https://geekbrains.ru'
responce = requests.get(url_start)
soup = bs(responce.text, 'lxml')
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}

data_tag = defaultdict(str)

def get_next_page(soup) -> str :
    ul = soup.find('ul', attrs={'class':'gb__pagination'})
    a = ul.find(lambda tag: tag.name == 'a' and tag.text == '›')
    return f'{url_base}{a["href"]}' if a else None


def get_page(url):
    while url:
        responce = requests.get(url, headers=headers)
        soup = bs(responce.text, 'lxml')
        yield soup
        url = get_next_page(soup)


def get_post_url(soup) -> set:
    post_a = soup.select('div.post-items-wrapper div.post-item a')
    return set(f'{url_base}{a["href"]}' for a in post_a)


def get_post_data(post_url:str) -> dict:
    template_data = {'url': 'post_url','title':'', 'tags':[],'author': {'name':'wrater_name', 'url': 'full_writer_url'}, 'image':''}
    responce = requests.get(post_url, headers = headers)
    soup = bs(responce.text, 'html.parser')
    template_data['url'] = post_url
    template_data['title'] = soup.select_one('article h1.blogpost-title').text
    template_data['image'] = soup.find('img')['src']
    template_data['author']['name'] = soup.select_one('article div.text-lg').text
    template_data['author']['url'] = f"{url_base}{soup.select_one('div.col-md-5 a')['href']}"
    template_data['tags']= {item.text: f'{url_base}{item["href"]}' for item in soup.select('article a.small')}
    return template_data


def get_tags(data_post):
    for tag_name,tag_url in data_post['tags'].items():
        if not data_tag[tag_name]:
            data_tag[tag_name]= {'url': '', 'posts': []}
            data_tag[tag_name]['url'] = tag_url
        data_tag[tag_name]['posts'].append(data_post['url'])



if __name__ == '__main__':


    for soup in get_page(url_start):
        posts = get_post_url(soup)
        for url in posts:
            data_post = get_post_data(url)
            get_tags(data_post)
            url_name = re.search("[^/]+$",url)[0]
            with open(f'{url_name}.json', 'w') as file:
                file.write(json.dumps(data_post))
        print(1)
    with open('tags.json', 'w') as file:
                file.write(json.dumps(data_tag))




