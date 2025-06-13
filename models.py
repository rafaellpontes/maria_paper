from database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, ForeignKey, Enum, Boolean, Double
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
import enum


class MessageReceived(Base):
    __tablename__ = "messages"
    __table_args__ = {"schema":"receiver"}

    id = Column(Integer,primary_key=True,nullable=False)
    bot_number = Column(Integer,nullable=False)
    wa_id = Column(String,nullable=False)
    body = Column(Text,nullable=False)
    type = Column(String,nullable=False)
    created = Column(TIMESTAMP(timezone=False),nullable=False)

class GenderTypeEnum(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True,nullable=False)
    age = Column(Integer,nullable=True)
    gender = Column(String,nullable=True)
    first_name = Column(String,nullable=False)
    last_name = Column(String,nullable=False)
    created = Column(TIMESTAMP(timezone=False),nullable=False)

    fl_audio = Column(Boolean(),nullable=False)
    accent = Column(Boolean(),nullable=False)
    email = Column(String,nullable=True)
    test_number = Column(Integer,nullable=True)

    phones = relationship('Phone', backref = 'user')
    conversation = relationship('Conversation', backref = 'user')
    alarms = relationship('Alarm', backref = 'user')
    measurements = relationship('Measurement', backref = 'user')
    food_datas = relationship('FoodData', backref = 'user')

class Phone(Base):
    __tablename__ = "phone"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True, nullable=False)
    state_code = Column(String, nullable=False)
    number = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    identifier = Column(String, nullable=False)
    thread_id = Column(String, nullable=False)
    created = Column(TIMESTAMP(timezone=False), nullable=False)
    audio_enabled = Column(Boolean(),nullable=False)
    phone_instance_id = Column(Integer,nullable=True)
    prod = Column(Boolean(),nullable=False)

    user_id = Column(Integer(), ForeignKey('public.user.id'))

    conversation = relationship('Conversation', backref = 'phone')

class Agent(Base):
    __tablename__ = "agent"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True,nullable=False)
    description = Column(String,nullable=False)
    created = Column(TIMESTAMP(timezone=False),nullable=False)

    conversation = relationship('Conversation', backref = 'agent')

class Conversation(Base):
    __tablename__ = "conversation"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True,nullable=False)

    agent_id = Column(Integer(), ForeignKey('public.agent.id'))
    phone_id = Column(Integer(), ForeignKey('public.phone.id'))
    user_id = Column(Integer(), ForeignKey('public.user.id'))

    created = Column(TIMESTAMP(timezone=False),nullable=False)

    conversationMessages = relationship('ConversationMessage', backref = 'agent')

class OwnerTypeEnum(enum.Enum):
    USER = "USER"
    AGENT = "AGENT"

class MessageTypeEnum(enum.Enum):
    TEXT = "TEXT"
    AUDIO = "AUDIO"
    IMAGE = "IMAGE"
    PDF = "PDF"

class MessageActiveTypeEnum(enum.Enum):
    PRIMEIRO_CONTATO = "PRIMEIRO_CONTATO"
    LEMBRETE = "LEMBRETE"
    PROATIVIDADE = "PROATIVIDADE"
    RESPONSABILIDADE_MEDICA = "RESPONSABILIDADE_MEDICA"
    PROATIVIDADE_CAMPANHA_1 = "PROATIVIDADE_CAMPANHA_1"
    PROATIVIDADE_FORCE_AUDIO = "PROATIVIDADE_FORCE_AUDIO"
    AVISO_NAO_HUMANO = "AVISO_NAO_HUMANO"
    PROATIVIDADE_FARMACIA_PROMOCAO = "PROATIVIDADE_FARMACIA_PROMOCAO"
    PROATIVIDADE_AGENDAMENTO_CONSULTA = "PROATIVIDADE_AGENDAMENTO_CONSULTA"
    MEDICAL_SCHEDULING_REMINDER = "MEDICAL_SCHEDULING_REMINDER"
    PROATIVIDADE_AUTONOMA = "PROATIVIDADE_AUTONOMA"
    PROATIVIDADE_ADMIN = "PROATIVIDADE_ADMIN"
    CAMPANHA_USUARIOS_SEMPRE_INATIVOS = "CAMPANHA_USUARIOS_SEMPRE_INATIVOS"
    FORMULARIO="FORMULARIO"

class ConversationMessage(Base):
    __tablename__ = "conversation_message"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True,nullable=False)
    content = Column(Text,nullable=False)
    owner_type = Column(Enum(OwnerTypeEnum),nullable=False)
    type = Column(Enum(MessageTypeEnum),nullable=False)
    activeType = Column("active_type",Enum(MessageActiveTypeEnum),nullable=True)
    owner_id = Column(Integer(),nullable=False)
    audio_authorized = Column(Boolean(),nullable=False)
    created = Column(TIMESTAMP(timezone=False),nullable=False)
    url = Column(Text,nullable=True)
    risk_analysed = Column(Boolean(),nullable=False)    
    danger_analysed = Column(Boolean(),nullable=False)    

    audio_filename = Column(String,nullable=True)
    accent = Column(Boolean(),nullable=False)
    fl_audio = Column(Boolean(),nullable=False)
    

    conversation_id = Column(Integer(), ForeignKey('public.conversation.id'))
    notifications = relationship('Notification', backref = 'conversation_message')

class NotificationTypeEnum(enum.Enum):
    SITUACAO_URGENCIA = "SITUACAO_URGENCIA"
    SITUACAO_PERIGOSA_AGENTE = "SITUACAO_PERIGOSA_AGENTE"

class Notification(Base):
    __tablename__ = "notification"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True,nullable=False)
    type = Column(Enum(NotificationTypeEnum),nullable=False)
    created = Column(TIMESTAMP(timezone=False),nullable=False)
    solved = Column(Boolean(),nullable=False)
    conversation_message_id = Column(Integer(), ForeignKey('public.conversation_message.id'))

class Alarm(Base):
    __tablename__ = "alarm_data"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True,nullable=False)
    owner_id = Column(Integer(), ForeignKey('public.user.id'))
    description = Column(String,nullable=False)
    date = Column(String,nullable=False)
    time = Column(String,nullable=False)
    date_time = Column(TIMESTAMP(timezone=False),nullable=False)
    message_sent = Column(Boolean(),nullable=False)
    created = Column(TIMESTAMP(timezone=False),nullable=False)

class MeasurementTypeEnum(enum.Enum):
    ALTURA = "ALTURA"
    PESO = "PESO"
    IMC = "IMC"
    HEMOGLOBINA_GLICADA = "HEMOGLOBINA_GLICADA"
    PRESSAO_ARTERIAL = "PRESSAO_ARTERIAL"
    HDL = "HDL"
    ESCORE_FRAMINGHAM = "ESCORE_FRAMINGHAM"
    CIRCUNFERENCIA_ABDOMINAL = "CIRCUNFERENCIA_ABDOMINAL"
    LDL = "LDL"

class Measurement(Base):
    __tablename__ = "measurements"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True,nullable=False)
    user_id = Column(Integer(), ForeignKey('public.user.id'))
    value = Column(Double,nullable=True)
    text_value = Column(String,nullable=True)
    type = Column(Enum(MeasurementTypeEnum),nullable=False)
    from_hapvida = Column(Boolean(),nullable=False)

    date = Column(TIMESTAMP(timezone=False),nullable=False)
    created = Column(TIMESTAMP(timezone=False),nullable=False)

    def get_value (self):
        if self.value == None:
            return self.text_value
        return self.value

class Address(Base):
    __tablename__ = "address"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True,nullable=False)
    user_id = Column(Integer(), ForeignKey('public.user.id'))
    value = Column(String,nullable=False)
    latitude = Column(Double,nullable=False)
    longitude = Column(Double,nullable=False)
    created = Column(TIMESTAMP(timezone=False),nullable=False)

class FoodDataTypeEnum(enum.Enum):
    PREFERENCIA_POSITIVA = "PREFERENCIA_POSITIVA"
    PREFERENCIA_NEGATIVA = "PREFERENCIA_NEGATIVA"
    ALERGIA = "ALERGIA"
    INTOLERANCIA = "INTOLERANCIA"
    HABITOS = "HABITOS"
    FREQUENCIA = "FREQUENCIA"
    RESTRICOES = "RESTRICOES"
    PREFERENCIAS_CULTURAIS_RELIGIOSAS = "PREFERENCIAS_CULTURAIS_RELIGIOSAS"
    HORARIOS = "HORARIOS"

class FoodData(Base):
    __tablename__ = "food_data"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True,nullable=False)
    user_id = Column(Integer(), ForeignKey('public.user.id'))

    value = Column(String,nullable=False)
    type = Column(Enum(FoodDataTypeEnum),nullable=False)

    created = Column(TIMESTAMP(timezone=False),nullable=False)

class Image(Base):
    __tablename__ = "image"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True,nullable=False)
    user_id = Column(Integer(), ForeignKey('public.user.id'))
    description = Column(Text,nullable=False)
    embedding = Column(Text,nullable=False)
    url = Column(Text,nullable=True)

    conversation_message_id = Column(Integer(), ForeignKey('public.conversation_message.id'))
    user_id = Column(Integer(), ForeignKey('public.user.id'))

    created = Column(TIMESTAMP(timezone=False),nullable=False)

class MedicalScheduling(Base):
    __tablename__ = "medical_scheduling"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True,nullable=False)
    user_id = Column(Integer(), ForeignKey('public.user.id'))

    type = Column(String,nullable=True)
    doctor_name = Column(String,nullable=True)
    exam = Column(String,nullable=True)
    date = Column(String,nullable=True)
    time = Column(String,nullable=True)
    date_unavailable = Column(String,nullable=True)
    time_unavailable = Column(String,nullable=True)
    reason = Column(String,nullable=True)
    same_day = Column(String,nullable=True)
    processed = Column(Boolean(),nullable=True)
    sent = Column(Boolean(),nullable=True)
    

    created = Column(TIMESTAMP(timezone=False),nullable=False)

    schedule_datetime = Column(TIMESTAMP(timezone=False),nullable=True)
    comments = Column(String,nullable=True)
    not_medical_scheduling = Column(Boolean(),nullable=True)

class ProactiveScheduling(Base):
    __tablename__ = "proactive_scheduling"
    __table_args__ = {"schema":"public"}

    id = Column(Integer,primary_key=True,nullable=False)
    user_id = Column(Integer(), ForeignKey('public.user.id'))

    description = Column(String,nullable=False)
    theme = Column(String,nullable=False)
    relevance = Column(String,nullable=False)
    date = Column(TIMESTAMP(timezone=False),nullable=False)
    message_excerpt = Column(Text,nullable=False)
    message = Column(Text,nullable=False)
    theme = Column(String,nullable=False)

    created = Column(TIMESTAMP(timezone=False),nullable=False)

    analysed = Column(Boolean(),nullable=True)
    sent = Column(Boolean(),nullable=True)
    response = Column(Text,nullable=True)

