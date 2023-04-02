from nonebot.adapters.onebot.v11 import Bot, MessageEvent


async def super_users_permission(event: MessageEvent, bot: Bot) -> bool:
    """权限控制：仅允许超级用户（Config 中的 SUPERUSERS）"""

    # if str(event.user_id) in bot.config.superusers:
    #     return True
    # 发送消息
    # await bot.send(event, '抱歉，我只听主人的命令哦~')
    # return False
    return str(event.user_id) in bot.config.superusers


__all__ = [
    'super_users_permission'
]
