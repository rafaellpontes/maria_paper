from models import Measurement, MeasurementTypeEnum
import pytz
from datetime import datetime
from business.action_business import resolve_function
import time

class Maria:

  def __init__(self, assistant, client):
    self.assistant = assistant
    self.client = client

  def traduzir_dia_semana(self,dia_em_ingles):
    dias_semana = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }
    return dias_semana.get(dia_em_ingles, "Dia inválido")

  def get_medical_data (self, user, db):
    first_measurement = db.query(Measurement).filter_by(user_id=user.id).order_by(Measurement.created.asc()).first()
    first_measurements = db.query(Measurement).filter_by(user_id=user.id).distinct(Measurement.type).order_by(Measurement.type.asc()).order_by(Measurement.created.asc()).all()
    current_measurements = db.query(Measurement).filter_by(user_id=user.id).distinct(Measurement.type).order_by(Measurement.type.asc()).order_by(Measurement.created.desc()).all()

    last_data_str = ""
    first_data_str = ""

    texto_adicional = ""
    if len(current_measurements) > 0:
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
            Na mais recente consultas, suas medidas são: 
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
        
        fist_date = first_measurement.created.strftime('%d/%m/%Y')
        primeira_consulta = f"Sua primeira consulta aconteceu em {fist_date}. Os valores de exames e medições segue a relação"
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
    return sobre_paciente, first_data_str, last_data_str

  def get_instructions_2 (self, assistant, user, db):

    name = user.first_name + ' ' + user.last_name
    instructions = f"""
        PASTE HERE System Template Prompt (PT or EN)
    """
    timezone = pytz.timezone('America/Fortaleza')
    current_datetime = datetime.now(tz = timezone).strftime("%d/%m/%Y %H:%M")
    now = datetime.now()
    day_of_week = self.traduzir_dia_semana(now.strftime("%A"))
    #additional_instructions = f"Para referências temporais considere a data e hora atual como {current_datetime} no formato DD-MM-YYYY HH:mm."
    additional_instructions = f"Para o seu contexto temporal, a data de hoje é: {current_datetime} e o dia da semana é: {day_of_week}. Se solicitado agendamento de lembrete para datas ou horários passados, peça ao usuário uma nova data ou horário."

    return instructions, additional_instructions

  def run (self, thread_id, user, assistant, db):
    instructions, additional_instructions = self.get_instructions_2(assistant, user, db)

    #print(instructions)
    run = self.client.beta.threads.runs.create(thread_id, assistant_id = self.assistant.id, instructions=instructions, additional_instructions=additional_instructions)
    runStatus = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    while (runStatus.status != 'completed'):
      time.sleep(1)
      runStatus = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
      print('Status: ' + runStatus.status)
      if runStatus.status == 'requires_action':
        tools_to_call = runStatus.required_action.submit_tool_outputs.tool_calls

        tool_output_response = []
        for i in range(0,len(tools_to_call)):
          tool_to_call = tools_to_call[i]
          function_name = tool_to_call.function.name
          arguments = tools_to_call[i].function.arguments
          print(f"function_name: {function_name} and arguments: {arguments}")
          response = resolve_function(function_name, arguments, user.id, db, self.client)
          print({"tool_call_id": tool_to_call.id, "output": response})
          tool_output_response.append({"tool_call_id": tool_to_call.id, "output": response})
          
        runStatus = self.client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run.id, tool_outputs=tool_output_response)

    messages = self.client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value