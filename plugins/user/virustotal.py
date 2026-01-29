import asyncio
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Optional

from hydrogram import Client, filters
from hydrogram.errors import ListenerTimeout
from hydrogram.types import (
    CallbackQuery, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    Message
)

from config import bot
from db import VirusTotalKey
from locales import use_lang
from utils import http, pretty_size

# Lista completa de motores AV para exibição
AV_ENGINES = [
    "Bkav", "Lionic", "MicroWorld-eScan", "CMC", "CAT-QuickHeal", "ALYac",
    "Malwarebytes", "Zillya", "Sangfor", "Trustlook", "Alibaba", "K7GW",
    "K7AntiVirus", "BitDefenderTheta", "VirIT", "Cyren", "SymantecMobileInsight",
    "Symantec", "ESET-NOD32", "Baidu", "TrendMicro-HouseCall", "Avast",
    "ClamAV", "Kaspersky", "BitDefender", "NANO-Antivirus", "SUPERAntiSpyware",
    "Tencent", "Ad-Aware", "TACHYON", "Emsisoft", "Comodo", "F-Secure",
    "DrWeb", "VIPRE", "TrendMicro", "McAfee-GW-Edition", "FireEye", "Sophos",
    "GData", "Jiangmin", "Avira", "Antiy-AVL", "Kingsoft", "Microsoft",
    "Gridinsoft", "Arcabit", "ViRobot", "ZoneAlarm", "Avast-Mobile", "Cynet",
    "BitDefenderFalx", "AhnLab-V3", "McAfee", "MAX", "VBA32", "Zoner",
    "Rising", "Yandex", "Ikarus", "MaxSecure", "Fortinet", "Panda"
]

# Constantes da API VirusTotal
VT_API_BASE = "https://www.virustotal.com/api/v3"
VT_UPLOAD_URL = f"{VT_API_BASE}/files"
MAX_FILE_SIZE = 32 * 1024 * 1024  # 32MB (limite da API free)

async def get_vt_key(user_id: int) -> Optional[str]:
    """Obtém a chave API do VirusTotal para um usuário específico."""
    record = await VirusTotalKey.get_or_none(id=user_id)
    return record.api_key if record else None

async def set_vt_key(user_id: int, api_key: str) -> None:
    """Define a chave API do VirusTotal para um usuário."""
    # Remove espaços e caracteres especiais
    api_key = api_key.strip()
    
    record = await VirusTotalKey.get_or_none(id=user_id)
    if record:
        # Atualiza chave existente
        record.api_key = api_key
        await record.save()
    else:
        # Cria novo registro
        await VirusTotalKey.create(id=user_id, api_key=api_key)

async def remove_vt_key(user_id: int) -> bool:
    """Remove a chave API do VirusTotal de um usuário."""
    record = await VirusTotalKey.get_or_none(id=user_id)
    if record:
        await record.delete()
        return True
    return False

async def upload_to_virustotal(file_path: str, api_key: str) -> Optional[Dict]:
    """Faz upload de um arquivo para o VirusTotal."""
    headers = {
        "x-apikey": api_key,
        "accept": "application/json"
    }
    
    try:
        with open(file_path, "rb") as file:
            files = {"file": (Path(file_path).name, file)}
            response = await http.post(
                VT_UPLOAD_URL,
                headers=headers,
                files=files,
                timeout=60
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"VT Upload Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"VT Upload Exception: {e}")
        return None

async def get_analysis_results(analysis_id: str, api_key: str) -> Optional[Dict]:
    """Obtém os resultados de uma análise do VirusTotal."""
    headers = {
        "x-apikey": api_key,
        "accept": "application/json"
    }
    
    analysis_url = f"{VT_API_BASE}/analyses/{analysis_id}"
    
    # Tentativa por até 60 segundos (a análise pode demorar)
    for attempt in range(12):  # 12 tentativas com 5 segundos de intervalo
        response = await http.get(analysis_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            status = data["data"]["attributes"]["status"]
            
            if status == "completed":
                return data
            elif status == "queued":
                # Mostrar progresso se for a 3ª tentativa ou mais
                if attempt >= 10:
                    return {"data": {"attributes": {"status": "queued", "attempt": attempt}}}
                await asyncio.sleep(5)
                continue
            else:
                return None
        else:
            return None
    
    return None  # Timeout após 60 segundos

async def get_file_report(file_hash: str, api_key: str) -> Optional[Dict]:
    """Obtém relatório de um arquivo já analisado (pelo hash)."""
    headers = {
        "x-apikey": api_key,
        "accept": "application/json"
    }
    
    report_url = f"{VT_API_BASE}/files/{file_hash}"
    response = await http.get(report_url, headers=headers, timeout=30)
    
    if response.status_code == 200:
        return response.json()
    return None

def format_analysis_results(data: Dict, file_info: Dict, t) -> str:
    """Formata os resultados da análise em uma mensagem bonita."""
    attributes = data["data"]["attributes"]
    
    # Se ainda está em fila
    if attributes.get("status") == "queued":
        attempt = attributes.get("attempt", 0)
        return t("vt_still_queued")
    
    stats = attributes.get("stats", {})
    results = attributes.get("results", {})
    
    # Cabeçalho com detecções
    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)
    total = sum(stats.values())
    
    # Emoji baseado na gravidade
    if malicious > 10:
        header_emoji = "☠️"
    elif malicious > 0:
        header_emoji = "⚠️"
    else:
        header_emoji = "✅"
    
    message = f"{header_emoji} **Detecções:** {malicious} / {total}" # (corrigir tradução)
    if suspicious > 0:
        message += f" (suspeitas: {suspicious})" # (corrigir tradução)
    message += "\n\n"
    
    # Lista de motores AV
    for engine in AV_ENGINES:
        if engine in results:
            result = results[engine]
            category = result.get("category", "undetected")
            
            if category == "malicious":
                message += f"❌ {engine}\n"
            elif category == "suspicious":
                message += f"⚠️ {engine}\n"
            elif category == "undetected":
                message += f"✅ {engine}\n"
            else:
                message += f"➖ {engine}\n"
        else:
            message += f"➖ {engine}\n"
    
    # Informações do arquivo (corrigir tradução)
    message += f"\n🔖 **Nome do arquivo:** `{file_info.get('name', 'Unknown')}`\n"
    message += f"🔒 **Tipo de arquivo:** `{file_info.get('type', 'Unknown')}`\n"
    message += f"📁 **Tamanho do arquivo:** `{pretty_size(file_info.get('size', 0))}`\n\n"
    
    # Magic (informações técnicas)
    magic = file_info.get('magic', 'Unknown')
    if magic and magic != 'Unknown':
        message += f"🎉 **Magic**\n• `{magic}`\n\n"
    
    # Link para VirusTotal
    sha256 = attributes.get("sha256", "")
    if sha256:
        vt_link = f"https://www.virustotal.com/gui/file/{sha256}"
        message += f"⚜️ [VirusTotal]({vt_link})"
    else:
        message += f"⚜️ [VirusTotal](https://www.virustotal.com)"
    
    return message

@Client.on_message(filters.command(["virustotal", "vt"], prefixes=".") & filters.sudoers)
@use_lang()
async def virustotal_cmd(c: Client, m: Message, t):
    """Comando principal para analisar arquivos no VirusTotal."""
    # Verificar se o usuário tem chave API
    user_id = m.from_user.id
    api_key = await get_vt_key(user_id)
    
    if not api_key:
        await m.edit(
            t("vt_no_api_key"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text=t("vt_configure"),
                    callback_data="config_plugin_virustotal"
                )]
            ])
        )
        return
    
    # Verificar se há arquivo para analisar
    target_msg = m
    if m.reply_to_message:
        target_msg = m.reply_to_message
    
    # Lista de tipos de mídia suportados
    supported_media = (
        target_msg.document or target_msg.photo or 
        target_msg.video or target_msg.audio or 
        target_msg.voice or target_msg.video_note
    )
    
    if not supported_media:
        await m.edit(t("vt_no_file"))
        return
    
    # Baixar o arquivo
    msg = await m.edit(t("vt_downloading"))
    
    try:
        # Criar diretório temporário
        temp_dir = Path("temp_vt")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Baixar arquivo
        file_path = await target_msg.download(
            file_name=temp_dir / f"vt_scan_{user_id}_{m.id}"
        )
        
        if not file_path:
            await msg.edit(t("vt_download_error"))
            return
        
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            os.remove(file_path)
            await msg.edit(t("vt_file_too_big").format(
                max=pretty_size(MAX_FILE_SIZE),
                actual=pretty_size(file_size)
            ))
            return
        
        # Calcular hash do arquivo
        await msg.edit(t("vt_calculating_hash"))
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Verificar se já existe análise
        await msg.edit(t("vt_checking_cache"))
        report = await get_file_report(file_hash, api_key)
        
        if report:
            # Usar análise existente
            file_info = {
                "name": Path(file_path).name,
                "size": file_size,
                "type": get_file_type(target_msg),
                "magic": report["data"]["attributes"].get("magic", "Unknown")
            }
            
            formatted = format_analysis_results(report, file_info, t)
            await msg.edit(formatted, disable_web_page_preview=False)
        
        else:
            # Fazer nova análise
            await msg.edit(t("vt_uploading"))
            upload_result = await upload_to_virustotal(file_path, api_key)
            
            if not upload_result:
                os.remove(file_path)
                await msg.edit(t("vt_upload_error"))
                return
            
            analysis_id = upload_result["data"]["id"]
            
            await msg.edit(t("vt_analyzing"))
            analysis_result = await get_analysis_results(analysis_id, api_key)
            
            if not analysis_result:
                os.remove(file_path)
                await msg.edit(t("vt_analysis_error"))
                return
            
            # Verificar se ainda está em fila
            if analysis_result.get("data", {}).get("attributes", {}).get("status") == "queued":
                await msg.edit(format_analysis_results(analysis_result, {}, t))
                os.remove(file_path)
                return
            
            # Formatar e mostrar resultados
            file_info = {
                "name": Path(file_path).name,
                "size": file_size,
                "type": get_file_type(target_msg),
                "magic": analysis_result["data"]["attributes"].get("magic", "Unknown")
            }
            
            formatted = format_analysis_results(analysis_result, file_info, t)
            await msg.edit(formatted, disable_web_page_preview=False)
        
        # Limpar arquivo temporário
        if os.path.exists(file_path):
            os.remove(file_path)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in virustotal_cmd: {e}\n{error_details}")
        await msg.edit(t("vt_error").format(error=str(e)[:200]))
        
        # Limpeza em caso de erro
        if 'file_path' in locals() and file_path and os.path.exists(file_path):
            os.remove(file_path)

def get_file_type(message: Message) -> str:
    """Determina o tipo do arquivo baseado na mensagem."""
    if message.document:
        return message.document.mime_type or "Document"
    elif message.photo:
        return "Photo"
    elif message.video:
        return "Video"
    elif message.audio:
        return "Audio"
    elif message.voice:
        return "Voice"
    elif message.video_note:
        return "Video Note"
    else:
        return "Unknown"

@bot.on_callback_query(filters.regex(r"\bconfig_plugin_virustotal\b"))
@use_lang()
async def config_virustotal(c: Client, m: CallbackQuery, t):
    """Menu principal de configuração do VirusTotal."""
    user_id = m.from_user.id
    current_key = await get_vt_key(user_id)
    
    if current_key:
        key_status = t("vt_has_key").format(
            masked=current_key[:4] + "****" + current_key[-4:]
        )
    else:
        key_status = t("vt_no_key")
    
    await m.edit(
        f"{t('vt_settings_title')}\n\n{key_status}",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=t("vt_set_key"),
                    callback_data="config_plugin_virustotal_key"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("vt_remove_key"),
                    callback_data="config_plugin_virustotal_remove"
                )
            ],
            [InlineKeyboardButton(text=t("back"), callback_data="config_plugins")]
        ])
    )

@bot.on_callback_query(filters.regex(r"config_plugin_virustotal_key"))
@use_lang()
async def config_virustotal_key(c: Client, cq: CallbackQuery, t):
    """Configurar chave API do VirusTotal."""
    user_id = cq.from_user.id
    
    await cq.edit_message_text(
        t("vt_enter_key_instructions"),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text=t("cancel"), callback_data="config_plugin_virustotal")]
        ])
    )
    
    # Aguardar resposta do usuário
    try:
        key_msg = await cq.message.chat.listen(
            filters.text & filters.user(user_id),
            timeout=60
        )
    except ListenerTimeout:
        await cq.edit_message_text(
            t("vt_timeout"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=t("back"), callback_data="config_plugin_virustotal")]
            ])
        )
        return
    
    new_key = key_msg.text.strip()
    
    if new_key.lower() == "/cancel":
        await cq.edit_message_text(
            t("canceled"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=t("back"), callback_data="config_plugin_virustotal")]
            ])
        )
        return
    
    # Validar chave (fazendo uma requisição de teste)
    await cq.edit_message_text(t("vt_validating_key"))
    
    test_headers = {"x-apikey": new_key}
    test_resp = await http.get(f"{VT_API_BASE}/users/me", headers=test_headers, timeout=30)
    
    if test_resp.status_code != 200:
        await cq.edit_message_text(
            t("vt_invalid_key"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=t("try_again"), callback_data="config_plugin_virustotal_key")]
            ])
        )
        return
    
    # Salvar chave
    await set_vt_key(user_id, new_key)
    
    await cq.edit_message_text(
        t("vt_key_set"),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text=t("back"), callback_data="config_plugin_virustotal")]
        ])
    )

@bot.on_callback_query(filters.regex(r"config_plugin_virustotal_remove"))
@use_lang()
async def config_virustotal_remove(c: Client, cq: CallbackQuery, t):
    """Remover chave API do VirusTotal."""
    user_id = cq.from_user.id
    removed = await remove_vt_key(user_id)
    
    if removed:
        message = t("vt_key_removed")
    else:
        message = t("vt_no_key_to_remove")
    
    await cq.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text=t("back"), callback_data="config_plugin_virustotal")]
        ])
    )

# Adicionar à lista de plugins
from config import plugins
plugins.append("virustotal")
