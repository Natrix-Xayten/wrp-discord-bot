import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from config import base_url, flarum_token

# format_status by atheop1337
def format_status(status: int) -> str:
        return {
            200: 'Всё прошло успешно!',
            201: 'Всё прошло успешно!',
            401: 'Ошибка! Неавторизован',
            403: 'Ошибка! Доступ запрещен',
            404: 'Ошибка! Обсуждение не найдено',
            500: 'Ошибка! Ошибка сервера',
        }.get(status, 'Ошибка! Неизвестная ошибка')

def like_post(post_id):
    url = f'{base_url}api/posts/{post_id}'

    headers = {
        'Authorization': f'Token {flarum_token}',
        'Content-Type': 'application/json',
    }

    payload = {
        'data': {'type': 'posts', 'attributes': {'isLiked': True}, 'id': post_id}
    }

    response = requests.patch(url, json=payload, headers=headers)
    return format_status(response.status_code)

def unlike_post(post_id):
    url = f'https://forum.wayzer.ru/api/posts/{post_id}'

    headers = {
        'Authorization': f'Token {flarum_token}',
        'Content-Type': 'application/json',
    }

    payload = {
        'data': {'type': 'posts', 'attributes': {'isLiked': False}, 'id': post_id}
    }

    response = requests.patch(url, json=payload, headers=headers)
    return format_status(response.status_code)

def send_message(discussion_id, content):
    api_url = f'{base_url}api/posts'
    headers = {
        'Authorization': f'Token {flarum_token}',
        'Content-Type': 'application/json',
    }

    data = {
        'data': {
            'type': 'posts',
            'attributes': {
                'content': content
            },
            'relationships': {
                'discussion': {
                    'data': {
                        'type': 'discussions',
                        'id': discussion_id
                    }
                }
            }
        }
    }
    response = requests.post(api_url, json=data, headers=headers)
    return format_status(response.status_code)

def get_posts(discussion_id):
    api_url = f'{base_url}api/discussions/{discussion_id}'

    try:
        headers = {
            'Authorization': f'Token {flarum_token}',
            'Content-Type': 'application/json',
        }

        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        posts = response.json()

        discussion_title = posts['data']['attributes']['title']
        posts_id = posts['data']['relationships']['posts']['data']
        post_end = {}

        for v in posts_id:
            post_id = v['id']
            response_post = requests.get(f'{base_url}api/posts/{post_id}')
            spots = response_post.json()

            content = spots['data']['attributes'].get('contentHtml', '')
            if not content:
                continue

            soup = BeautifulSoup(content, 'html.parser')
            for mention in soup.find_all('a', class_='PostMention'):
                username = mention.get_text(strip=True, separator=' ')
                link = mention['href']
                mention.replace_with(f'[{username}]({link})')

            for img in soup.find_all('img'):
                img.replace_with(f'[Изображение]({img["src"]})')

            for blockquote in soup.find_all('blockquote'):
                blockquote_text = blockquote.get_text(separator='\n', strip=True)
                blockquote.replace_with(f'> {blockquote_text}')

            for ol in soup.find_all('ol'):
                items = ol.find_all('li')
                numbered_list = '\n'.join(f'{index + 1}. {item.get_text(strip=True)}' for index, item in enumerate(items))
                ol.replace_with(numbered_list)
            author = spots['included'][0]['attributes']['displayName']
            avatar_url = spots['included'][0]['attributes'].get('avatarUrl', None)
            
            post_time = spots['data']['attributes']['createdAt']
            post_time = datetime.fromisoformat(post_time) + timedelta(hours=3)
            formatted_time = post_time.strftime('%H:%M:%S %d-%m-%Y')

            post_content = soup.get_text(separator='\n', strip=False)
            post_end[post_id] = [author, post_content, [img['src'] for img in soup.find_all('img')], avatar_url, formatted_time]
            
        return post_end, discussion_title
    except requests.exceptions.RequestException as e:
        return None, None

def split_message(content, max_length=2000):
    if len(content) <= max_length:
        return [content]
    
    return [content[i:i + max_length] for i in range(0, len(content), max_length)]
