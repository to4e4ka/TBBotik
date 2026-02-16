import random
import re
from modules import module_util
from modules import module_process
from modules import module_send


async def HeavyFunc_Resources(text, peer_id, vk_session, replied_text=""):
    spacebar = text.find(' ')
    if spacebar > -1:
        resources = module_process.generate_resources(text[spacebar + 1:].lower())
        resources = module_process.resource_string_format(resources)
        await module_send.send(resources, peer_id, vk_session)


async def HeavyFunc_Ingredients(text, peer_id, vk_session, replied_text=""):
    spacebar = text.find(' ')
    if spacebar > -1:
        ingredients = module_process.generate_ingredients(text[spacebar + 1:].lower())
        ingredients = module_process.resource_string_format(ingredients)
        await module_send.send(ingredients, peer_id, vk_session)


async def HeavyFunc_Koobrii(text, peer_id, vk_session, replied_text=""):
    if text[7:].isdigit():
        amount = module_process.generate_koobrii(int(text[7:]))
        await module_send.send('Осколки кубрия х{0}'.format(amount), peer_id, vk_session)


async def Func_Counter(text, peer_id, vk_session, replied_text=""):
    if replied_text != "":
        spacebar = text.find(' ')
        if spacebar > -1:
            pattern = text[spacebar + 1:]
            if pattern.isnumeric():
                pattern = f' {pattern} '
            respond = module_util.count(replied_text, pattern)
            await module_send.send(respond, peer_id, vk_session)


async def HeavyFunc_Random(text, peer_id, vk_session, replied_text=""):
    checking = text.split(' ')
    edge = list(map(int, re.findall(r'\d+', text)))
    if (len(edge) == 1) and (len(checking) == 2):
        e1 = edge[0]
        await module_send.send(
            '!Случайное число из диапазона [' + '0' + '...' + str(e1) +
            '] выпало на ' + str(random.randint(0, e1)), peer_id, vk_session)
    elif (len(edge) == 2) and (len(checking) == 3):
        e1 = edge[0]
        e2 = edge[1]
        await module_send.send(
            '!Случайное число из диапазона [' + str(e1) + '...' + str(e2) +
            '] выпало на ' + str(random.randint(e1, e2)), peer_id, vk_session)
    elif (len(edge) == 3) and (len(checking) == 4):
        e1 = edge[0]
        e2 = edge[1]
        e3 = edge[2]
        if e1 > 250:
            e1 = 250
        if e2 > 1000:
            e2 = 1000
        if e3 > 1000:
            e3 = 1000
        temp = random.randint(e2, e3)
        n_sum = temp
        num_list = str(temp)
        for i in range(e1 - 1):
            temp = random.randint(e2, e3)
            n_sum += temp
            num_list += " + " + str(temp)

        await module_send.send(
            '!Случайные числа из диапазона [' + str(e2) + '...' + str(e3) +
            '] выпали на (' + num_list + ') = ' + str(n_sum), peer_id, vk_session)


async def Func_Kva(text, peer_id, vk_session, replied_text=""):
    await module_send.kva(random.randint(1, 100), peer_id, vk_session)


async def func_repost(post_id, vk_session, peer_id=2000000014):
    await module_send.repost(post_id, peer_id, vk_session)


async def Func_rules(param, peer_id, session, replied_text=""):
    spacebar = param.find(' ')
    if spacebar > -1:
        param = param[param.find(' ') + 1:]
        rule = module_util.getrule(param)
    else:
        rule = module_util.getrule('все')
    if param is not None:
        await module_send.send(rule, peer_id, session)


async def Func_shop(name, peer_id, session, replied_text=""):
    spacebar = name.find(' ')
    if spacebar > -1:
        name = name[name.find(' ') + 1:]
        shop, image = module_util.readshop(name)
        image = 'photo-172386457_' + image
        await module_send.send_attachment(shop, peer_id, image, session)


commands = {
    'ква': Func_Kva,
    'ингры': HeavyFunc_Ingredients,
    'ресы': HeavyFunc_Resources,
    'рандом': HeavyFunc_Random,
    'кубрий': HeavyFunc_Koobrii,
    'счёт': Func_Counter,
    'счет': Func_Counter,
    'правила': Func_rules,
    'магазин': Func_shop
}

