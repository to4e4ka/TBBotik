from modules import module_commands
from modules import module_send
from modules import module_draw
import re


async def handle_message(text: str, peer_id, vkApiInstance, replied_text=""):
    RE_PROMPT = re.compile(r'/ig (.{3,})')
    if match := RE_PROMPT.match(text):
        prompt = match.groups()[0]
        img_data = await module_draw.request_image_generation(peer_id, prompt, vkApiInstance)
        if img_data:
            await module_send.send_attachment('', peer_id, img_data, vkApiInstance)
        else:
            await module_send.send('Проверьте логи: не удалось получить результат генерации', peer_id, vkApiInstance)

    parsed = str(text).split(' ')
    if parsed[0].lower() in module_commands.commands:
        await module_commands.commands[parsed[0].lower()](text, peer_id, vkApiInstance, replied_text)
    elif text[:3].lower() == 'ква':
        await module_commands.commands[text[:3].lower()](text, peer_id, vkApiInstance, replied_text)


async def handle_post(post_id, vkApiInstance):
    await module_commands.func_repost(post_id, vkApiInstance)
