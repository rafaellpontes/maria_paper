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

def get_medical_data (user_id, db):
    first_measurement = db.query(Measurement).filter_by(user_id=user_id).order_by(Measurement.date.asc()).first()

    
    subquery_max = db.query(func.max(Measurement.date)).filter_by(user_id=user_id).subquery()
    subquery_min = db.query(func.min(Measurement.date)).filter_by(user_id=user_id).subquery()

    first_measurements = db.query(Measurement).filter_by(user_id=user_id).filter(Measurement.date.in_(subquery_min)).all()
    current_measurements = db.query(Measurement).filter_by(user_id=user_id).filter(Measurement.date.in_(subquery_max)).all()



    last_data_str = ""
    first_data_str = ""

    texto_adicional = ""
    current_date = ""
    fist_date = ""
    
    if len(current_measurements) > 0:
        current_date = current_measurements[0].date.strftime('%d/%m/%Y')
        height = next((x for x in current_measurements if x.type == MeasurementTypeEnum.ALTURA), None)
        weight = next((x for x in current_measurements if x.type == MeasurementTypeEnum.PESO), None)
        imc = next((x for x in current_measurements if x.type == MeasurementTypeEnum.IMC), None)
        glycated_hemoglobin = next((x for x in current_measurements if x.type == MeasurementTypeEnum.HEMOGLOBINA_GLICADA), None)
        blood_pressure = next((x for x in current_measurements if x.type == MeasurementTypeEnum.PRESSAO_ARTERIAL), None)
        hdl = next((x for x in current_measurements if x.type == MeasurementTypeEnum.HDL), None)
        framingham_score = next((x for x in current_measurements if x.type == MeasurementTypeEnum.ESCORE_FRAMINGHAM), None)
        ldl = next((x for x in current_measurements if x.type == MeasurementTypeEnum.LDL), None)
        abdominal_circumference = next((x for x in current_measurements if x.type == MeasurementTypeEnum.CIRCUNFERENCIA_ABDOMINAL), None)


        height_txt = "Não informado"
        weight_txt = "Não informado"
        imc_txt = "Não informado"
        glycated_hemoglobin_txt = "Não informado"
        blood_pressure_txt = "Não informado"
        hdl_txt = "Não informado"
        ldl_txt = "Não informado"
        framingham_score_txt = "Não informado"
        abdominal_circumference_txt = "Não informado"

        if height != None and height.get_value() != None:
            height_txt = str(height.get_value()) + ' cm'
        if weight != None and weight.get_value() != None:
            weight_txt = str(weight.get_value()) + ' kg'
        if imc != None and imc.get_value() != None:
            imc_txt = imc.get_value()
        if glycated_hemoglobin != None and glycated_hemoglobin.get_value() != None:
            glycated_hemoglobin_txt = glycated_hemoglobin.get_value()
        if blood_pressure != None and blood_pressure.get_value() != None:
            blood_pressure_txt = blood_pressure.get_value()
        if hdl != None and hdl.get_value() != None:
            hdl_txt = hdl.get_value()
        if ldl != None and ldl.get_value() != None:
            ldl_txt = ldl.get_value()
        if framingham_score != None and framingham_score.get_value() != None:
            framingham_score_txt = framingham_score.get_value()
        if abdominal_circumference != None and abdominal_circumference.get_value() != None:
            abdominal_circumference_txt = abdominal_circumference.get_value()
            
        last_data_str = f"dados recentes de altura: {str(height_txt)}, peso: {str(weight_txt)}, índice de massa corporal: {str(imc_txt)}, hemoglobina glicada: {str(glycated_hemoglobin_txt)}, pressão arterial: {str(blood_pressure_txt)}, hdl: {str(hdl_txt)}, ldl: {str(ldl_txt)}, score de Framingham: {str(framingham_score_txt)}, circunferência abdominal: {str(abdominal_circumference_txt)}"

        texto_adicional = f"""
            Com valores de exames e medições: 
            Altura: {str(height_txt)}
            Peso: {str(weight_txt)}
            Índice de massa corporal (imc): {str(imc_txt)}
            hemoglobina glicada (hemoglobina_glicada): {str(glycated_hemoglobin_txt)}
            pressão arterial (pressao_arterial): {str(blood_pressure_txt)}
            hdl: {str(hdl_txt)}
            ldl: {str(ldl_txt)}
        """
    primeira_consulta = ""
    if len(first_measurements) > 0:

        height = next((x for x in first_measurements if x.type == MeasurementTypeEnum.ALTURA), None)
        weight = next((x for x in first_measurements if x.type == MeasurementTypeEnum.PESO), None)
        imc = next((x for x in first_measurements if x.type == MeasurementTypeEnum.IMC), None)
        glycated_hemoglobin = next((x for x in first_measurements if x.type == MeasurementTypeEnum.HEMOGLOBINA_GLICADA), None)
        blood_pressure = next((x for x in first_measurements if x.type == MeasurementTypeEnum.PRESSAO_ARTERIAL), None)
        hdl = next((x for x in first_measurements if x.type == MeasurementTypeEnum.HDL), None)
        framingham_score = next((x for x in first_measurements if x.type == MeasurementTypeEnum.ESCORE_FRAMINGHAM), None)
        ldl = next((x for x in first_measurements if x.type == MeasurementTypeEnum.LDL), None)
        abdominal_circumference = next((x for x in first_measurements if x.type == MeasurementTypeEnum.CIRCUNFERENCIA_ABDOMINAL), None)

        height_txt = "Não informado"
        weight_txt = "Não informado"
        imc_txt = "Não informado"
        glycated_hemoglobin_txt = "Não informado"
        blood_pressure_txt = "Não informado"
        hdl_txt = "Não informado"
        ldl_txt = "Não informado"
        framingham_score_txt = "Não informado"
        abdominal_circumference_txt = "Não informado"


        if height != None and height.get_value() != None:
            height_txt = str(height.get_value()) + ' cm'
        if weight != None and weight.get_value() != None:
            weight_txt = str(weight.get_value()) + ' kg'
        if imc != None and imc.get_value() != None:
            imc_txt = imc.get_value()
        if glycated_hemoglobin != None and glycated_hemoglobin.get_value() != None:
            glycated_hemoglobin_txt = glycated_hemoglobin.get_value()
        if blood_pressure != None and blood_pressure.get_value() != None:
            blood_pressure_txt = blood_pressure.get_value()
        if hdl != None and hdl.get_value() != None:
            hdl_txt = hdl.get_value()
        if ldl != None and ldl.get_value() != None:
            ldl_txt = ldl.get_value()
        if framingham_score != None and framingham_score.get_value() != None:
            framingham_score_txt = framingham_score.get_value()
        if abdominal_circumference != None and abdominal_circumference.get_value() != None:
            abdominal_circumference_txt = abdominal_circumference.get_value()
            
        first_data_str = f"nos dados da primeira consulta de altura: {str(height_txt)}, peso: {str(weight_txt)}, índice de massa corporal: {str(imc_txt)}, hemoglobina glicada: {str(glycated_hemoglobin_txt)}, pressão arterial: {str(blood_pressure_txt)}, hdl: {str(hdl_txt)}, ldl: {str(ldl_txt)}, score de Framingham: {str(framingham_score_txt)}, circunferência abdominal: {str(abdominal_circumference_txt)}"

        if first_measurement != None:
            fist_date = first_measurement.date.strftime('%d/%m/%Y')
        primeira_consulta = f"Com valores de exames e medições: "
        primeira_consulta = primeira_consulta +  f"""
            \n
            Altura: {str(height_txt)}
            Peso: {str(weight_txt)}
            Índice de massa corporal (imc): {str(imc_txt)}
            hemoglobina glicada (hemoglobina_glicada): {str(glycated_hemoglobin_txt)}
            pressão arterial (pressao_arterial): {str(blood_pressure_txt)}
            hdl: {str(hdl_txt)}
            ldl: {str(ldl_txt)}
        """
    sobre_paciente = ""
    if primeira_consulta == "" and texto_adicional == "":
        sobre_paciente = "Sem histórico do paciente"
    else:
        sobre_paciente = f"""
            {primeira_consulta}
            {texto_adicional}
        """
    return primeira_consulta, texto_adicional, fist_date, current_date

def send_image(senderToken, phone_instance_id, message):
    filename = "campanha_27"
    type = 'image' 
    llm_client = None,
    fl_audio = False, 
    accent = False, 
    email = None

    send_message(message, senderToken, type, llm_client, phone_instance_id, fl_audio, accent, email, filename)

ids_send = []
with open('users_form.csv', newline='', encoding='utf-8') as f:
    leitor = csv.reader(f)
    
    # Iterar pelas linhas do CSV
    for linha in leitor:
        ids_send.append(int(linha[0]))

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
            -- u.test_number = 3
            -- AND is_happvida = true
             -- OR (u.id = 37865 OR u.id = 37864 OR u.id = 145)
           u.id = 145
          --u.id = 37874
        
        order by p.created asc
    '''
    #AND NOT EXISTS (SELECT * FROM public.conversation_message cm WHERE cm.owner_id = u.id AND active_type = 'PROATIVIDADE_CAMPANHA_1')            
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
        #fl_audio = values[4]
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
        #response = response.choices[0].message.content
        #response = f'''
#Olá, tudo bem? 💛
#Fiquei muito feliz em conversar com você nos últimos tempos. Pelas nossas interações, você foi identificada como uma das 44 pessoas com maior chance de manter a hemoglobina controlada, entre todas que conversaram comigo. Isso é uma ótima notícia — Parabéns! ✨
#Sua participação tem feito a diferença, e agora eu adoraria saber: como foi essa experiência pra você?
#É rapidinho! Você pode me contar clicando aqui: 👉 https://forms.gle/dECsDtGZqRLAwq3o9
#Se preferir, posso te lembrar mais tarde ou pedir pra alguém da nossa equipe te ligar e fazer as perguntinhas por telefone. É só me avisar! 💬
        #'''
        print(response)
        
        #response = "Comece o ano com propósito, crie metas simples e alcançaveis para transformar sua saúde e bem-estar em 2025!"
        response = f"""Hoje é dia de celebrar você — que cuida, que se doa, que enfrenta tudo com um amor que não tem medida. 🌸🩷

Que o seu dia seja cheio de carinho, reconhecimento e, principalmente, de descanso merecido.

Feliz Dia das Mães! 
Com todo meu carinho,
 MarIA 
💐❤️✨
"""
        
        create_thread_message_assistant (llm_client, phone.thread_id, response)
        vsvfwefwefe
        if fl_audio == True:
            gggg
            send_image(senderToken=phone.identifier, phone_instance_id=phone.phone_instance_id, message="")
            audio_filename = send_message(message = response, senderToken = phone.identifier, type = 'audio', llm_client = llm_client, 
                phone_instance_id = phone.phone_instance_id, fl_audio = fl_audio,
                accent=accent, email=email, filename=None)

            create_conversation_message(conversation = conversation, phone = phone, 
                text = response, owner_type = OwnerTypeEnum.AGENT, type='audio', llm_client = llm_client, db = db,
                audio_filename=None, accent=phone.user.accent, fl_audio=phone.user.fl_audio, activeType=MessageActiveTypeEnum.FORMULARIO)
        else:
            bbbb
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

    

    

    