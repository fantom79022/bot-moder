import vk_api
import settings

# процесс авторизации
if settings.acces_token() != '':
    bot = vk_api.VkApi(token=settings.acces_token())
    bot._auth_token()
elif settings.log_pass()[0] != '' and settings.log_pass()[1] != '':
    bot = vk_api.VkApi(login=settings.log_pass()[0], password=settings.log_pass()[1])
    bot.auth()
else:
    bot = None
    print("please login")

# списко айди тех, кто может карать банами
moderators = ["415754216"]


def send_msg(chat_id, text, forward_messages = None):
    """отправляет сообщения"""
    if forward_messages == None:
        bot.method("messages.send", {"message": text, "chat_id": chat_id})
    else:
        bot.method("messages.send", {"message": text, "chat_id": chat_id, "forward_messages": forward_messages})


def get_msg(bot):
    """получает обновления сообщний"""
    response = bot.method("messages.get", {"count": 1})
    if response["items"][0] and response["items"][0]["read_state"] == 0:
        print(response)
        bot.method("messages.markAsRead", {"message_ids": response["items"][0]["id"]})
        return response


def users_list(chat_id):
    """составляет список тех, кто в данный момент в беседе"""
    list_users = []
    members_list = bot.method("messages.getChatUsers", {"chat_id": str(chat_id), "fields": "first_name"})
    for user in members_list:
        list_users.append({"first_name": user["first_name"],
                           "last_name": user["last_name"],
                           "uid": user["id"],
                           "chat_id": chat_id})
    return list_users


def get_user_id(first_name, last_name, chat_id):
    """пытается найти того, кого ты дал как аргументы"""
    for user in users_list(chat_id):
        if user["first_name"] == first_name and user["last_name"] == last_name:
            return user["uid"]


def kick(chat_id, first_name = None, last_name =  None, id = None):
    """кикает"""
    if first_name != None and last_name != None:
        try:
            if get_user_id(first_name = first_name, last_name = last_name, chat_id = chat_id) != "Error 404":
                bot.method("messages.removeChatUser", {"chat_id": chat_id,
                                                       "user_id": get_user_id(first_name, last_name, chat_id)})
        except vk_api.exceptions.ApiError:
            pass
    elif id != None:
        bot.method("messages.removeChatUser", {"chat_id": chat_id,
                                               "user_id": id})

# главная часть кода (да, я горазд писать кривые (но рабочие) алгоримты
if __name__ == '__main__':
    while True:
        response = get_msg(bot)
        if response != None:
            if "кик" in response["items"][0]["body"].lower():
                chat_id = response["items"][0]["chat_id"]
                if str(response["items"][0]["user_id"]) in moderators:
                    body = response["items"][0]["body"]
                    body = body.split(' ')
                    if len(body) >= 3:
                        kick(first_name= body[1], last_name= body[2], chat_id = chat_id)
                    elif len(body) == 2:
                        kick(id = body[1], chat_id = chat_id)
                else:
                    send_msg(chat_id, text = "У тебя нет прав на это")