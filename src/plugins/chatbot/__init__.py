from nonebot import logger, on_message, on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata

from .chatgpt import *
from .new_bing import *
from ..global_setting import super_users_permission


__plugin_meta__ = PluginMetadata(
    name="ChatAI",
    description="ChatGPT和Bing聊天机器人",
    usage="直接@聊天即可",
    extra={},
)

chat_bot_type = 2
switch_chat = True
# 群组黑名单
group_blacklist = []
# 用户黑名单
user_blacklist = []


def get_user_id(event: MessageEvent) -> int:
    """获取用户ID，一个群视为一个用户"""

    return event.__getattribute__("group_id") if event.message_type == "group" else event.user_id


async def permission_handler(event: MessageEvent) -> bool:
    """ 权限处理，配置可以触发 Chat 的消息来源类型 """

    flag_group = False
    flag_private = False
    # 是否在群组黑名单中
    if event.message_type == "group" and (group_id := event.__getattribute__("group_id")):
        flag_group = group_id not in group_blacklist
    # 是否是好友私聊
    elif event.message_type == "private" and event.sub_type == "friend":
        flag_private = True

    # 允许条件为：已启用机器人 且 不在群组黑名单中或好友私聊 且 用户不在黑名单中
    return switch_chat and (flag_group or flag_private) and event.get_user_id not in user_blacklist


on_msg = on_message(rule=to_me(), priority=100, permission=permission_handler)


@on_msg.handle()
async def chat_bot(event: MessageEvent):
    """聊天机器人"""

    msg_qq = event.get_message().extract_plain_text().strip()  # 获取消息纯文本内容，不包含CQ码
    msg_result = None

    # ChatGPT 官方 API
    if chat_bot_type == 0:
        try:
            msg_result = await ask_gpt(msg_qq)
        except Exception:
            await on_msg.finish("ChatGPT 好像异常了！")
    # ChatGPT 逆向 API
    elif chat_bot_type == 1:
        try:
            msg_result = await ask_gpt_reverse(msg_qq)
        except Exception:
            await on_msg.finish("ChatGPT 好像异常了！")
    # ChatBing API
    elif chat_bot_type == 2:
        try:
            msg_result = await ask_bing(get_user_id(event), msg_qq)
        except Exception:
            await on_msg.finish("Error")

    # 发送（回复）QQ消息
    if msg_result:
        await on_msg.finish(msg_result)
    else:
        logger.info("Result message is None")


cmd_chat = on_command("chatbot", rule=to_me(), priority=10, block=True, permission=super_users_permission)


@cmd_chat.handle()
async def chat_command(msg_args: Message = CommandArg()):
    global switch_chat, chat_bot_type

    args = msg_args.extract_plain_text().strip()
    if not args:
        await cmd_chat.finish("参数缺失")

    args = args.lower().split(' ')

    if args[0] == 'on' or args[0] == '启用':
        switch_chat = True
        await cmd_chat.finish(message='ChatBot 已启用')

    elif args[0] == 'off' or args[0] == '禁用':
        switch_chat = False
        await cmd_chat.finish(message='ChatBot 已禁用')

    elif args[0] == 'group' or args[0] == '群组':
        # 如果小于两个参数，则查询群组列表，否则继续执行
        if len(args) < 2:
            msg = '【群组黑名单】\n'
            for gid in group_blacklist:
                msg += '%d\n' % gid

            await cmd_chat.finish(msg)
        else:
            group_id = int(args[1])
            # 有则移除，无则添加
            if group_id in group_blacklist:
                group_blacklist.remove(group_id)
                await cmd_chat.finish('已移除群组：%d' % group_id)
            else:
                group_blacklist.append(group_id)
                await cmd_chat.finish('已添加群组：%d' % group_id)

    elif args[0] == 'blacklist' or args[0] == '黑名单':
        # 如果小于两个参数，则查询黑名单列表，否则继续执行
        if len(args) < 2:
            msg = '【用户黑名单】\n'
            for qid in user_blacklist:
                msg += '%d\n' % qid

            await cmd_chat.finish(msg)
        else:
            qq_id = int(args[1])
            # 有则移除，无则添加
            if qq_id in user_blacklist:
                user_blacklist.remove(qq_id)
                await cmd_chat.finish('已移除黑名单：%d' % qq_id)
            else:
                user_blacklist.append(qq_id)
                await cmd_chat.finish('已添加黑名单：%d' % qq_id)

    elif args[0] == 'api' or args[0] == '切换':
        if len(args) < 2:
            await cmd_chat.finish("无效命令，参数不完整")
        else:
            number = int(args[1])
            if number > 2:
                await cmd_chat.finish("参数无效")
                return

            chat_bot_type = number
            msg = ''
            if chat_bot_type == 0:
                msg = 'ChatGPT 官方 API'
            elif chat_bot_type == 1:
                msg = 'ChatGPT 逆向 API'
            elif chat_bot_type == 2:
                msg = 'New Bing API'

            await cmd_chat.finish(f'已切换至：{msg}')

    elif args[0] == 'tokens':
        await cmd_chat.finish(f"ChatGPT的当前上下文tokens：{get_msg_history_tokens()}")

    elif args[0] == "delete" or args[0] == "删除记录":
        if len(args) < 2:
            await cmd_chat.finish("无效命令，参数不完整")
        else:
            number = int(args[1])
            await cmd_chat.finish(f'已清除 {remove_msg_history(number)} 条聊天记录')

    else:
        await cmd_chat.finish('没有这个命令')


cmd_bing = on_command("bing", rule=to_me(), priority=10, block=True, permission=permission_handler)


@cmd_bing.handle()
async def bing_command(event: MessageEvent, msg_args: Message = CommandArg()):
    """ChatBing 的一些命令"""

    args = msg_args.extract_plain_text().strip()
    if not args:
        await cmd_bing.finish("参数缺失")

    args = args.strip().split(' ')

    if args[0] == "jailbreak" or args[0] == "越狱":
        if len(args) < 2:
            await cmd_bing.finish('无效命令，请指定参数')
        elif args[1] == "on" or args[1] == "启用":
            switch_jailbreak(get_user_id(event), True)
            await cmd_bing.finish('已启用越狱模式')
        elif args[1] == "off" or args[1] == "禁用":
            switch_jailbreak(get_user_id(event), False)
            await cmd_bing.finish('已禁用越狱模式')
        else:
            await cmd_bing.finish('参数无效')

    elif args[0] == "restart" or args[0] == "重启":
        try:
            restart_server()
        except Exception as e:
            logger.error(e)
            await cmd_bing.finish('重启失败')
            return

        if len(args) > 1:
            await ask_bing(get_user_id(event), "reset")
            await cmd_bing.finish(await ask_bing(get_user_id(event), args[1]))
        else:
            await cmd_bing.finish("已重启服务")

    elif args[0] == "source" or args[0] == "参考来源":
        if len(args) < 2:
            await cmd_bing.finish('无效命令，请指定参数')
        elif args[1] == "on" or args[1] == "启用":
            switch_source_attributions(get_user_id(event), True)
            await cmd_bing.finish('已启用参考来源')
        elif args[1] == "off" or args[1] == "禁用":
            switch_source_attributions(get_user_id(event), False)
            await cmd_bing.finish('已禁用参考来源')
        else:
            await cmd_bing.finish('参数无效')

    else:
        await cmd_bing.finish('无效命令')


__all__ = []
