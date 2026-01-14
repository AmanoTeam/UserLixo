import ipaddress
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import bot, user
from utils import http  
from locales import use_lang

# --- Funções de Suporte ---

async def get_api_return(ip: str):
    """Consulta a API ipinfo.io para obter detalhes do IP."""
    try:
        r = await http.get(f"https://ipinfo.io/{ip}/json", timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        data.pop("readme", None) 
        return data
    except Exception:
        return None

def format_api_return(req: dict, t):
    """Formata o JSON da API em uma mensagem HTML elegante."""
    if req.get("bogon"):
        return t("ip_err_bogon_ip").format(ip=req["ip"])
    
    # Gera linhas: Chave em Negrito: Valor em Mono
    lines = [f"<b>{k.title()}</b>: <code>{v}</code>" for k, v in req.items()]
    return "\n".join(lines)

async def resolve_hostname(hostname: str) -> list:
    """Resolve um domínio para IPs usando Cloudflare DNS (DoH)."""
    ips = []
    for type_dns in ["A", "AAAA"]: # IPv4 e IPv6
        try:
            r = await http.get(
                f"https://cloudflare-dns.com/dns-query?name={hostname}&type={type_dns}",
                headers={"accept": "application/dns-json"},
                timeout=10
            )
            data = r.json()
            if "Answer" in data:
                # Tipo 1 é A, Tipo 28 é AAAA
                ips.extend([ans["data"] for ans in data["Answer"] if ans["type"] in [1, 28]])
        except Exception:
            continue
    return list(dict.fromkeys(ips)) # Remove duplicatas mantendo a ordem

# --- Handlers ---

@Client.on_message(filters.command("ip", prefixes=".") & filters.sudoers)
@use_lang()
async def ip_cmd(c: Client, m: Message, t):
    # 1. Verificação de Argumento
    if len(m.command) < 2:
        return await m.edit(t("ip_err_no_ip"))

    query = m.command[1]
    
    # 2. Limpeza de URL para extrair apenas o Host 
    host = query.split("://")[-1].split("/")[0].split(":")[0]

    msg = await m.edit(strings("ip_search"))

    # 3. Identificação (IP ou Domínio)
    try:
        ipaddress.ip_address(host)
        ips = [host]
    except ValueError:
        ips = await resolve_hostname(host)

    if not ips:
        return await msg.edit(t("ip_err_no_ips").format(domain=host))

    # 4. Resultado Único 
    if len(ips) == 1:
        data = await get_api_return(ips[0])
        if not data:
            return await msg.edit(strings("ip_err_search"))
        return await msg.edit(format_api_return(data, t))

    # 5. Múltiplos Resultados 
    keyboard = []
    for ip in ips[:10]: # Limite de 10 botões para não poluir o chat
        keyboard.append([InlineKeyboardButton(ip, callback_data=f"ip_info|{ip}")])
    
    # Deletamos a mensagem do userbot e enviamos a do bot assistente
    await m.delete()
    await bot.send_message(
        m.chat.id,
        t("ip_select_ip").format(domain=host),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@bot.on_callback_query(filters.regex(r"^ip_info\|"))
@use_lang()
async def ip_callback(c: Client, cb: CallbackQuery, t):
    ip = cb.data.split("|")[1]
    
    # Feedback visual de carregamento
    await cb.answer(strings("ip_search_loading"), show_alert=False)
    
    data = await get_api_return(ip)
    if data:
        await cb.edit_message_text(
            format_api_return(data, t),
            reply_markup=None # Remove os botões após a escolha
        )
    else:
        await cb.answer(strings("ytdl_missing_argument"), show_alert=True)
