from modules import module_logger


async def send(text, peer_id, vkApiInstance):
    await vkApiInstance.method('messages.send', {
        'peer_id': peer_id,
        'message': text,
        'random_id': 0
    })


async def send_attachment(text, peer_id, attachment, vkApiInstance):
    try:
        await vkApiInstance.method('messages.send', {
            'peer_id': peer_id,
            'message': text,
            'attachment': attachment,
            'random_id': 0
        })
    except Exception as e:
        module_logger.Log(e)


async def repost(post_id, peer_id, vkApiInstance):
    try:
        await vkApiInstance.method('messages.send', {
            'peer_id': peer_id,
            'attachment': 'wall-172386457_' + str(post_id),
            'message': 'Новый пост в группе:',
            'random_id': 0
        })
    except Exception as e:
        module_logger.Log(e)


async def kva(c, chid, vkApiInstance, replied_text=""):
    try:
        if c != 1:
            txt = 'Ква'
            attch = ''
        else:
            txt = 'Джекпот'
            attch = 'audio474499147_456517029'
        await vkApiInstance.method(
            'messages.send', {
                'peer_id': chid,
                'message': txt,
                'random_id': 0,
                'attachment': attch
            })
    except Exception as e:
        module_logger.Log(e)
