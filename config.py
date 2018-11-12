from pyrogram import Client, Filters
import redis

app = Client("my_account")
db = redis.StrictRedis(host='localhost', port=6379, db=0)
sudos = [652890017,200097591,123892996]
keys = {
	'screenshots':'', #Obtenha uma key em https://thumbnail.ws
	'yandex':'' #Obtenha uma key em https://tech.yandex.com/translate
}