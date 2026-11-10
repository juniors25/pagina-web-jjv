"""Publica en Instagram el post del día según social/calendario.json.

Variables de entorno: IG_ACCESS_TOKEN, IG_USER_ID, IMAGE_BASE_URL (opcional),
FECHA (opcional, YYYY-MM-DD), DRY_RUN=1 para no publicar.
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

API = 'https://graph.instagram.com/v21.0'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get('IMAGE_BASE_URL', 'https://raw.githubusercontent.com/juniors25/pagina-web-jjv/master/')


def post(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode())
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def get(url, params):
    with urllib.request.urlopen(url + '?' + urllib.parse.urlencode(params)) as r:
        return json.load(r)


def main():
    fecha = os.environ.get('FECHA') or dt.datetime.now(ZoneInfo('America/Argentina/Mendoza')).date().isoformat()
    with open(os.path.join(ROOT, 'social', 'calendario.json'), encoding='utf-8') as f:
        items = [i for i in json.load(f) if i['fecha'] == fecha]
    if not items:
        print(f'No hay publicación programada para {fecha}')
        return
    for item in items:
        image_url = BASE + item['imagen']
        print(f'{fecha}: {image_url}')
        if os.environ.get('DRY_RUN') == '1':
            print(item['texto'])
            continue
        token, user = os.environ['IG_ACCESS_TOKEN'], os.environ['IG_USER_ID']
        container = post(f'{API}/{user}/media', {'image_url': image_url, 'caption': item['texto'], 'access_token': token})['id']
        for _ in range(30):
            status = get(f'{API}/{container}', {'fields': 'status_code', 'access_token': token})['status_code']
            if status == 'FINISHED':
                break
            if status in ('ERROR', 'EXPIRED'):
                sys.exit(f'Error en el contenedor {container}: {status}')
            time.sleep(5)
        media = post(f'{API}/{user}/media_publish', {'creation_id': container, 'access_token': token})['id']
        print(f'Publicado: {media}')


if __name__ == '__main__':
    main()
