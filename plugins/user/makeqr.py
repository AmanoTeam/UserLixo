import io
import re
from typing import Optional

import qrcode
from hydrogram import Client, filters
from hydrogram.types import Message
from PIL import Image

from locales import use_lang

# Regex para encontrar links
LINK_REGEX = re.compile(
    r'https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'
)


@Client.on_message(filters.command("mkqr", prefixes=".") & filters.sudoers)
@use_lang()
async def mkqr_command(c: Client, m: Message, t):
    """
    Gera QR Code a partir de texto ou mensagem respondida.
    
    Uso:
      .mkqr <texto>          - Gera QR do texto
      .mkqr (respondendo)    - Gera QR do texto da mensagem
      .mkqr -l (respondendo) - Gera QR apenas do primeiro link
    """
    # Processar argumentos
    args = m.command
    link_only = "-l" in args
    
    # Remover -l dos argumentos para processamento
    if link_only:
        args = [arg for arg in args if arg != "-l"]
    
    # Obter texto para codificar
    text = await get_text_to_encode(c, m, args, link_only, t)
    if not text:
        return
    
    # Verificar tamanho
    if len(text) > 1000:
        await m.edit(t("mkqr_too_long").format(
            max=1000, actual=len(text)
        ))
        return
    
    # Gerar QR Code
    msg = await m.edit(t("mkqr_generating"))
    
    try:
        # Criar e enviar QR
        qr_bytes = await generate_qr_code(text)
        caption = await generate_caption(text, link_only, t)
        
        await m.reply_photo(
            photo=qr_bytes,
            caption=caption 
        )
        
        await msg.edit(t("mkqr_success"))
        
    except Exception as e:
        await msg.edit(t("mkqr_error").format(error=str(e)))


async def get_text_to_encode(
    c: Client, 
    m: Message, 
    args: list, 
    link_only: bool, 
    t
) -> Optional[str]:
    """Obtém o texto para codificar no QR."""
    # Caso 1: Texto direto nos argumentos
    if len(args) > 1:
        return " ".join(args[1:])
    
    # Caso 2: Respondendo a mensagem
    if m.reply_to_message:
        replied = m.reply_to_message
        
        # Obter texto da mensagem
        text = replied.text or replied.caption
        if not text:
            await m.edit(t("mkqr_no_text"))
            return None
        
        # Modo -l: extrair apenas primeiro link
        if link_only:
            links = LINK_REGEX.findall(text)
            if not links:
                await m.edit(t("mkqr_no_links"))
                return None
            return links[0]
        
        # Modo normal: usar todo o texto
        return text
    
    # Caso 3: Sem entrada válida
    await m.edit(t("mkqr_no_input"))
    return None


async def generate_qr_code(text: str) -> io.BytesIO:
    """Gera QR Code e retorna bytes da imagem."""
    # Criar QR Code otimizado
    qr = qrcode.QRCode(
        version=None,  # Auto ajuste
        error_correction=qrcode.constants.ERROR_CORRECT_Q,  # 25% de correção
        box_size=8,
        border=2,
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    # Gerar imagem
    img = qr.make_image(
        fill_color="black",
        back_color="white",
        image_factory=None
    )
    
    # Converter para bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG', optimize=True)
    img_bytes.seek(0)
    
    return img_bytes


async def generate_caption(text: str, link_only: bool, t) -> str:
    """Gera legenda apropriada para o QR."""
    if link_only:
        # Para links, mostrar truncado se muito longo
        display = text[:60] + ("..." if len(text) > 60 else "")
        return t("mkqr_caption_link").format(link=display)
    
    # Para texto, mostrar preview
    if len(text) <= 80:
        preview = text
    else:
        preview = text[:77] + "..."
    
    return t("mkqr_caption_text").format(preview=preview)
