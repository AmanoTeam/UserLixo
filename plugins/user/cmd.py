import asyncio
import io
import os
import docker
from hydrogram import Client, filters
from hydrogram.types import Message

from locales import use_lang

# --- VARIÁVEIS DE AMBIENTE ---
DOCKER_SOCKET_PATH = "/var/run/docker.sock"


def run_host_command(command: str) -> str:
    """
    Executa um comando Shell arbitrário no HOST (com acesso a binários e serviços) 
    usando um contêiner sidecar temporário com mapeamento do Root do Host.
    """
    
    try:
        client = docker.from_env()
    except Exception as e:
        return f"🚨 Erro ao conectar ao daemon Docker do Host: {e}"

    try:
        shell_command = f"chroot /host sh -c '{command}'"
        
        container = client.containers.run(
            image="alpine:latest", 
            command=["sh", "-c", shell_command], 
            
            volumes={
                "/": {'bind': '/host', 'mode': 'ro'}, 
                DOCKER_SOCKET_PATH: {'bind': DOCKER_SOCKET_PATH, 'mode': 'rw'}
            }, 
            privileged=True,
            network_mode='host',
            remove=True,
            detach=False
        )
        return container.decode('utf-8').strip()

    except docker.errors.APIError as e:
        return f"❌ Erro na API Docker (Host): {e}"
    except Exception as e:
        return f"❌ Erro inesperado na execução do Host: {e}"


@Client.on_message(filters.command("cmd", prefixes=".") & filters.sudoers)
@use_lang()
async def cmd(_, m: Message, t):
    
    # 1. Parsing do Comando
    text = m.text[5:].strip()
    if not text:
        await m.edit(t("cmd_usage")) 
        return
    
    # 2. DETECÇÃO DO AMBIENTE
    is_docker_env = os.path.exists("/.dockerenv")
    can_access_docker_daemon = os.path.exists(DOCKER_SOCKET_PATH)

    # 3. Lógica de Execução
    if is_docker_env and can_access_docker_daemon:
        res = await asyncio.to_thread(run_host_command, text)
        is_host_execution = True
        
    else:
        proc = await asyncio.create_subprocess_shell(
            text, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )
        ex = await proc.communicate()
        res = ex[0].decode().rstrip()
        is_host_execution = False

    # 4. Formatação e Resposta (Ajustada para simplificar a saída)
    
    # Se houver erro ou saída, mostramos a saída.
    # Se a saída for vazia (ex: comando 'cd ..' bem-sucedido), usamos a mensagem de sucesso.
    if not res:
        final_response = t("cmd_no_output") 
    else:
        final_response = res
        
    if len(final_response) > 4096:
        with io.BytesIO(str.encode(final_response)) as out_file:
            out_file.name = "cmd.txt"
            await m.reply_document(out_file)
    else:
        # Edita a mensagem para mostrar apenas a resposta final ou a mensagem de sucesso.
        await m.edit(final_response)
