import asyncio
import speedtest
import tempfile
from datetime import datetime
from pathlib import Path

from hydrogram import Client, filters
from hydrogram.types import Message

from utils import http
from locales import use_lang


def convert_from_bytes(size):
    """Converte bytes para unidade legível."""
    power = 2**10
    n = 0
    units = {0: "", 1: "Kbps", 2: "Mbps", 3: "Gbps", 4: "Tbps"}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {units[n]}"


async def run_speedtest_async():
    """Executa o speedtest de forma assíncrona para não bloquear o bot."""
    def sync_speedtest():
        s = speedtest.Speedtest()
        
        # Encontrar melhor servidor
        s.get_best_server()
        
        # Testar download
        s.download()
        
        # Testar upload
        s.upload()
        
        return s.results
    
    return await asyncio.to_thread(sync_speedtest)


@Client.on_message(filters.command("speedtest", prefixes=".") & filters.sudoers)
@use_lang()
async def speedtest_command(c: Client, m: Message, t):
    """
    Teste de velocidade do servidor onde o bot está hospedado.
    Uso: 
      .speedtest       - Texto (padrão)
      .speedtest -t    - Apenas texto
      .speedtest -i    - Imagem 
      .speedtest -f    - Arquivo (documento)
    """
    # Determinar modo de saída padrão
    mode = "text"
    
    # Verificar argumentos
    if len(m.command) > 1:
        arg = m.command[1].lower()
        
        if arg in ["-t", "--text", "text", "txt"]:
            mode = "text"
        elif arg in ["-f", "--file", "file", "doc", "document"]:
            mode = "file"
        elif arg in ["-i", "--image", "image", "img", "photo"]:
            mode = "image"
        else:
            await m.edit(t("speedtest_invalid_arg"))
            return
    
    # Mensagem inicial
    msg = await m.edit(t("speedtest_start"))
    
    try:
        # Executar teste com timeout de 180 segundos (3 minutos)
        start_time = datetime.now()
        
        # Primeira fase: encontrando servidor
        await msg.edit(t("speedtest_testing"))
        
        # Executar o teste completo
        results = await asyncio.wait_for(
            run_speedtest_async(),
            timeout=180  # 3 minutos de timeout
        )
        
        end_time = datetime.now()
        test_duration = (end_time - start_time).total_seconds()
        
        # Extrair dados
        download = results.download
        upload = results.upload
        ping = results.ping
        server = results.server
        client = results.client
        
        # Formatar resultados
        download_str = convert_from_bytes(download)
        upload_str = convert_from_bytes(upload)
        download_mbps = round(download / 8e6, 2)  # Convertendo para MB/s
        upload_mbps = round(upload / 8e6, 2)
        
        server_info = f"{server['name']} - {server['country']}"
        if server.get('sponsor'):
            server_info += f" ({server['sponsor']})"
        
        isp = client['isp']
        isp_rating = client.get('isprating', 'N/A')
        
        # Texto do resultado
        result_text = t("speedtest_result").format(
            duration=round(test_duration, 2),
            download_speed=download_str,
            download_mbps=download_mbps,
            upload_speed=upload_str,
            upload_mbps=upload_mbps,
            ping=round(ping, 2),
            server=server_info,
            isp=isp,
            isp_rating=isp_rating
        )
        
        # Modo texto: apenas enviar o texto
        if mode == "text":
            await msg.edit(result_text)
            return
        
        # Modos imagem/arquivo: baixar e enviar imagem
        try:
            # Obter URL da imagem do speedtest
            image_url = results.share()
            
            # Baixar imagem
            await msg.edit(t("speedtest_downloading_image"))
            response = await http.get(image_url, timeout=30)
            
            if response.status_code != 200:
                raise Exception("Falha ao baixar imagem do speedtest")
            
            # Salvar temporariamente
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp.write(response.content)
                temp_path = tmp.name
            
            # Enviar como imagem ou arquivo
            if mode == "image":
                await msg.delete()  # Deletar mensagem de progresso
                await c.send_photo(
                    chat_id=m.chat.id,
                    photo=temp_path,
                    caption=result_text,
                    reply_to_message_id=m.id
                )
            else:  # mode == "file"
                await msg.delete()  # Deletar mensagem de progresso
                await c.send_document(
                    chat_id=m.chat.id,
                    document=temp_path,
                    caption=result_text,
                    reply_to_message_id=m.id
                )
            
            # Limpar arquivo temporário
            try:
                Path(temp_path).unlink()
            except:
                pass
            
        except Exception as img_error:
            # Fallback para texto se falhar a imagem
            await msg.edit(f"{result_text}\n\n⚠️ {t('speedtest_image_fallback')}: {str(img_error)}")
    
    except asyncio.TimeoutError:
        await msg.edit(t("speedtest_timeout"))
    
    except speedtest.ConfigRetrievalError:
        await msg.edit(t("speedtest_no_internet"))
    
    except speedtest.NoMatchedServers:
        await msg.edit(t("speedtest_no_servers"))
    
    except Exception as e:
        await msg.edit(t("speedtest_error").format(error=str(e)[:200]))
