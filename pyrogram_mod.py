import asyncio
import functools
import pyrogram
from pyrogram import *

loop = asyncio.get_event_loop()

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
        
class Client(Client):
    def __init__(self, *args, **kwargs):
        # print('Client.__init__ called')
        self.deferred_listeners = AttrDict()
        
        super().__init__(*args, **kwargs)

    def listen(self, chat_id, filters=None, timeout=300):
        future = loop.create_future()
        future.add_done_callback(
            functools.partial(self.clearListener, chat_id)
        )
        self.deferred_listeners.update(
            {chat_id: {"future": future, "filters": filters}}
        )
        return asyncio.wait_for(future, timeout)
        
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
        listener = client.deferred_listeners[update.chat.id] if update.chat.id in client.deferred_listeners else None
        if listener and not listener.future.done() and (listener.filters(update) if callable(listener.filters) else True):
            return True
            
        return (
            self.filters(update)
            if callable(self.filters)
            else True
        )

pyrogram.client.client.Client = Client
pyrogram.MessageHandler = pyrogram.client.handlers.MessageHandler = pyrogram.client.handlers.message_handler.MessageHandler = MessageHandler