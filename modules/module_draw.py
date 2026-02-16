import httpx
import base64
from io import BytesIO

from module_logger import Log

ENDPOINT = 'workflow/flux2_klein_t2i'


async def upload_photo_to_server(asyncHttpSession: httpx.AsyncClient, url: str, binary: bytes) -> dict:
    rq = await asyncHttpSession.post(url, files={'file': ('file.png', BytesIO(binary), 'image/png')})
    keys = ['server', 'hash', 'photo']
    return {key: rq.json().get(key) for key in keys}


async def upload_message_photo(vkApiInstance, peer_id: int, bin_photo: bytes) -> tuple[int, int]:
    try:
        _url = (await vkApiInstance.call('photos.getMessagesUploadServer', {'peer_id': peer_id}))['upload_url']
    except KeyError:
        return 0, 0
    _upload_info = await upload_photo_to_server(vkApiInstance.session, _url, bin_photo)
    _photo_info = (await vkApiInstance.call('photos.saveMessagesPhoto', _upload_info))[0]
    return _photo_info['owner_id'], _photo_info['id']


async def request_image_generation(peer_id: int, prompt: str, vkApiInstance) -> str:
    """Возвращает строку вложения, готовую к вклеиванию в сообщение"""
    try:
        response = await vkApiInstance.session.post(f'http://213.141.130.152:49205/{ENDPOINT}', json={
            'input': {'width': 1024, 'height': 1024, 'prompt': prompt}
        })
        if images := response.json().get('images'):
            photo_binary = base64.b64decode(images[0])
            oid, pid = await upload_message_photo(vkApiInstance, peer_id, photo_binary)
            if oid == pid == 0:
                Log('[J] Не удалось отправить картинку: пользователь должен разрешить сообщения в ЛС')
                return ''
            return f'photo{oid}_{pid}'
        else:
            return ''
    except httpx.HTTPError:
        Log('[J] Не удалось отправить картинку: ошибка на стороне рисовалки')
    except Exception as e:
        Log(f'[J] Не удалось отправить картинку: {e}')
    return ''
