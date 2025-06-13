def string_validation(text):
    if text == None or (text+'').strip() == '':
        return False
    return True