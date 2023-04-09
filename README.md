# QQ-Chat-Bot
一个基于[NoneBot2](https://github.com/nonebot/nonebot2)的ChatGPT和NewBing的AI聊天的实现，用于搭建QQ机器人。


需要配置以下环境并运行来配合使用：
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
- [node-chat-api](https://github.com/waylaidwanderer/node-chatgpt-api) (BingAI服务端)

### 配置
对于 ChatGPT，需要把Key添加到 .evn 配置文件中或者系统环境变量中（根据[NoneBot2文档](https://v2.nonebot.dev/docs/appendices/config#系统环境变量)，同名环境变量会覆盖.env文件中的配置）。

### 两个插件的命令：

chatbot 插件
```
chatbot [args]...
# 该命令需要超级用户权限，在 .env 文件中的 SUPERUSERS 配置

- on|off | 启用|禁用    启用或禁用ChatBot
- group | 群组    查看群组黑名单
- [group | 群组] [群号]    添加或移除群组黑名单
- [blacklist | 黑名单]    查看用户黑名单
- [blacklist | 黑名单] [QQ号]    添加或移除用户黑名单
- [api] [0|1|2]    切换API：0-ChatGPT官方API，1-ChatGPT逆向API(revChatGPT)，2-NewBing API(node-chat-api)
- tokens    ChatGPT(官方API)的当前上下文tokens（简单粗暴“字符*2”的计算方式）
- [delete | 删除记录] [n]    删除ChatGPT(官方API)最早的 n 条记录


bing [args]...
# 该命令仅用于 NewBing API (chatbot api 2)

- [jailbreak | 越狱] [on|off | 启用|禁用]    启用或禁用越狱模式
- restart | 重启    重启 node-chat-api 服务
- [source | 参考来源] [on|off | 启用|禁用]    启用或禁用在消息末尾添加参考来源


另外，在 NewBing API 下，可以直接发送以下文字来达到相应效果（这不属于命令）：
- 发送 sudo 或 reset 来重置对话。
- 发送 msg 来查询当前的聊天记录数量。
```


global_setting 插件
```
set|设置 [args]...
# 该命令需要超级用户权限，在 .env 文件中的 SUPERUSERS 配置

- [at | 召唤] [on|off | 启用|禁用]    启用或禁用在发送消息时 @用户
```


## 安装
Python最低要求版本：Python3.9

至少需要安装以下依赖：

nonebot2 以及驱动器
```shell
pip install 'nonebot2[fastapi]'
```

适配器
```shell
pip install nonebot-adapter-onebot
```

OpenAI
```shell
pip install openai
```

revChatGPT
```shell
pip install --upgrade revChatGPT
```

## 启动

1. 使用 nb-cli 启动 `nb run --reload`
2. 使用 Python 启动 `python3 bot.py`

如果要使用`nb`命令，还需要安装NoneBot2的脚手架*nb-cli*，这部分内容请参考NoneBot2官方文档。

---

更多信息请参考：
- [NoneBot2 文档](https://v2.nonebot.dev/)
- [go-cqhttp 帮助中心](https://docs.go-cqhttp.org/)
- [revChatGPT](https://github.com/acheong08/ChatGPT)