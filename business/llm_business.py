from openai import OpenAI
from models import Phone
from util.downloads import download_audio, download_image
from util.text_util import corrigir_texto, generate_audio_and_check
import json
import requests
import base64
from PyPDF2 import PdfReader

def init_llm(api_key):
    llm_client = OpenAI(api_key=api_key)
    return llm_client

def retrieve_assistant(llm_client):
    assistant = llm_client.beta.assistants.retrieve("")
    return assistant

def create_single_thread (llm_client):
    thread =  llm_client.beta.threads.create()
    return thread

def create_thread (llm_client, phone, db):
    if phone.thread_id == None or phone.thread_id.strip() == '':
        thread =  llm_client.beta.threads.create()
        db.query(Phone).filter_by(id=phone.id).update(values={'thread_id': thread.id})
        db.commit()
    return phone

def create_thread_message_assistant (llm_client, thread_id, content):
    thread_message = llm_client.beta.threads.messages.create(thread_id, role="assistant", content=content)
    return thread_message.id

def create_thread_message (llm_client, thread_id, content):
    if content != None or content != '':
        thread_message = llm_client.beta.threads.messages.create(thread_id, role="user", content=content)
        return thread_message.id
    return None

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def image_to_text(url, llm_client):

    with open('config.json') as f:
        env_variables = json.load(f)
    api_key = env_variables['openai_key']

    file = download_image(url)
    base64_image = encode_image(file)

    prompt = f'''
        Seu objetivo é analisar uma imagem e requisitar a um assistante virtual chamado MarIA que tire conclusões sobre a imagem.

        % Para imagem de refeição ou comida
        Caso a imagem seja de uma refeição ou comida você deve extrair as seguintes informações:
        - peso aproximado
        - calorias de cada macronutrientes

        % Formato da Requisição à MarIA
        Toda requisição à MarIA para imagens sobre refeições ou comidas deve ter o seguinte formato
        "Você está recebendo uma imagem de [X] e deve você deve fazer uma análise do impacto de [X] no meu bem-estar. Os macronutrientes contidos em [X] são [Y], o peso aproximado de cada macronutriente são [PESO] e as calorias de cada macronutrientes são [CALORIAS]. Você sempre deve manter na sua análise final o peso e calorias de cada macronutriente."
        [X] = uma breve descrição da imagem.
        [Y] = a lista de macronutrientes contidos na refeição separados por vírgula.
        [PESO] = o peso de cada macronutriente contido na refeição.
        [CALORIAS] = as calorias de cada macronutriente contido na refeição.
        Matenha sempre ao final do texto gerado a seguinte frase: "Você sempre deve manter na sua análise final o peso e calorias de cada macronutriente."
        
        % Para imagem que não é de refeições ou comida
        Caso a imagem não seja uma refeição ou lanche faça uma descrição detalhada do que é a imagem [descrição detalhada].
        Caso ao analisar a imagem e encontrar algum indício de problemas de saúde e ou ferimentos quero que fale sobre o que encotrou na [descrição detalhada].

        % Formato da Requisição à MarIA
        Toda requisição à MarIA para imagens que não são sobre refeições ou comidas deve ter o seguinte formato
        "Você está recebendo de [X] e você deve fazer uma análise sobre a imagem que tem a seguinte descrição [descrição detalhada]"
        [X] = uma breve descrição da imagem.
    '''

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            },
        ]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    resposta_texto = response.json()['choices'][0]['message']['content']
    return resposta_texto

def text_embedding(llm_client, text):

    response = llm_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )

    return response.data[0].embedding


def image_description_extractor(url, llm_client):

    with open('config.json') as f:
        env_variables = json.load(f)
    api_key = env_variables['openai_key']

    file = download_image(url)
    base64_image = encode_image(file)

    prompt = f'''
        Você está recebendo uma imagem.
        Faça a descrição mais detalhada possível desta imagem.
    '''

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            },
        ]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    resposta_texto = response.json()['choices'][0]['message']['content']
    return resposta_texto

def pdf_to_text(url):

    
    file_path = download_image(url)
    with open(file_path, "rb") as arquivo_pdf:
        leitor_pdf = PdfReader(arquivo_pdf)
        texto_extraido = ""

        for pagina in range(len(leitor_pdf.pages)):
            texto_extraido += leitor_pdf.pages[pagina].extract_text()
        return texto_extraido

def audio_to_text(url, llm_client):
    file = download_audio(url)
    transcription = None
    # Realize a transcrição do áudio
    with open(file, "rb") as audio_file:
        transcription = llm_client.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text")
    
    return transcription

def text_to_audio(text, llm_client, accent, email):
    #getting env variables
    with open('config.json') as f:
        env_variables = json.load(f)
    temp_path = env_variables['temp_path']

    text = corrigir_texto(text)

    id_text = 'vitoria'
    region = 'sudeste'

    if accent == True and email == 'salvador@hapvida.com.br':
        region = 'bahia'
    if accent == True and email == 'recife@hapvida.com.br':
        region = 'pernambuco'
    if accent == True and email == 'fortaleza@hapvida.com.br':
        region = 'ceara'


    filename = generate_audio_and_check(text, region, temp_path, id_text, llm_client)
    return filename

