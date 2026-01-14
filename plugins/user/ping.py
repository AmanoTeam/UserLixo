import asyncio
import socket
import time
import statistics
import re
from datetime import datetime

from hydrogram import Client, filters
from hydrogram.types import Message

from locales import use_lang


async def python_ping(host, count=5, timeout=3):
    """
    Ping usando apenas Python (socket)
    """
    port = 80  # Porta HTTP para teste de conectividade
    results = []
    successful = 0
    
    # Tenta resolver o host primeiro
    try:
        # Resolve para IPv4
        info = await asyncio.get_event_loop().getaddrinfo(
            host, port, family=socket.AF_INET, type=socket.SOCK_STREAM
        )
        ip = info[0][4][0]
    except socket.gaierror:
        return {
            'success': False,
            'host': host,
            'error': f'Host não encontrado: {host}'
        }
    except Exception as e:
        return {
            'success': False,
            'host': host,
            'error': f'Erro ao resolver host: {str(e)}'
        }
    
    for i in range(count):
        try:
            # Cria socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            start_time = time.time()
            
            # Tenta conexão
            await asyncio.wait_for(
                asyncio.get_event_loop().sock_connect(sock, (ip, port)),
                timeout=timeout
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            results.append(latency_ms)
            successful += 1
            
            sock.close()
            
            # Pequena pausa entre pings
            if i < count - 1:
                await asyncio.sleep(0.5)
                
        except (socket.timeout, asyncio.TimeoutError):
            # Timeout conta como falha
            pass
        except ConnectionRefusedError:
            # Conexão recusada mas host respondeu (TCP SYN-ACK)
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            results.append(latency_ms)
            successful += 1
            sock.close()
        except Exception as e:
            if 'sock' in locals():
                sock.close()
    
    if successful == 0:
        return {
            'success': False,
            'host': host,
            'ip': ip,
            'error': 'Host não respondeu'
        }
    
    # Calcula estatísticas
    if results:
        loss_percentage = ((count - successful) / count) * 100
        
        return {
            'success': True,
            'host': host,
            'ip': ip,
            'stats': {
                'sent': count,
                'received': successful,
                'loss': loss_percentage,
                'min': min(results),
                'avg': statistics.mean(results) if len(results) > 1 else results[0],
                'max': max(results),
                'results': results
            }
        }
    else:
        return {
            'success': False,
            'host': host,
            'ip': ip,
            'error': 'Nenhuma resposta recebida'
        }


@Client.on_message(filters.command("ping", prefixes=".") & filters.sudoers)
@use_lang()
async def ping_command(c: Client, m: Message, t):
    """
    Comando .ping - Testa latência de hosts ou do bot
    Uso: .ping [host]
    Exemplos:
      .ping          - Mostra latência do bot
      .ping google.com  - Pinga google.com
      .ping 8.8.8.8    - Pinga DNS do Google
    """
    # Se não houver argumentos, pinga o bot
    if len(m.command) == 1:
        t1 = datetime.now()
        msg = await m.edit("Pong!")
        t2 = datetime.now()
        latency = (t2 - t1).microseconds / 1000
        await msg.edit(f"Latência do bot: `{latency:.2f}ms`")
        return
    
    host = m.command[1]
    
    # Validação do host
    if not re.match(r'^[a-zA-Z0-9.-]+$', host):
        await m.edit(f"❌ Host inválido: `{host}`")
        return
    
    msg = await m.edit(f"🔄 Pingando `{host}`...")
    
    try:
        result = await python_ping(host, count=5, timeout=3)
        
        if result['success']:
            stats = result['stats']
            loss = stats['loss']
            ip = result.get('ip', host)
            
            # Formata a resposta
            response = (
                f"**📡 Ping: {host}**\n"
                f"IP: `{ip}`\n"
                f"Pacotes: {stats['received']}/{stats['sent']} "
                f"(perda: {loss:.1f}%)\n\n"
                f"**Latência:**\n"
                f"• Mínima: `{stats['min']:.1f}ms`\n"
                f"• Média: `{stats['avg']:.1f}ms`\n"
                f"• Máxima: `{stats['max']:.1f}ms`"
            )
            
            # Análise qualitativa
            if loss > 70:
                status = "❌ Péssima (alta perda)"
            elif loss > 30:
                status = "⚠️ Ruim (perda moderada)"
            elif stats['avg'] > 300:
                status = "⚠️ Regular (latência alta)"
            elif stats['avg'] > 100:
                status = "✅ Boa"
            else:
                status = "✅ Excelente"
            
            response += f"\n\n**Status:** {status}"
            
        else:
            error_msg = result.get('error', 'Erro desconhecido')
            ip = result.get('ip', 'N/A')
            
            response = (
                f"**❌ Falha ao pingar**\n"
                f"Host: `{host}`\n"
                f"IP: `{ip}`\n"
                f"Erro: {error_msg}"
            )
        
        await msg.edit(response)
        
    except Exception as e:
        await msg.edit(f"**💥 Erro inesperado**\n\n```\n{str(e)[:150]}\n```")
