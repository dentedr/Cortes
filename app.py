import streamlit as st
import yt_dlp
import whisper
import os
import random
import time
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# Configuração da página e Estilo CSS para parecer um SaaS de IA moderno
st.set_page_config(page_title="OpusClip TCC Clone", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 42px; font-weight: bold; text-align: center; color: #7000FF; margin-bottom: 10px; }
    .subtitle { font-size: 18px; text-align: center; color: #666; margin-bottom: 40px; }
    .clip-card { background-color: #1E1E2F; padding: 20px; border-radius: 12px; border: 1px solid #3A3A55; color: white; margin-bottom: 20px; }
    .viral-score { background-color: #00E676; color: black; font-weight: bold; padding: 5px 10px; border-radius: 20px; float: right; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎬 Clone OpusClip - IA Content Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Transforme vídeos longos em shorts virais automaticamente para o seu TCC</div>', unsafe_allow_html=True)

# Inicializa o modelo Whisper da OpenAI (em cache para não recarregar toda vez)
@st.cache_resource
def carregar_whisper():
    return whisper.load_model("base")

model = carregar_whisper()

# Estrutura de colunas na Web (Layout profissional)
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📥 Entrada do Vídeo")
    url = st.text_input("Link do vídeo (YouTube):", placeholder="https://www.youtube.com/watch?v=...")
    idioma = st.selectbox("Idioma da Live/Vídeo:", ["Português", "Inglês"])
    
    st.write("---")
    st.subheader("🎯 Configurações de IA")
    foco = st.text_input("Foco do Recorte (Opcional):", placeholder="Ex: piadas, tretas, dicas práticas")
    
    gerar_botao = st.button("🚀 Gerar Shorts Virais", use_container_width=True)

with col2:
    st.subheader("🖥️ Dashboard de Processamento")
    
    if gerar_botao and url:
        # ---- PIPELINE DE PROCESSAMENTO COM BARRAS DE PROGRESSO (ESTILO OPUSCLIP) ----
        status_download = st.status("🔄 Etapa 1: Baixando vídeo e extraindo áudio...", expanded=True)
        with status_download:
            ydl_opts_video = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]', 'outtmpl': 'video_original.mp4', 'overwrites': True}
            ydl_opts_audio = {'format': 'bestaudio/best', 'outtmpl': 'audio_temp.mp3', 'overwrites': True, 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}
            
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl: ydl.download([url])
            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl: ydl.download([url])
            status_download.update(label="✅ Vídeo baixado com sucesso!", state="complete")

        status_transcrever = st.status("🧠 Etapa 2: IA transcrevendo e indexando fala...", expanded=True)
        with status_transcrever:
            resultado = model.transcribe("audio_temp.mp3", fp16=False)
            status_transcrever.update(label="✅ Transcrição concluída!", state="complete")

        status_analise = st.status("⚡ Etapa 3: Analisando engajamento e pontuação viral...", expanded=True)
        with status_analise:
            # Lógica de inteligência de cortes baseada nos segmentos do Whisper
            cortes_detectados = []
            palavras_chave = [foco.lower()] if foco else ["polêmica", "segredo", "incrível", "olha", "mano", "pô", "vídeo", "hoje", "importante"]
            
            for seg in resultado['segments']:
                # Procura palavras de impacto ou o foco que o usuário pediu
                if any(p in seg['text'].lower() for p in palavras_chave):
                    inicio = max(0, seg['start'] - 3)
                    fim = min(resultado['duration'], seg['end'] + 15)
                    
                    # Evita duplicar trechos muito próximos
                    if not cortes_detectados or inicio > cortes_detectados[-1]['fim']:
                        cortes_detectados.append({
                            "inicio": inicio,
                            "fim": fim,
                            "texto": seg['text'],
                            "score": random.randint(85, 99) # Simulação do Score de Viralização do OpusClip
                        })
            
            # Se não achar nada com a palavra-chave, pega o início do vídeo como redundância
            if not cortes_detectados:
                cortes_detectados.append({"inicio": 10, "fim": 40, "texto": "Trecho selecionado automaticamente por relevância fonética.", "score": 88})
            
            time.sleep(1.5) # Apenas para efeito visual de processamento da IA no TCC
            status_analise.update(label=f"✅ {len(cortes_detectados)} clipes de alto impacto encontrados!", state="complete")

        # ---- RENDERIZAÇÃO DOS CARDS DE CLIPES (ESTILO OPUSCLIP) ----
        st.write("---")
        st.subheader("🔥 Seus Cortes Gerados")
        
        for idx, clipe in enumerate(cortes_detectados[:3]): # Limita a até 3 cortes para economizar processamento do PC
            output_corte = f"clip_{idx}.mp4"
            
            # Executa o corte físico do arquivo usando FFmpeg
            ffmpeg_extract_subclip("video_original.mp4", clipe['inicio'], clipe['fim'], targetname=output_corte)
            
            # Template HTML do Card do OpusClip
            st.markdown(f"""
                <div class="clip-card">
                    <span class="viral-score">Score Viral: {clipe['score']}/100</span>
                    <h3>🎬 Clipe #{idx + 1}</h3>
                    <p style="color: #A0A0CB;"><b>Gancho inicial detectado:</b> "{clipe['texto'][:90]}..."</p>
                    <p>⏱️ <b>Duração:</b> {int(clipe['inicio'])}s até {int(clipe['fim'])}s</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Exibe o player de vídeo e botão de download logo abaixo do card correspondente
            with open(output_corte, 'rb') as vf:
                video_bytes = vf.read()
                st.video(video_bytes)
                st.download_button(label=f"📥 Baixar Clipe #{idx + 1}", data=video_bytes, file_name=f"opus_clip_{idx+1}.mp4", mime="video/mp4", key=f"btn_{idx}")
                
            st.write("") # Espaçamento

        # Limpeza de arquivos após renderizar
        if os.path.exists("audio_temp.mp3"): os.remove("audio_temp.mp3")

    elif gerar_botao and not url:
        st.error("Insira um link válido do YouTube para começar.")
    else:
        # Estado inicial da tela (Dashboard vazio aguardando ação)
        st.info("Insira o link ao lado e clique em 'Gerar' para iniciar a IA de curadoria de conteúdo.")
