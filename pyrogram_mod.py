import asyncio
import functools
import pyrogram
from pyrogram import *

loop = asyncio.get_event_loop()

class Client(Client):
    def __init__(self, *args, **kwargs):
        print('Client.__init__ called')
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
        print('Future done')
        if future == self.deferred_listeners[chat_id]:
            self.deferred_listeners.pop(chat_id, None)

class MessageHandler(MessageHandler):
	def __init__(self, callback: callable, filters=None):
		self.user_callback = callback
		super().__init__(self.retrieveListener, filters)
	
	async def retrieveListener(self, client, message, *args):
		print('retrieveListener called with text ', message.text)
		print('message.chat', message.chat)
		print('message.chat.id', message.chat.id)
		print('message.chat.id in client.deferred_listeners', message.chat.id in client.deferred_listeners)
		print('client.deferred_listeners', client.deferred_listeners)
		if message.chat and message.chat.id in client.deferred_listeners:
			print('Setting result')
			client.deferred_listeners[message.chat.id]['future'].set_result(message)
		else:
			await self.user_callback(client, message, *args)

pyrogram.client.client.Client = Client
pyrogram.MessageHandler = pyrogram.client.handlers.MessageHandler = pyrogram.client.handlers.message_handler.MessageHandler = MessageHandler