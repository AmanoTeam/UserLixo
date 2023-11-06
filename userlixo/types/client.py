import pyrogram


class Client(pyrogram.client.Client):
    me: pyrogram.types.User
    assistant: pyrogram.client.Client
