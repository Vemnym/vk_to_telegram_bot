from __future__ import absolute_import
import psycopg2
from celery import shared_task
import requests
import config


@shared_task
def get_post_from_vk():
    conn = psycopg2.connect(dbname="postgres",
                            user="postgres",
                            password="postgres",
                            host="db")
    all_posts = []

    for domain in config.domains:
        offset = 0
        while offset < 2000:
            response = requests.get('https://api.vk.com/method/wall.get',  # spare request
                                    params={
                                        'access_token': config.vk_token,
                                        'v': config.version,
                                        'domain': domain,
                                        'offset': offset,
                                        'count': 100,
                                    })

            data = response.json()['response']['items']

            all_posts.extend(data)
            offset +=100

    correct_posts = []
    for post in all_posts:  # filter for posts what have url
        if 'http://ali.pub' in post['text'].lower():
            correct_posts.append(post)

    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS products")
    cur.execute("CREATE TABLE products (id SERIAL PRIMARY KEY, text VARCHAR);")

    for post in correct_posts:
        cur.execute("INSERT INTO products (text) VALUES(%s)", (post['text'].lower(),))

    conn.commit()
    cur.close()

    conn.close()
