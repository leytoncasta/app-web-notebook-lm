def structure_question(texto, prompt):
    
    concat = " ".join(texto)

    return f'''Atencion: A continuación se proporciona un 
    contexto detallado que debe utilizarse para responder la siguiente pregunta, 
    sin tener en cuenta ningún otro conocimiento preentrenado. 
    Contexto: 
    {concat}. 
    Pregunta: 
    {prompt}'''
   