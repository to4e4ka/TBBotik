#from webserver import keep_alive
from modules import module_handler
from modules import module_logger
import os

import anyio
import httpx

if os.path.exists('data'):
    data = open("data", "r")
    print("File opened")
    contents = data.readlines()
    data.close()
else:
    data = open('../data', 'r')
    print('Opened outside working folder')
    contents = data.readlines()
    data.close()

secter = contents[0].strip('\n')
another = contents[1].strip('\n')


DEFAULT_USER_AGENT = 'Mozilla/5.0 (Linux; Android 13; FNE-NX9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.280 Mobile Safari/537.36 OPR/80.4.4244.77866'


def SES_PARAMS():
    """
    ОСТАВИТЬ В ВИДЕ ФУНКЦИИ!!!
    """
    return {
        'headers': httpx.Headers({
            'User-Agent': DEFAULT_USER_AGENT,
            'Connection': 'keep-alive',
        }),
        'timeout': httpx.Timeout(timeout=120.0),
        'limits': httpx.Limits(max_keepalive_connections=None, max_connections=None, keepalive_expiry=120)
    }


class VKAPI_instance:
    def __init__(self, token: str, group_id: int):
        self.token = token
        self.group_id = group_id
        self.base_url = "https://api.vk.com/method/"
        self.api_version = "5.131"
        self.ts: int | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.session: httpx.AsyncClient = httpx.AsyncClient(**SES_PARAMS())

    async def call(self, method: str, params: dict) -> dict:
        """
        Выполнение запроса к VK API
        """
        params.update({
            'access_token': self.token,
            'lang': 0
        })
        params['v'] = self.api_version if 'v' not in params.keys() else params['v']

        async def _make_call():
            r = await self.session.post(self.base_url + method, json=params)
            try:
                result = r.json()
                if 'error' in result.keys():
                    error_code = int(result['error']['error_code'])
                    error_msg = result['error']['error_msg']
                    if error_code in [6, 7, 10] and 'denied' not in error_msg:  # Нужно повторить вызов функции
                        return {'retry': True}
                    else:
                        raise RuntimeError
                return result.get('response', result)
            except:
                module_logger.Log(f"Ошибка API: {r}")
                return {}

        _delay = 1
        while True:
            response = await _make_call()
            if response.get('retry') and _delay <= 4:
                await anyio.sleep(_delay)
                _delay *= 2
                continue
            break
        return {}

    async def get_longpoll_server(self):
        params = {
            'group_id': self.group_id
        }
        response = await self.call('groups.getLongPollServer', params)
        if response:
            self.key = response['key']
            self.server = response['server']
            self.ts = response['ts']
            return True
        return False

    async def listen(self):
        if not await self.get_longpoll_server():
            module_logger.Log("Не удалось получить LongPoll сервер")
            return

        while True:
            try:
                params = {
                    'act': 'a_check',
                    'key': self.key,
                    'ts': self.ts,
                    'wait': 25
                }

                async with self.session.get(self.server, params=params) as response:
                    _data = await response.json()

                    if 'failed' in _data:
                        if _data['failed'] in [2, 3]:
                            await self.get_longpoll_server()
                        continue

                    self.ts = _data['ts']

                    for update in _data.get('updates', []):
                        await self.handle_update(update)

            except Exception as e:
                print(f"Ошибка в LongPoll: {e}")
                await anyio.sleep(1)

    async def handle_update(self, update: dict):
        update_type = update.get('type')

        if update_type == 'message_new':
            await self.handle_message(update['object'])
        elif update_type == 'wall_post_new':
            await self.handle_wall_post(update['object'])

    async def handle_message(self, message_obj: dict):
        message = message_obj['message']
        peer_id = message['peer_id']

        # Проверка на стоп-сообщение
        if peer_id in [372894745, 222366400] and message['text'] == 'stfu':
            exit()

        reply_text = ""
        if 'reply_message' in message:
            reply_text = message['reply_message']['text']

        await module_handler.handle_message(
            message['text'],
            peer_id,
            self,
            reply_text
        )

    async def handle_wall_post(self, post_obj: dict):
        if post_obj.get('post_type') == 'post':
            post_id = post_obj['id']
            await module_handler.handle_post(post_id, self)

    async def send_message(self, peer_id: int, message: str, attachment: str = ""):
        params = {
            'peer_id': peer_id,
            'message': message,
            'random_id': 0
        }
        if attachment:
            params['attachment'] = attachment

        return await self.call('messages.send', params)


class VkBotGroup:
    def __init__(self, main_token: str, reserve_token: str, group_id: int):
        self.main_bot = VKAPI_instance(main_token, group_id)
        self.reserve_bot = VKAPI_instance(reserve_token, group_id)
        self.current_bot = self.main_bot

    async def switch(self):
        self.current_bot = self.reserve_bot if self.current_bot == self.main_bot else self.main_bot

    async def listen_with_failover(self):
        while True:
            try:
                await self.current_bot.listen()
            except Exception as e:
                if str(e).__contains__("Connection aborted") or str(e).__contains__("Read timed out"):
                    await self.switch()
                    module_logger.Log("Switched key")
                else:
                    module_logger.Log("Ошибка longpoll, ждем 10 секунд...")
                    await anyio.sleep(10)
                continue


async def main():
    bot_group = VkBotGroup(secter, another, 172386457)

    print("Бот запущен...")
    await bot_group.listen_with_failover()


if __name__ == "__main__":
    anyio.run(main())
