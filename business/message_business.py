from datetime import datetime
from sqlalchemy import text

from business.phone_business import get_phone_by_identifier
from business.user_business import create_user_with_phone
from business.llm_business import create_thread, audio_to_text, image_to_text, pdf_to_text, image_description_extractor, text_embedding

from models import Conversation, ConversationMessage, OwnerTypeEnum, MessageTypeEnum, MessageReceived, Image

def fill_message(message_received, llm_client, db):
    
    identifier = message_received.wa_id
    phone, country_code, state_code, number = get_phone_by_identifier(identifier, db)
    
    if phone == None:
        user, phone = create_user_with_phone(country_code, state_code, number, db)
        phone.user = user
    
    phone = create_thread(llm_client, phone, db)
    message_received.phone = phone
    return message_received

def create_conversation (phone, db):
    conversation = db.query(Conversation).filter_by(user_id = phone.user.id).one_or_none()
    if conversation == None:
        conversation = Conversation(agent_id = 1, phone = phone, user = phone.user, created = datetime.now())
        db.add(conversation)
        db.commit()
    return conversation

def create_conversation_message (conversation, phone, text, owner_type, type, llm_client, db, audio_filename, accent, fl_audio, activeType):
    type = text
    url = None
    if type == 'audio':
        message_type = MessageTypeEnum.AUDIO
    elif type == 'image':
        message_type = MessageTypeEnum.IMAGE
    elif type == 'pdf':
        message_type = MessageTypeEnum.PDF
    else:
        message_type = MessageTypeEnum.TEXT
    
    image_description = None
    image_description_embedding = None

    if "unifor.easychannel.online" in text and type == 'audio':
        url = text
        text = audio_to_text(url, llm_client)
    if "unifor.easychannel.online" in text and type == 'image':
        url = text
        text = image_to_text(url, llm_client)
        image_description = image_description_extractor(url, llm_client)
        
        if image_description != None:
            image_description_embedding = text_embedding(llm_client, image_description)
    

    if "unifor.easychannel.online" in text and type == 'pdf':
        url = text
        text = pdf_to_text(url)
        

    if text == None:
        return None
    text = text.strip()
    owner_id = conversation.user_id
    if owner_type == OwnerTypeEnum.AGENT:
        owner_id = 1
    
    conversation_message = ConversationMessage(content = text, owner_type = owner_type, 
        type = message_type, owner_id = conversation.user_id, audio_authorized = phone.audio_enabled, 
        conversation_id = conversation.id, created = datetime.now(), url = url, 
        risk_analysed = False, 
        danger_analysed = False, audio_filename=audio_filename, accent=accent, fl_audio=fl_audio, activeType=activeType)
    db.add(conversation_message)
    db.commit()

    if image_description != None:
        image = Image(user_id = conversation.user_id, created = datetime.now(), url = url,
            description=image_description, embedding=str(image_description_embedding), 
            conversation_message_id=conversation_message.id)
        db.add(image)
        db.commit()

    
    
    
    return conversation_message, text

def move_received_message (received_message_id, db):
    sql = f'''
        INSERT INTO receiver.messages_processed
        (
            sms_message_id, 
            num_media, 
            profile_name, 
            sms_sid, 
            wa_id, 
            sms_status, 
            body, 
            "to", 
            num_segments, 
            referral_num_media, 
            message_sid,
            account_sid, 
            "from", 
            api_version, 
            created, 
            bot_number, 
            type
        )
	    SELECT
		    sms_message_id, 
            num_media, 
            profile_name, 
            sms_sid, 
            wa_id, 
            sms_status, 
            body, 
            "to", 
            num_segments, 
            referral_num_media, 
            message_sid, 
            account_sid, 
            "from", 
            api_version, 
            created, 
            bot_number, 
            type 
	    FROM receiver.messages WHERE id = {received_message_id}
    '''
    sql = text(sql)
    result = db.execute(sql)
    db.query(MessageReceived).filter_by(id=received_message_id).delete()
    db.commit()
