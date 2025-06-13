import json
import requests

def download_audio(url):
    
    #getting env variables
    with open('config.json') as f:
        env_variables = json.load(f)
    temp_path = env_variables['temp_path']
    filename = url.split('/')[len(url.split('/'))-1]

    file = temp_path + filename
    
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return file

def download_image(url):
    #getting env variables
    with open('config.json') as f:
        env_variables = json.load(f)
    temp_path = env_variables['temp_path']
    filename = url.split('/')[len(url.split('/'))-1]

    file = temp_path + filename
    
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return file