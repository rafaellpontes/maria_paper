from business.llm_business import text_to_audio
import requests
import json
import boto3
from botocore.exceptions import ClientError
import json

def send_message(message, senderToken, type, llm_client, phone_instance_id, fl_audio, accent, email,filename):
    type = 'text'
    fl_audio = False
    audio_filename = None
    if (phone_instance_id == 1):
        phone_instance_id = 1
    
    if (phone_instance_id == 3):
        phone_instance_id = 4
    
    if (phone_instance_id == 2):
        phone_instance_id = 3
        
    if type == 'audio' or fl_audio == True:
        print('Sending audio')
        filename = text_to_audio(text=message, llm_client=llm_client, accent=accent, email=email)
        audio_filename = filename
        send_message_audio(message, senderToken, filename, phone_instance_id)
    elif type == 'pdf':
        print('Sending pdf')
        send_message_pdf(message, senderToken, filename, phone_instance_id)
    elif type == 'image':
        a
        print('Sending image')
        send_message_image(message, senderToken, filename, phone_instance_id)
    else:
        print('Sending text')
        send_message_text(message, senderToken, phone_instance_id)
        
    return audio_filename

def send_message_text(message, senderToken, phone_instance_id):
    #getting env variables
    with open('config.json') as f:
        env_variables = json.load(f)

    api_key = env_variables['enterness']['api_key']

    url = f'https://unifor.easychannel.online/instance/{phone_instance_id}/send-message'
    
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "senderToken": senderToken+"@c.us",
        "content": {
            "type": "text",
            "message": message
        }
    }
    response = requests.post(url, json = params, headers = headers)
    print(response.text)
    return response.text

def send_btn_message_text(message, senderToken, phone_instance_id):
    #getting env variables
    with open('config.json') as f:
        env_variables = json.load(f)

    api_key = env_variables['enterness']['api_key']

    url = f'https://unifor.easychannel.online/instance/{phone_instance_id}/send-message'
    
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "senderToken": senderToken+"@c.us",
        "content": {
            "type": "button",
            "body": message,
            "buttons": ["Sim", "Não"]
        }
    }
    response = requests.post(url, json = params, headers = headers)
    print(response.text)
    return response.text

def send_message_audio(message, senderToken, filename, phone_instance_id):
    
    #getting env variables
    with open('config.json') as f:
        env_variables = json.load(f)

    #Enviando audio para S3
    file_path = env_variables['temp_path']
    aws_access_key_id = env_variables['aws']['aws_access_key_id']
    aws_secret_access_key = env_variables['aws']['aws_secret_access_key']
    bucket_name = env_variables['aws']['bucket_name']

    api_key = env_variables['enterness']['api_key']

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    with open(file_path+filename, "rb") as f:
        s3.upload_fileobj(f, bucket_name, filename, ExtraArgs={'ContentType': "audio/mpeg"})
    audio_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket_name,
            'Key': filename
        },
        ExpiresIn = 120
    )

    #Enviando mensagem via enterness
    url = f'https://unifor.easychannel.online/instance/{phone_instance_id}/send-message'
    
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "senderToken": senderToken+"@c.us",
        "content": {
            "type": "audio",
            "file": {
                "url": audio_url,
                "filename": filename,
            },
            "caption": ""
        }
    }
    response = requests.post(url, json = params, headers = headers)
    
    return response.text


def send_message_pdf(message, senderToken, filename, phone_instance_id):
    
    #getting env variables
    with open('config.json') as f:
        env_variables = json.load(f)

    #Enviando audio para S3
    file_path = env_variables['temp_path']
    aws_access_key_id = env_variables['aws']['aws_access_key_id']
    aws_secret_access_key = env_variables['aws']['aws_secret_access_key']
    bucket_name = env_variables['aws']['bucket_name']

    api_key = env_variables['enterness']['api_key']
    
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    with open(file_path+filename+".pdf", "rb") as f:
        s3.upload_fileobj(f, bucket_name, filename+".pdf", ExtraArgs={'ContentType': "application/pdf"})

    pdf_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket_name,
            'Key': filename+".pdf"
        },
        ExpiresIn = 120
    )
    #Enviando mensagem via enterness
    url = f'https://unifor.easychannel.online/instance/{phone_instance_id}/send-message'
    
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    params = {
        "senderToken": senderToken+"@c.us",
        "content": {
            "type": "document",
            "file": {
                "url": pdf_url,
                "filename": filename,
            },
            "caption": ""
        }
    }
    response = requests.post(url, json = params, headers = headers)
    return response.text

def send_message_image(message, senderToken, filename, phone_instance_id):
    
    #getting env variables
    with open('config.json') as f:
        env_variables = json.load(f)

    #Enviando audio para S3
    file_path = env_variables['temp_path']
    aws_access_key_id = env_variables['aws']['aws_access_key_id']
    aws_secret_access_key = env_variables['aws']['aws_secret_access_key']
    bucket_name = env_variables['aws']['bucket_name']

    api_key = env_variables['enterness']['api_key']

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    with open(file_path+filename+".jpeg", "rb") as f:
        s3.upload_fileobj(f, bucket_name, filename+".jpeg", ExtraArgs={'ContentType': "image/jpeg"})

    pdf_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket_name,
            'Key': filename+".jpeg"
        },
        ExpiresIn = 120
    )
    #Enviando mensagem via enterness
    url = f'https://unifor.easychannel.online/instance/{phone_instance_id}/send-message'
    
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    params = {
        "senderToken": senderToken+"@c.us",
        "content": {
            "type": "image",
            "file": {
                "url": pdf_url,
                "filename": filename,
            },
            "caption": message
        }
    }
    response = requests.post(url, json = params, headers = headers)
    return response.text

