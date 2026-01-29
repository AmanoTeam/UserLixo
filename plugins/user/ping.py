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
    Ping usando apenas Python (socket) na porta 80
    """
    port = 80 
    results = []
    successful = 0
    
    try:
        info = await asyncio.get_event_loop().getaddrinfo(
            host, port, family=socket.AF_INET, type=socket.SOCK_STREAM
        )
        ip = info[0][4][0]
    except Exception as e:
        return {
            'success': False,
            'host': host,
            'error': str(e)
        }
    
    for i in range(count):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            start_time = time.time()
            
            await asyncio.wait_for(
                asyncio.get_event_loop().sock_connect(sock, (ip, port)),
                timeout=timeout
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            results.append(latency_ms)
            successful += 1
            sock.close()
            
            if i < count - 1:
                await asyncio.sleep(0.5)
                
        except (socket.timeout, asyncio.TimeoutError, ConnectionRefusedError):
            if 'start_time' in locals() and isinstance(e, ConnectionRefusedError):
                end_time = time.time()
                results.append((end_time - start_time) * 1000)
                successful += 1
            if 'sock' in locals(): sock.close()
        except Exception:
            if 'sock' in locals(): sock.close()
    
    if successful == 0:
        return {'success': False, 'host': host, 'ip': ip, 'error': 'No response'}
    
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
            'max': max(results)
        }
    }

@Client.on_message(filters.command("ping", prefixes=".") & filters.sudoers)
@use_lang()
async def ping_command(c: Client, m: Message, t):
    # Ping do Bot (Simples)
    if len(m.command) == 1:
        t1 = datetime.now()
        msg = await m.edit("Pong!")
        t2 = datetime.now()
        latency = (t2 - t1).microseconds / 1000
        await msg.edit(t("ping_bot_latency").format(latency=f"{latency:.2f}"))
        return
    
    host = m.command[1]
    
    # Validação do host
    if not re.match(r'^[a-zA-Z0-9.-]+$', host):
        await m.edit(t("ping_invalid_host").format(host=host))
        return
    
    msg = await m.edit(t("ping_start").format(host=host))
    
    try:
        result = await python_ping(host)
        
        if result['success']:
            stats = result['stats']
            
            # Cabeçalho da resposta
            response = t("ping_response").format(
                host=host,
                ip=result['ip'],
                received=stats['received'],
                sent=stats['sent'],
                loss=f"{stats['loss']:.1f}"
            )
            
            # Linhas de latência
            response += t("ping_min").format(min=f"{stats['min']:.1f}") + "\n"
            response += t("ping_avg").format(avg=f"{stats['avg']:.1f}") + "\n"
            response += t("ping_max").format(max=f"{stats['max']:.1f}")
            
            # Lógica qualitativa com tradução
            if stats['loss'] > 70:
                status_text = t("ping_status_terrible")
            elif stats['loss'] > 30:
                status_text = t("ping_status_bad")
            elif stats['avg'] > 300:
                status_text = t("ping_status_regular")
            elif stats['avg'] > 100:
                status_text = t("ping_status_good")
            else:
                status_text = t("ping_status_excellent")
                
            response += t("ping_status").format(status=status_text)
            
        else:
            response = t("ping_fail").format(
                host=host,
                ip=result.get('ip', 'N/A'),
                error=result.get('error', 'N/A')
            )
        
        await msg.edit(response)
        
    except Exception as e:
        await msg.edit(t("ping_unexpected_error").format(error=str(e)[:150]))
