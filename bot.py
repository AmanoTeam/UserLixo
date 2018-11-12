import config
import threading
import io
import urllib
import os
import time
import subprocess
from plugns import youtube
from plugns import traduzir
from contextlib import redirect_stdout
from pyrogram import Client, Filters

app = config.app

def exec_thread(target, *args, **kwargs):
	t = threading.Thread(target=target, args=args, kwargs=kwargs)
	t.daemon = True
	t.start()

@app.on_message(Filters.new_chat_members)
def welcome(client, message):
	if message.from_user.id == client.get_me().id:
		client.send_message(message.chat.id, 'Coé rapazeada',reply_to_message_id=message.message_id,disable_web_page_preview=True)
	else:
		welcome = config.db.hget('welcomeee', message.chat.id)
		try:
			client.send_sticker(message.chat.id,welcome.decode('utf-8'),reply_to_message_id=message.message_id)
		except:
			new_members = "".join([
				"[{}](tg://user?id={})".format(i.first_name, i.id)
				for i in message.new_chat_members
			])
			if welcome != None:
				welcome = welcome.decode('utf-8').replace('$name',new_members).replace('$title',message.chat.title)
			else:
				welcome = "Olá {}, seja bem-vindo ao **{}**!".format(new_members,message.chat.title)
			client.send_message(message.chat.id,welcome,reply_to_message_id=message.message_id,disable_web_page_preview=True)

@app.on_message(Filters.text)
def echo(client, message):
	if message.text.lower() == '/ping' or message.text.lower() == '!ping' or message.text.lower() == 'ping':
		first_time = time.time()
		sent = client.send_message(message.chat.id,'**Pong!**',reply_to_message_id=message.message_id)
		second_time = time.time()
		client.edit_message_text(message.chat.id, sent.message_id,'**Pong!** `{}`s'.format(str(second_time - first_time)[:5]))
	if message.text.startswith('/print ') or message.text.startswith('!print '):
		try:
			client.send_photo(message.chat.id, f"https://api.thumbnail.ws/api/{config.keys['screenshots']}/thumbnail/get?url={urllib.parse.quote_plus(message.text[7:])}&width=1280",reply_to_message_id=message.message_id)
		except Exception as e:
			client.send_message(message.chat.id, f'Ocorreu um erro ao enviar a print, favor tente mais tarde.\nDescrição do erro: {e}',reply_to_message_id=message.message_id)
	if message.text.startswith('/ytdlv'):
		exec_thread(youtube.ytdlv,message,client)
	if message.text.startswith('/eval '):
		if message.from_user.id in config.sudos:
			md = str(eval(message.text[6:]))
			client.send_message(message.chat.id,md,reply_to_message_id=message.message_id)
	if message.text.startswith('/exec'):
		if message.from_user.id in config.sudos:
			try:
				with io.StringIO() as buf, redirect_stdout(buf):
					exec(message.text[6:])
					res = buf.getvalue()
			except Exception as e:
				res = 'Erro: {}: {}'.format(type(e).__name__, e)
			if len(res) < 1:
				res = 'Código sem retornos.' 
			client.send_message(message.chat.id, res, reply_to_message_id=message.message_id)
	if message.text.startswith('!backup'):
		if message.from_user.id in config.sudos:
			hora = str(int(time.time()))
			sent = client.send_message(chat_id=message.chat.id,text='OK...',reply_to_message_id=message.message_id)
			os.system('tar -czf backup-' + hora + '-{}-.tar.gz --exclude my_account.session *'.format(client.get_me().first_name))
			chat_id = message.chat.id
			if 'privado' in message.text or 'pv' in message.text:
				chat_id = message.from_user.id
			client.send_document(chat_id=chat_id,document='backup-' + hora + '-{}-.tar.gz'.format(client.get_me().first_name))
			os.remove('backup-' + hora + '-{}-.tar.gz'.format(client.get_me().first_name))
			client.edit_message_text(message.chat.id, sent.message_id,text='Concluído')
	if message.text.startswith('/tr'):
		exec_thread(traduzir.traduzir, message, client)
	if message.text.startswith('/text'):
		if message.from_user.id in config.sudos:
			text = message.text[6:].replace(' ','|')
			a = len(text)
			b = 1
			if message.from_user.id == client.get_me().id:
				edit = message.message_id
			else:
				edit = client.send_message(message.chat.id,'aguarde...').message_id
			time.sleep(1)
			for i in range(a):
				if a == True:
					b -= 1
					client.edit_message_text(message.chat.id, edit, text[:b].replace('|',' ')+'|')
					time.sleep(0.5)
					client.edit_message_text(message.chat.id, edit, text[:b].replace('|',' '))
					time.sleep(0.5)
					b += 1
					a == False
				try:
					client.edit_message_text(message.chat.id, edit, text[:b].replace('|',' '))
				except:
					pass
				b += 1
				a = True
				time.sleep(0.5)
	if message.text.startswith('!doc'):
		if message.from_user.id in config.sudos:
			file = message.text[5:]
			try:
				client.send_document(message.chat.id,file)
			except FileNotFoundError:
				client.send_message(message.chat.id,'arquivo não encontrado.',reply_to_message_id=message.message_id)
			except Exception as erro:
				client.send_message(message.chat.id,'Ocorreu um erro ao enviar o arquivo.\nErro: {}'.format(erro),reply_to_message_id=message.message_id)
	if message.text.startswith('!cmd'):
		if message.from_user.id in config.sudos:
			text = message.text[5:]
			res = subprocess.getstatusoutput(text)[1]
			if res != '':
				client.send_message(chat_id=message.chat.id,text=res,reply_to_message_id=message.message_id)
			else:
				client.send_message(chat_id=message.message_id,text='O comando foi executado',reply_to_message_id=message.message_id)
	if message.text.startswith('/save'):
		if message.from_user.id in config.sudos:
			frase = message.text[6:]
			oi = ''
			try:
				sent = client.forward_messages(message.from_user.id,message.chat.id,message.reply_to_message.message_id)
				oi = 'sussesso'
			except:
				pass
			if frase != '':
				if oi != '':
					client.send_message(message.from_user.id,frase,reply_to_message_id=sent.message_id)
				else:
					client.send_message(message.from_user.id,frase)
			client.send_message(message.chat.id,'sussesso',reply_to_message_id=message.message_id)
	if message.text.startswith('/welcome'):
		try:
			config.db.hset('welcomeee',message.chat.id,message.reply_to_message.sticker.file_id)
			kk = 'sucesso'
		except:
			text = message.text[9:]
			try:
				config.db.hset('welcomeee',message.chat.id,text)
				kk = 'sucesso'
			except Exception as erro:
				print(erro)
				kk = 'erro'
		client.send_message(message.chat.id,kk,reply_to_message_id=message.message_id)
	if message.text == '/suco':
		if message.from_user.id in config.sudos:
			l = '✅'
		else:
			l = '❌'
		client.send_message(message.chat.id,l+'🍹',reply_to_message_id=message.message_id)
	if message.text.lower() == 'rt':
		first_name = message.from_user.first_name
		nome = message.reply_to_message.from_user.first_name
		mensagem = message.reply_to_message.text
		if mensagem == None:
			mensagem = message.reply_to_message.caption
		client.send_message(message.chat.id,'''**{}** concorda com **{}**:

**{}**: __{}__'''.format(first_name,nome,nome,mensagem),reply_to_message_id=message.message_id)

app.run()
