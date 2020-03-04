import asyncio
import functools
import pyrogram
from pyrogram import *

loop = asyncio.get_event_loop()

class Client(Client):
    def __init__(self, *args, **kwargs):
        # print('Client.__init__ called')
        self.deferred_listeners = {}
        
        super().__init__(*args, **kwargs)

    async def listen(self, chat_id, filters=None, timeout=300):
        chat = await self.get_chat(chat_id)
        chat_id = chat.id
        
        future = loop.create_future()
        future.add_done_callback(
            functools.partial(self.clearListener, chat_id)
        )
        self.deferred_listeners.update(
            {chat_id: {"future": future, "filters": filters}}
        )
        return await asyncio.wait_for(future, timeout)
        
    def clearListener(self, chat_id, future):
        # print('Future done')
        if future == self.deferred_listeners[chat_id]:
            self.deferred_listeners.pop(chat_id, None)

class MessageHandler(MessageHandler):
    def __init__(self, callback: callable, filters=None):
        self.user_callback = callback
        super().__init__(self.resolveListener, filters)
    
    async def resolveListener(self, client, message, *args):
        """
        print('resolveListener called with text ', message.text)
        print('message.chat', message.chat)
        print('message.chat.id', message.chat.id)
        print('message.chat.id in client.deferred_listeners', message.chat.id in client.deferred_listeners)
        print('client.deferred_listeners', client.deferred_listeners)
        """
        
        future_exists = message.chat.id in client.deferred_listeners
        if future_exists and not client.deferred_listeners[message.chat.id]['future'].done():
            # print('Setting result')
            client.deferred_listeners[message.chat.id]['future'].set_result(message)
        else:
            if future_exists and client.deferred_listeners[message.chat.id]['future'].done():
                client.clearListener(message.chat.id, client.deferred_listeners[message.chat.id]['future'])
            await self.user_callback(client, message, *args)
            
    def check(self, update):
        client = update._client
        listener = client.deferred_listeners[update.chat.id] if update.chat.id in client.deferred_listeners else None
        if listener and not listener['future'].done() and (listener['filters'](update) if callable(listener['filters']) else True):
            return True
            
        return (
            self.filters(update)
            if callable(self.filters)
            else True
        )

class Chat(Chat):
    def listen(self, *args, **kwargs):
        return self._client.listen(self.id, *args, **kwargs)

class User(User):
    def listen(self, *args, **kwargs):
        return self._client.listen(self.id, *args, **kwargs)


pyrogram.Client = pyrogram.client.Client = pyrogram.client.client.Client = Client
pyrogram.MessageHandler = pyrogram.client.handlers.MessageHandler = pyrogram.client.handlers.message_handler.MessageHandler = MessageHandler
pyrogram.User = pyrogram.client.types.User = pyrogram.client.types.user_and_chats.User = pyrogram.client.types.user_and_chats.user.User = User
pyrogram.Chat = pyrogram.client.types.Chat = pyrogram.client.types.user_and_chats.Chat = pyrogram.client.types.user_and_chats.chat.Chat = Chat
