import asyncio

import chatgpt


async def start():
    while True:
        print("AI: " + await chatgpt.ask_gpt(input("User：")))


if __name__ == "__main__":
    asyncio.run(start())
