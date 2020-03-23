from bs4 import BeautifulSoup as bs
import requests
from datetime import date, timedelta


url_start = 'https://habr.com/ru/'
url_base = 'https://habr.com'
headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}

responce = requests.get(url_start, headers=headers)

soup = bs(responce.text, 'lxml')

data = {}
authors_data = {}
authors_comments_data = {}

def get_pages(soup):
    url_pages = [url_start]
    a = soup.select('li.toggle-menu__item_pagination a')
    for page in a:
        url_pages.append(f"{url_base}{page['href']}")
    return url_pages


def get_authors_comments(url):
    responce = requests.get(url, headers=headers)
    soup = bs(responce.text, 'lxml')
    comments = soup.select('div.comment__head')
    authors_comments_temp = []
    for c in comments:
        author_comments = {'nick': c.span.text, 'url': c.a['href']}
        authors_comments_temp.append(author_comments)
        authors_comments_data[c.span.text] = c.a['href']

    return authors_comments_temp


def get_posts(soup):
    posts = soup.select('ul.content-list article')
    for article in posts:
        title_name = article.h2.a.text.replace('.', '_')
        data[title_name] = {'url': '', 'comments_counts': '', 'date_time': '',
                            'author': {'nick': '', 'url': ''}, 'authors_comments': {'nick': '', 'url': ''}}
        data[title_name]['url'] = article.h2.a['href']
        data[title_name]['comments_counts'] = article.footer.a.span.text.replace('Комментировать', '0')
        data[title_name]['author'] = {
            'nick': article.find('span', attrs={'class': 'user-info__nickname user-info__nickname_small'}).text,
            'url': article.header.a['href']}
        data[title_name]['authors_comments'] = get_authors_comments(article.footer.a['href'])
        data[title_name]['date_time'] = article.find('span', attrs={'class': 'post__time'}).text.replace('сегодня', f'{date.today()}').replace('вчера', f'{date.today() - timedelta(days=1)}')
        authors_data[data[title_name]['author']['nick']]= data[title_name]['author']['url']
