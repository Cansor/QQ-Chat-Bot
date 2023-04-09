from .config import Config
from .utils import super_users_permission

from typing import Dict, Any
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata


__plugin_meta__ = PluginMetadata(
    name="全局设置",
    description="设置一些全局的参数、功能",
    usage="发送命令：set [参数1] [参数2]",
    config=Config,
    extra={},
)

plugin_config: Config = Config.parse_obj(get_driver().config)


@Bot.on_calling_api
async def hook_send(bot: Bot, api: str, data: Dict[str, Any]):
    """消息钩子函数，在消息发送前执行"""

    # 如果是群消息 且 启用了 at用户，则在消息前添加 at
    if data.get("message_type") == "group" and plugin_config.at_sender:
        data.get("message").insert(0, MessageSegment.at(data.get("user_id")))


cmd_set = on_command("set", aliases={"设置"}, rule=to_me(), priority=10, block=True, permission=super_users_permission)


@cmd_set.handle()
async def on_features(msg_args: Message = CommandArg()):
    """全局设置"""

    args = msg_args.extract_plain_text().strip()

    if not args:
        await cmd_set.finish("参数缺失")

    args = args.lower().split(" ")

    if args[0] == "at" or args[0] == "召唤":
        if len(args) < 2:
            await cmd_set.finish(message="参数无效")
        elif args[1] == "on" or args[1] == "启用":
            plugin_config.at_sender = True
            await cmd_set.finish(message="已启用 [@用户] 功能")
        elif args[1] == "off" or args[1] == "禁用":
            plugin_config.at_sender = False
            await cmd_set.finish(message="已禁用 [@用户] 功能")
    else:
        await cmd_set.finish('抱歉，没有这样的功能呢~')


__all__ = [
    'super_users_permission'
]
