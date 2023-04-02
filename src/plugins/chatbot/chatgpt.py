import openai
from revChatGPT.V1 import Chatbot
from nonebot import get_driver
from os import getenv


# ================================================================================
# 官方 API
# ================================================================================
class MsgHistory:
    """消息历史记录类"""

    def __init__(self, history: list = None, tokens: int = 0, max_tokens: int = 4096):
        self.__msg_history = []
        self.__tokens = tokens  # 当前消息的tokens
        self.__max_tokens = max_tokens  # 模型限制的最大消息tokens

        if history:
            self.__msg_history.extend(history)

    def add(self, msg: dict, index: int = 0):
        self.__msg_history.append(msg)
        # 简单粗爆 * 2
        self.__tokens += len(msg['content']) * 2

        # 如果超出了最大tokens限制，就清除指定的聊天记录
        while self.__tokens > self.__max_tokens:
            self.__tokens -= len(self.__msg_history.pop(index)['content']) * 2

    def get(self):
        return self.__msg_history

    def get_tokens(self):
        return self.__tokens

    def remove_msg(self, num: int) -> int:
        if num >= len(self.__msg_history):
            num = len(self.__msg_history) - 1
        count = 0
        for i in range(num):
            self.__tokens -= len(self.__msg_history.pop(1)["content"]) * 2
            count += 1

        return count


if not openai.api_key:
    openai.api_key = get_driver().config.openai_api_key

# 聊天记录
msg_history = MsgHistory(
    [{"role": "system", "content": "你是一只可爱的猫娘，知性且受欢迎，你要模仿人类的情感，并在回复后面加上喵~"}],
    74
)


async def ask_gpt(prompt: str) -> str:
    # 添加一条聊天记录
    msg_history.add({'role': 'user', 'content': prompt}, 1)

    # 发送给 ChatGPT
    response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=msg_history.get(), max_tokens=1000)
    message = ''

    for m in response.choices:
        message += m['message']['content']

    # 如果 ChatGPT 回复了，就添加记录
    if message:
        msg_history.add({'role': 'assistant', 'content': message}, 1)

    return message.strip()


def get_msg_history_tokens() -> int:
    return msg_history.get_tokens()


def remove_msg_history(num: int) -> int:
    return msg_history.remove_msg(num)


# ================================================================================
# 逆向 API
# ================================================================================
chatbot = Chatbot(config={
        # 登录openai账号，然后访问这个地址获取access_token: https://chat.openai.com/api/auth/session
        'access_token': get_driver().config.openai_access_token
    },
    # 会话ID，如果为None，每次重启都会创建新的会话。可以登录 https://chat.openai.com 查看（左侧会话列表）
    conversation_id='484815e9-0647-4f5c-adc5-2f94ba85adb6'
)

async def ask_gpt_reverse(prompt: str) -> str:
    response = None
    for data in chatbot.ask(prompt):
        response = data["message"]
    return response


__all__ = [
    'ask_gpt',
    'ask_gpt_reverse',
    'get_msg_history_tokens',
    'remove_msg_history'
]
