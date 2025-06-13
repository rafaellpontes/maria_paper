import json
from sqlalchemy import text
from database import get_engine, get_db
from business.message_business import fill_message, create_conversation, create_conversation_message, create_thread
from business.llm_business import init_llm, retrieve_assistant, create_thread_message, create_single_thread ,create_thread_message_assistant
from business.phone_business import get_phone_by_identifier
from business.gateway_business import send_message
from models import OwnerTypeEnum, MessageActiveTypeEnum, Measurement, MeasurementTypeEnum
from agents.maria import Maria
import csv
from sqlalchemy import func


def send_image(senderToken, phone_instance_id, message):
    filename = "campanha_27"
    type = 'image' 
    llm_client = None,
    fl_audio = False, 
    accent = False, 
    email = None

    send_message(message, senderToken, type, llm_client, phone_instance_id, fl_audio, accent, email, filename)


#getting env variables
with open('config.json') as f:
    env_variables = json.load(f)

llm_client = init_llm(api_key = env_variables['openai_key'])
assistant = retrieve_assistant(llm_client)
gpt_model = env_variables['gpt_model']

engine = get_engine()
db = get_db()
with engine.connect() as connection:
    query = f'''
        SELECT 
            u.first_name,
            u.last_name,
            p.identifier,
            u.id,
            u.fl_audio,
            u.accent,
            email
        FROM public.user u
        INNER JOIN public.phone p on p.user_id = u.id
        WHERE 
            u.test_number = 3
            AND is_happvida = true
        order by p.created asc
    '''
    result = connection.execute(text(query))


maria = Maria(assistant=assistant, client = llm_client)

i = 0
for values in result:
    
    i = i + 1
    #continue

    try:
    
        firstname = values[0]
        lastname = values[1]
        identifier = values[2]
        user_id = values[3]
        fl_audio = False
        accent = values[5]
        email = values[6]

       
        nome_completo = firstname + ' ' + lastname
        
        phone, country_code, state_code, number = get_phone_by_identifier(identifier, db)
        phone = create_thread(llm_client, phone, db)
        conversation = create_conversation(phone = phone, db = db)

        thread = create_single_thread(llm_client)


        primeira_consulta, recente_consulta, primeira_data, data_recent = get_medical_data(user_id, db)


        prompt = f"""
            {{tema}}: "Cuidados essenciais com a pele no diabetes (Como prevenir ressecamento, coceiras e feridas.)",
            "persona": "Como Maria, a assistente cuidadora de saúde do projeto Viver Bem da Hapvida NotreDame Intermédica, cumprimente calorosamente o usuário {nome_completo}.",
            "tarefa": "Explique o {{tema}} e forneça orientações relevantes. Com base nos dados das consultas desde {primeira_data}, da {data_recent} até do dia atual, considerando inclusive o que já foi conversado anteriormente, adapte suas sugestões para promover um estilo de vida mais ativo e saudável, considerando as mudanças nas medições e valores dos exames compartilhado pelo usuário.",
            "tom": "Mantenha um tom empático e educativo ao oferecer informações essenciais sobre o {{tema}}.",
            "formato": "Responda em até 500 caracteres, organizando as informações de forma clara e acessível, abordando uma pergunta de cada vez. Finalize com uma pergunta relacionada ao tema discutido para manter o engajamento e relevância ao longo do tempo.",
        """

        response = llm_client.chat.completions.create(
            model = gpt_model,
            messages=[
                {
                    "role": "system", "content": prompt
                },
            ]
        )
        response = response.choices[0].message.content
        
        
        create_thread_message_assistant (llm_client, phone.thread_id, response)

        if fl_audio == True:
            send_image(senderToken=phone.identifier, phone_instance_id=phone.phone_instance_id, message="")
            audio_filename = send_message(message = response, senderToken = phone.identifier, type = 'audio', llm_client = llm_client, 
                phone_instance_id = phone.phone_instance_id, fl_audio = fl_audio,
                accent=accent, email=email, filename=None)

            create_conversation_message(conversation = conversation, phone = phone, 
                text = response, owner_type = OwnerTypeEnum.AGENT, type='audio', llm_client = llm_client, db = db,
                audio_filename=None, accent=phone.user.accent, fl_audio=phone.user.fl_audio, activeType=MessageActiveTypeEnum.FORMULARIO)
        else:
            send_image(senderToken=phone.identifier, phone_instance_id=phone.phone_instance_id, message=response)
            #send_message(message = response, senderToken = phone.identifier, type = 'text', llm_client = llm_client, 
            #    phone_instance_id = phone.phone_instance_id, fl_audio = False,
            #    accent=accent, email=email, filename=None)
            create_conversation_message(conversation = conversation, phone = phone, 
                text = response, owner_type = OwnerTypeEnum.AGENT, type='text', llm_client = llm_client, db = db,
                audio_filename=None, accent=phone.user.accent, fl_audio=False, activeType=MessageActiveTypeEnum.FORMULARIO)
    except:
        print('erro')

print(i)   

    

    

    