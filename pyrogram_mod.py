import asyncio
import functools
import pyrogram
from pyrogram import *

loop = asyncio.get_event_loop()

class Client(Client):
    def __init__(self, *args, **kwargs):
        self.deferred_listeners = {}
        
        super().__init__(*args, **kwargs)

    def listen(self, chat_id, timeout=300):
        future = loop.create_future()
        future.add_done_callback(
            functools.partial(self.remove_future, chat_id)
        )
        self.deferred_listeners.update(
            {chat_id: {"future": future}}
        )
        return asyncio.wait_for(future, timeout)
        
    def remove_future(self, chat_id, future):
        if future == self.deferred_listeners[chat_id]:
            self.deferred_listeners.pop(chat_id, None)

class MessageHandler(MessageHandler):
	def __init__(self, callback: callable, filters=None):
		print('pyrogram_mod.MessageHandler initiated')
		super().__init__(functools.partial(self.retrieveListener, callback), filters)
	
	def retrieveListener(self, callback, client, message, *args):
		print('pyrogram_mod.MessageHandler.retrieveListener called')
		if message.chat and message.chat.id in client.deferred_listeners:
			client.deferred_listeners[message.chat.id]['future'].set_result(message)
		else:
			callback(client, message, *args)

pyrogram.client.client.Client = Client
pyrogram.client.handlers.message_handler.MessageHandler = MessageHandler