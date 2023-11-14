import dicioinformal
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from config import bot
from locales import use_lang

@Client.on_message(filters.command("dicio", prefixes=".") & filters.sudoers)
@use_lang()
async def dicio(c: Client, m: Message, t):
    text = m.text.split(" ", 1)[1]
    responses = dicioinformal.definicao(text)["results"]

    if len(responses)>=1:
        keyb = [[(resp["title"], f"dicio_{text}_{i}"), (resp["tit"][:20], f"dicio_{text}_{i}")] for i, resp in enumerate(responses)]
        print(keyb)
        await m.reply(t("choose_options"), reply_markup=keyb)
    else:
        await m.edit(responses[0])


@bot.on_callback_query(filters.regex("^dicio"))
async def dicioc(c: Client, q:CallbackQuery):
    text, n = q.data.split("_")[1:]
    responses = dicioinformal.definicao(text)["results"]

    await q.edit(f'{responses[int(n)]["title"]}:\n{responses[int(n)]["tit"]}\n\n__{responses[int(n)]["desc"]}__')