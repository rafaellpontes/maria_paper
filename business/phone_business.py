from models import Phone
from database import get_db

def get_phone_by_identifier(identifier, db):
    country_code = identifier[0:2]
    state_code = identifier[2:4]
    number = identifier[4:14]
    print(country_code)
    print(state_code)
    print(number)
    
    phone = db.query(Phone).filter_by(number=number, state_code=state_code, country_code=country_code).one_or_none()
    return phone, country_code, state_code, number


