from datetime import datetime

import requests
from bs4 import BeautifulSoup
from process import Post


class ForumLoader:
    def __init__(self, path) -> None:
        self.base_path = path
        self.posts = []

    def fetch_post(self, post_id) -> None:
        url = f'{self.base_path}sp{post_id}'
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.content, 'html.parser')
        try:
            date_tag = soup.find('div', class_='post-heading')
            date_string = date_tag.text.strip()
            date = datetime.strptime(date_string, "%Y-%m-%d, %H:%M")

            author_tag = soup.find('a', id=f'dropdown-user-post{post_id}')
            author = author_tag.get('href').strip('/')

            self.posts.append(Post(
                post_id=post_id,
                date=date,
                author_id=author
            ))
        except (AttributeError, ConnectionRefusedError) as error:
            print(url)
            raise error
