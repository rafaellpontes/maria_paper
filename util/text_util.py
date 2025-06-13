import re
import datetime
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def save_audio_file(response, relative_path_audio, id_text, chunk_size, fonte):

    
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audio_{current_time}.mp3"
    output_path_audio = f"{relative_path_audio}/"+filename
    

    if fonte == "elevenlabs":
        with open(output_path_audio, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
    else:
        with open(output_path_audio, "wb") as f:
            # Read the response in chunks and write to the file
            for chunk in response.iter_bytes(chunk_size=chunk_size):
                f.write(chunk)

    return output_path_audio, filename

def get_audio_stream(text_to_speak, voice_id, headers, relative_path_audio, id_text, chunk_size):

    # Construct the URL for the Text-to-Speech API request
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"

    # Set up the data payload for the API request, including the text and voice settings
    data = {
        "text": text_to_speak,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.80,
            "style": 0.1,
            "use_speaker_boost": False
        }
    }

    # Make the POST request to the TTS API with headers and data, enabling streaming response
    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    output_path_audio, filename = save_audio_file(response, relative_path_audio, id_text, chunk_size, "elevenlabs")

    return output_path_audio, filename

def get_audio_stream_sudeste(answers, voice_id, client, relative_path_audio, id_text):

    chunk_size=8192
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice_id,
        input= answers,
    )

    #response.stream_to_file(output_path_audio)
    output_path_audio, filename = save_audio_file(response, relative_path_audio, id_text, chunk_size, "openai")

    return output_path_audio, filename

def corrigir_texto(texto):
    # Transformar "R$" em " reais"
    texto = re.sub(r'R\$\s*([\d,.]+)', r'\1 reais', texto)
    # Remover "_"
    texto = texto.replace("_", " ")
    # Remover "-"
    texto = texto.replace("-", " ")
    # Substituir "{" e "}" por ""
    texto = texto.replace("{", "").replace("}", "")
    # Substituir % por porcento
    texto = texto.replace("%", " porcento")
    # Substituir # por ""
    texto = texto.replace("#", "")
    # Subistituir qualquer quantidade de *
    texto = re.sub(r'\*+', '', texto)
    # Subistituir qualquer quantidade de " "
    texto = re.sub(r'\s+', ' ', texto)
    # Substituis ºC para transcrição
    texto = texto.replace("ºC", " graus Celsius")
    texto = texto.replace("°C", " graus Celsius")
    texto = texto.replace("degC", " graus Celsius")
    # Ajuste na unidade de horas
    texto = re.sub(r'(\d{1,2})h', r'\1 horas', texto)
    
    #texto = remover_acentos(texto)
    
    return texto

def get_transcription(enter_path, llm_client):
    transcription = []
    
    # Realize a transcrição do áudio
    with open(enter_path, "rb") as audio_file:
        trans = llm_client.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text")
    transcription.append(trans)

    return transcription

def text_similarity(text1, text2):
    # Criação do vetor TF-IDF
    vectorizer = TfidfVectorizer()

    # Ajusta e transforma os textos em uma matriz TF-IDF
    tfidf_matrix = vectorizer.fit_transform([text1, text2])

    # Calcula a similaridade do cosseno
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    return cosine_sim[0][0]

def generate_audio_and_check(answers, region, relative_path_audio, id_text, client):

    # Define constants for the script
    chunk_size = 1024  # Size of chunks to read/write at a time
    XI_API_KEY_ELEVENLABS = ""  # Your API key for authentication

    # Set up headers for the API request, including the API key for authentication
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY_ELEVENLABS
    }

    # Configuração de vozes
    config_voice = {
        'ceara': '', 
        'pernambuco': '', 
        'sudeste':'shimmer', 
        'bahia': ''
    }

    if region == 'ceara':
        voice_id = config_voice['ceara']
    elif region == 'bahia':
        voice_id = config_voice['bahia']
    elif region == 'pernambuco':
        voice_id = config_voice['pernambuco']
    else:
        voice_id = config_voice['sudeste']

    if region == 'sudeste':
        output_path_audio, filename = get_audio_stream_sudeste(answers, voice_id, client, relative_path_audio, id_text)
    else:
        output_path_audio, filename = get_audio_stream(answers, voice_id, headers, relative_path_audio, id_text, chunk_size)
    return filename