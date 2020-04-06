# -*- coding: utf-8 -*-
import scrapy
import re
import json
from urllib.parse import urljoin, urlencode
from copy import deepcopy


class InstaSpider(scrapy.Spider):
    name = 'insta'
    allowed_domains = ['instagram.com']
    start_urls = ['http://www.instagram.com//']
    pars_users = ['fedorkonyukhov', 'fedoremelianenkoofficial']
    graphql_url = "https://www.instagram.com/graphql/query/?"
    variables = {"id":'',
                 "include_reel": True,
                 "fetch_mutual": False,
                 "first": 100,
                 }

    def __init__(self, logpass : tuple, **kwargs):
        self.login, self.pwd = logpass
        self.Query_hash = {'follower': 'c76146de99bb02f6415203be841dd25a',
                           'subscription': 'd04b0a864b4b54837c0d870b0e77e076',
                           'post': 'd496eb541e5c789274548bf473cc553e',
                           'like' : 'd5d763b1e2acf209d62d22d184488e57',
                           'comment': 'bc3296d1ce80a24b1b6e40b1e72903f5',
                           }

        super().__init__(**kwargs)

    def parse(self, response):
        login_url = 'https://www.instagram.com/accounts/login/ajax/'
        csrf_token = self.fetch_csrf_token(response.text)

        yield scrapy.FormRequest(
            login_url,
            method='POST',
            callback=self.main_parse,
            formdata={'username': self.login, 'password': self.pwd},
            headers={'X-CSRFToken': csrf_token},
        )

    def main_parse(self, response):
        j_resp = json.loads(response.text)
        if j_resp.get("authenticated"):
            for u_name in self.pars_users:
                yield response.follow(
                    urljoin(self.start_urls[0], u_name),
                    callback=self.parse_user,
                    cb_kwargs={'user_name': u_name}
                )

    def parse_user(self, response, user_name: str):
        user_id = self.fetch_user_id(response.text, user_name)
        user_vars = deepcopy(self.variables)
        user_vars.update({'id': user_id})

        user_vars_post = {k: user_vars[k] for k in ['id', 'first']}

        url_followers = self.make_graphql_url(user_vars, hash_key ='follower')
        url_subscription = self.make_graphql_url(user_vars,  hash_key ='subscription')
        url_posts = self.make_graphql_url(user_vars = user_vars_post,  hash_key ='post')

        yield response.follow(
            url_subscription,
            callback=self.parse_subscriptions,
            cb_kwargs={'user_vars': user_vars, 'user_name': user_name, }
        )

        yield response.follow(
            url_followers,
            callback= self.parse_followers,
            cb_kwargs= {'user_vars': user_vars, 'user_name': user_name, }
        )

        yield response.follow(
            url_posts,
            callback=self.parse_posts,
            cb_kwargs={'user_vars_post': user_vars_post, 'user_name': user_name, }
        )
        print(2)


    def parse_followers(self, response, user_vars, user_name):
        j_response = json.loads(response.text)
        if j_response['data']['user']['edge_followed_by']['page_info']['has_next_page']:
            user_vars.update({'after':j_response['data']['user']['edge_followed_by']['page_info']['end_cursor']})
            url = self.make_graphql_url(user_vars, hash_key='follower')

            yield response.follow(
                url,
                callback= self.parse_followers,
                cb_kwargs= {'user_vars': user_vars, 'user_name': user_name})

        followers = j_response['data']['user']['edge_followed_by']['edges']
        for follower in followers:
            yield {'user_name': user_name, 'user_id': user_vars['id'], 'follower': follower['node']}

    def parse_subscriptions(self, response, user_vars, user_name):
        j_response = json.loads(response.text)
        if j_response['data']['user']['edge_follow']['page_info']['has_next_page']:
            user_vars.update({'after': j_response['data']['user']['edge_follow']['page_info']['end_cursor']})
            url = self.make_graphql_url(user_vars, hash_key='subscription')
            yield response.follow(
                url,
                callback=self.parse_subscriptions,
                cb_kwargs={'user_vars': user_vars, 'user_name': user_name})
        subscriptions = j_response['data']['user']['edge_follow']['edges']
        for subscription in subscriptions:
            yield {'user_name': user_name, 'user_id': user_vars['id'], 'subscription': subscription['node']}

    def parse_posts(self, response, user_vars_post, user_name):

        j_response = json.loads(response.text)
        if j_response['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']:
            user_vars_post.update({'after': j_response['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']})
            url = self.make_graphql_url(user_vars_post, hash_key='post')
            yield response.follow(
                url,
                callback=self.parse_posts,
                cb_kwargs={'user_vars_post': user_vars_post, 'user_name': user_name})
        posts = j_response['data']['user']['edge_owner_to_timeline_media']['edges']
        for post in posts:
            data = {}
            data.update({'user_name': user_name, 'user_id': user_vars_post['id'], 'posts': post['node']})
            shortcode = post['node']['shortcode']
            user_vars_likes = {"shortcode": shortcode,
                               "include_reel": True,
                               "first": 100,
                               }
            url_like = self.make_graphql_url(user_vars_likes, hash_key='like')

            yield response.follow(
                url_like,
                callback=self.parse_likes,
                cb_kwargs={'user_vars_likes': user_vars_likes, 'data': data}
            )

    def parse_likes(self,response, user_vars_likes, data):
        user_likes = []
        j_response = json.loads(response.text)
        if j_response['data']['shortcode_media']['edge_liked_by']['page_info']['has_next_page']:
            user_vars_likes.update({'after': j_response['data']['shortcode_media']['edge_liked_by']['page_info']['end_cursor']})
            url_like = self.make_graphql_url(user_vars_likes, hash_key='like')
            yield response.follow(
                url_like,
                callback=self.parse_likes,
                cb_kwargs={'user_vars_likes': user_vars_likes})
            user_likes.extend(re.findall('\"username\":\"([^,]+)\"',response.text))
        data['user_likes'] = list(set(user_likes))

        url_comments = self.make_graphql_url(user_vars_likes, hash_key='comment')

        yield response.follow(
            url_comments,
            callback=self.parse_comments,
            cb_kwargs={'user_vars_likes': user_vars_likes, 'data': data}
        )

    def parse_comments(self, response, user_vars_likes, data):

        user_comments = []
        j_response = json.loads(response.text)
        if j_response['data']['shortcode_media']['edge_media_to_parent_comment']['page_info']['has_next_page']:
            user_vars_likes.update(
                {'after': j_response['data']['shortcode_media']['edge_media_to_parent_comment']['page_info']['end_cursor']})
            url_comments = self.make_graphql_url(user_vars_likes, hash_key='like')
            yield response.follow(
                url_comments,
                callback=self.parse_comments,
                cb_kwargs={'user_vars_likes': user_vars_likes})
            user_comments.extend(re.findall('\"username\":\"([^,]+)\"', response.text))
        data['user_comments'] = list(set(user_comments))
        yield data

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
        return json.loads(matched).get('id')

    def make_graphql_url(self, user_vars, hash_key):
        return f'{self.graphql_url}query_hash={self.Query_hash[hash_key]}&{urlencode(user_vars)}'



