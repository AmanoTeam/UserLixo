import ipaddress
import json
from hydrogram import Client, filters
from hydrogram.types import Message
from db import Message
from utils import http  
from locales import use_lang


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
    
    lines = [f"<b>{k.title()}</b>: <code>{v}</code>" for k, v in req.items()]
    return "\n".join(lines)


async def resolve_hostname(hostname: str) -> list:
    """Resolve um domínio para IPs usando Cloudflare DNS (DoH)."""
    ips = []
    for type_dns in ["A", "AAAA"]:
        try:
            r = await http.get(
                f"https://cloudflare-dns.com/dns-query?name={hostname}&type={type_dns}",
                headers={"accept": "application/dns-json"},
                timeout=10
            )
            data = r.json()
            if "Answer" in data:
                ips.extend([ans["data"] for ans in data["Answer"] if ans["type"] in [1, 28]])
        except Exception:
            continue
    return list(dict.fromkeys(ips))


@Client.on_message(filters.command("ip", prefixes=".") & filters.sudoers)
@use_lang()
async def ip_cmd(c: Client, m: Message, t):
    if len(m.command) < 2:
        return await m.edit(t("ip_err_no_ip"))

    query = m.command[1]
    host = query.split("://")[-1].split("/")[0].split(":")[0]

    msg = await m.edit(t("ip_search"))

    try:
        ipaddress.ip_address(host)
        ips = [host]
    except ValueError:
        ips = await resolve_hostname(host)

    if not ips:
        return await msg.edit(t("ip_err_no_ips").format(domain=host))

    # Resultado único
    if len(ips) == 1:
        data = await get_api_return(ips[0])
        if not data:
            return await msg.edit(t("ip_err_search"))
        return await msg.edit(format_api_return(data, t))

    # Múltiplos resultados 
    if len(ips) > 10:
        ips = ips[:10]
    
    # TRUQUE: Armazenar dados estruturados como JSON no campo 'keyboard'
    # Isso evita que o inline.py tente usar strings como botões
    
    # Criar estrutura de dados
    ip_data = {
        "host": host,
        "ips": ips,
        "type": "ip_selector"  # Identificador para saber como processar
    }
    
    # Armazenar como JSON string
    mes = await Message.create(
        text=f"IP Selector: {host}",
        keyboard=json.dumps(ip_data)  
    )
    
    # Criar botões normais para enviar
    keyb = []
    for i, ip in enumerate(ips):
        keyb.append([(ip, f"ip_info|{i}|{mes.key}")])
    
    # Organizar em 2 colunas
    formatted_keyb = []
    for i in range(0, len(keyb), 2):
        if i + 1 < len(keyb):
            formatted_keyb.append([keyb[i][0], keyb[i+1][0]])
        else:
            formatted_keyb.append([keyb[i][0]])
    
    await m.reply(t("ip_select_ip").format(domain=host), reply_markup=formatted_keyb)
    await m.delete()


@Client.on_callback_query(filters.regex(r"^ip_info\|") & filters.sudoers)
@use_lang()
async def ip_callback(c: Client, cb, t):
    parts = cb.data.split("|")
    if len(parts) != 3:
        return await cb.answer(t("ip_err_format"), show_alert=True)
    
    index = int(parts[1])
    message_key = parts[2]
    
    mes = await Message.get_or_none(key=message_key)
    if not mes:
        return await cb.answer(t("old_msg"), show_alert=True)
    
    try:
        # Tentar parsear como JSON primeiro
        import json
        ip_data = json.loads(mes.keyboard)
        if isinstance(ip_data, dict) and ip_data.get("type") == "ip_selector":
            ip = ip_data["ips"][index]
        else:
            # Fallback: assumir que é lista de strings
            ip = mes.keyboard[index]
    except (json.JSONDecodeError, IndexError, TypeError, KeyError):
        # Se falhar, tentar como lista direta
        try:
            ip = mes.keyboard[index]
        except:
            return await cb.answer(t("ip_err_nf"), show_alert=True)
    
    await cb.answer(t("ip_search_loading"), show_alert=False)
    
    data = await get_api_return(ip)
    if not data:
        return await cb.answer(t("ip_err_search"), show_alert=True)
    
    formatted = format_api_return(data, t)
    
    keyboard = [[("◀️ Voltar", f"ip_back|{message_key}")]]
    
    await cb.edit_message_text(
        formatted,
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex(r"^ip_back\|") & filters.sudoers)
@use_lang()
async def ip_back_callback(c: Client, cb, t):
    """Voltar para a lista de IPs"""
    message_key = cb.data.split("|")[1]
    
    mes = await Message.get_or_none(key=message_key)
    if not mes:
        return await cb.answer(t("ip_err_data_nf"), show_alert=True)
    
    try:
        # Tentar parsear JSON
        import json
        ip_data = json.loads(mes.keyboard)
        if isinstance(ip_data, dict) and ip_data.get("type") == "ip_selector":
            host = ip_data["host"]
            ips = ip_data["ips"]
        else:
            host = mes.text.replace("IP Selector: ", "")
            ips = mes.keyboard
    except:
        host = mes.text.replace("IP Selector: ", "")
        ips = mes.keyboard
    
    # Recriar botões
    keyb = []
    for i, ip in enumerate(ips):
        keyb.append([(ip, f"ip_info|{i}|{message_key}")])
    
    # Organizar em 2 colunas
    formatted_keyb = []
    for i in range(0, len(keyb), 2):
        if i + 1 < len(keyb):
            formatted_keyb.append([keyb[i][0], keyb[i+1][0]])
        else:
            formatted_keyb.append([keyb[i][0]])
    
    await cb.edit_message_text(
        t("ip_select_ip").format(domain=host),
        reply_markup=formatted_keyb
    )
