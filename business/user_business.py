from models import User, Phone
from database import get_db
from datetime import datetime

def create_user_with_phone(country_code, state_code, number, db):
    user = User(first_name = 'Usuário',
                    last_name = 'Desconhecido', created = datetime.now(), fl_audio = False, accent = False)
    db.add(user)

    identifier = country_code + state_code + number
    phone = Phone(state_code = state_code, country_code = country_code, number = number, audio_enabled = False,
                    identifier = identifier, user = user, created = datetime.now(), phone_instance_id=3)
    db.add(phone)
    db.commit()

    return user, phone