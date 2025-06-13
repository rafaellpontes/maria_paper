from agents.maria import Maria

#businesses
from business.llm_business import init_llm, retrieve_assistant, create_thread_message, audio_to_text
from business.message_business import fill_message, create_conversation, create_conversation_message, move_received_message
from business.gateway_business import send_message

from database import get_db
from models import MessageReceived, OwnerTypeEnum, Phone
import json
import time

#getting env variables
with open('config.json') as f:
    env_variables = json.load(f)

bot_number = env_variables['bot_number']


#init db
db = get_db()

#init llm
llm_client = init_llm(api_key=env_variables['openai_key'])
assistant = retrieve_assistant(llm_client)
maria = Maria(assistant=assistant, client = llm_client)

while True:
    
    print('Searching messages ....')
    message_received = db.query(MessageReceived).filter_by(bot_number=bot_number).order_by(MessageReceived.created.asc()).first()
    if message_received == None:
        time.sleep(2)
        continue
    
    #Buscando ou criando usuário e telefone / salvando mensagens no banco e enviando mensagem para thread do assistant
    message_received = fill_message(message_received, llm_client, db)
    
    #if message_received.phone.identifier != '5583999472236' and message_received.phone.identifier != '5585997587802'  and message_received.phone.identifier != '5585996237064'   and message_received.phone.identifier != '5585996260909':
    #    continue

    if message_received.phone.prod == False:
        continue

    #Move received message to receiver.messages_processed from receiver.messages
    move_received_message(received_message_id = message_received.id, db = db)
    
    if message_received.body == '#maria test 123#':
        db.query(Phone).filter_by(id=message_received.phone.id).update(values={'prod': False})
        db.commit()
        continue

    if message_received.body == '#maria prod 123#':
        db.query(Phone).filter_by(id=message_received.phone.id).update(values={'prod': True})
        db.commit()
        continue
    
    if message_received.phone.user.test_number == None or message_received.phone.user.test_number != 3:
        print(f'Usuário não autorizado ({str(message_received.phone.identifier)})')
        continue
    
    conversation = create_conversation(phone = message_received.phone, db = db)
    conversation_message, content = create_conversation_message(conversation = conversation, phone = message_received.phone, 
    text = message_received.body, owner_type = OwnerTypeEnum.USER, 
        type=message_received.type, llm_client = llm_client, db = db, 
            audio_filename=None, accent=message_received.phone.user.accent, fl_audio=message_received.phone.user.fl_audio, activeType=None)
    
    if conversation_message == None:
        continue
    
    thread_message_id = create_thread_message(llm_client = llm_client, thread_id = message_received.phone.thread_id, content = content)
    
    #chamar o run do llm_business
    response = maria.run(thread_id = message_received.phone.thread_id, user = message_received.phone.user, assistant = assistant, db = db)

    type = message_received.type
    if type == 'image':
        type = 'text'
    if type == 'pdf':
        type = 'text'
    
    #enviando mensagem via enterness
    if type == 'text' and message_received.phone.prod == False:
        response = '*[Teste]:* ' + response

    audio_filename = send_message(message = response, senderToken = message_received.phone.identifier, type = type, llm_client = llm_client, 
        phone_instance_id = message_received.phone.phone_instance_id, fl_audio = message_received.phone.user.fl_audio,
        accent=message_received.phone.user.accent, email=message_received.phone.user.email, filename=None)

    type = 'text'
    if audio_filename != None:
        type = 'audio'

    #Criando resposta do bot no banco de dados
    create_conversation_message(conversation = conversation, phone = message_received.phone, 
        text = response, owner_type = OwnerTypeEnum.AGENT, type=type, llm_client = llm_client, db = db,
        audio_filename=audio_filename, accent=message_received.phone.user.accent, 
        fl_audio=message_received.phone.user.fl_audio, activeType=None)

    #Chamar o Enterness para devolver o response
    time.sleep(1)
    
    