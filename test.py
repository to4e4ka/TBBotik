"""from vk_api.utils import get_random_id

import vk_api

data = open("data", "r")
print("File opened")
contents = data.readlines()
data.close()
print("Closed")

secter = contents[0].strip('\n')
another = contents[1].strip('\n')

session = vk_api.VkApi(token=str(secter))

zalupa = session.method('messages.getConversations', {
    'group_id': 172386457,
    'filter': 'all'
})['items']

for hair in zalupa:
    if hair['conversation']['peer']['type'] == 'chat' and hair['conversation']['chat_settings']['title'].__contains__('Флуд'):
        print(hair['conversation']['peer']['id'])"""
