from nonebot import get_driver, logger
import subprocess
import requests
from time import sleep


server_url = get_driver().config.node_chat_api_server_url


class User:
    def __init__(self, jailbreak=True, sourceAttributions=True):
        self.jailbreak = jailbreak  # 是否开启越狱模式
        self.sourceAttributions = sourceAttributions  # 是否在回复的消息中展示参考来源
        self.msg_count = 0  # 消息数量记录
        # 发送的消息对象
        self.message = {
            "jailbreakConversationId": self.jailbreak,
        }

    def __str__(self):
        return "jailbreak: %s, sourceAttributions: %s, msg_count: %d, message: {%s}"\
            % (self.jailbreak, self.sourceAttributions, self.msg_count, self.message)


session_store: dict[int, User] = dict()


async def ask_bing(user_id: int, prompt: str) -> str | None:
    user = session_store.setdefault(user_id, User())

    # sudo 时重置对话
    if prompt == 'sudo':
        reset_msg(user)
        user.message["message"] = "你好"
    # reset 时仅重置对话而不发送消息
    elif prompt == 'reset':
        reset_msg(user)
        return "已重置，下次发送消息将开启一个新的对话"

    # 获取消息数量
    elif prompt == 'msg':
        return f"当前聊天记录：{user.msg_count} 条"
    else:
        user.message["message"] = prompt

    count = 0
    response = None

    # 网络连接异常时，将重试 5 次重连
    while count < 5:
        try:
            response = requests.post(server_url, json=user.message)
            break
        except requests.exceptions.ConnectionError as e:
            sleep(1)
            count += 1
            logger.error(e)

    if not response:
        return None

    # 获取响应的Json内容，是一个字典
    result = response.json()
    # print("Response content: ", result, "\n")

    # 这段代码是自已改的 node-chatgpt-api 异常返回内容，官方没有
    if result.get("error"):
        return f"%s: %s" % (result.get("name"), result.get("message"))

    user.message["conversationId"] = result.get("conversationId")

    if user.jailbreak:
        user.message["parentMessageId"] = result.get("messageId")
        # 记录下越狱ID，否则没有记忆
        user.message["jailbreakConversationId"] = result.get("jailbreakConversationId")
    else:
        user.message["conversationSignature"] = result.get("conversationSignature")
        user.message["invocationId"] = result.get("invocationId")
        user.message["clientId"] = result.get("clientId")

    # 消息正文
    res_str = result.get("response")

    if user.sourceAttributions:
        # 在消息中加上参考来源
        source_attributions = result.get("details").get("sourceAttributions")
        if source_attributions:
            res_str += "\n"
            index = 1
            for source in source_attributions:
                res_str += "\n%d. [%s] %s" % (index, source.get("providerDisplayName"), source.get("seeMoreUrl"))
                index += 1

    # 提问+响应
    user.msg_count += 2
    
    return res_str


def reset_msg(user: User):
    """重置消息参数"""

    user.msg_count = 0
    user.message = {"jailbreakConversationId": user.jailbreak}


def clear_msg():
    """清空所有会话消息"""

    session_store.clear()


def restart_server():
    """执行shell脚本重启服务"""

    command = get_driver().config.node_chat_api_restart_script
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    sleep(1.5)


def switch_source_attributions(user_id: int, flag: bool):
    session_store.setdefault(user_id, User(sourceAttributions=flag)).sourceAttributions = flag


def switch_jailbreak(user_id: int, flag: bool):
    session_store.setdefault(user_id, User(jailbreak=flag)).jailbreak = flag


__all__ = [
    'ask_bing',
    'switch_jailbreak',
    'restart_server',
    'clear_msg',
    'switch_source_attributions'
]
