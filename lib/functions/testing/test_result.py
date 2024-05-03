import json 
from fuzzywuzzy import fuzz

from lib.models.invoice_model import Invoice

def testResult(analizedInvoice: Invoice, jsonPath: str):    
    result:float = 0
    itemsCompared:int = 0  
    
    # Convierto el json perfecto guardado    
    with open(jsonPath, 'r') as file:
        file_content = file.read()
    
    perfect_invoice = dict(json.loads(file_content))
      
    # Tipo de factura
    analizedValue =  str(analizedInvoice.type)
    perfectValue =  str(perfect_invoice['type'])
    result = result + fuzz.ratio(analizedValue, perfectValue)
    itemsCompared = itemsCompared + 1
    
    # Elementos del encabezado
    for key, value in dict(analizedInvoice.header.__dict__).items():
        analizedValue = dict(analizedInvoice.header.__dict__).get(key)
        perfectValue = dict(perfect_invoice['header']).get(key)
        result = result + fuzz.ratio(analizedValue, perfectValue)
        itemsCompared = itemsCompared + 1
        
    # Elementos de los productos
    for i in range(len(analizedInvoice.items)):
        for key, value in dict(analizedInvoice.items[i].__dict__).items():
            analizedValue = dict(analizedInvoice.items[i].__dict__).get(key)
            perfectValue = dict(perfect_invoice['items'][i]).get(key)
            result = result + fuzz.ratio(analizedValue, perfectValue)
            itemsCompared =itemsCompared + 1
        
    # Elementos del pie
    for key, value in dict(analizedInvoice.footer.__dict__).items():
        analizedValue = dict(analizedInvoice.footer.__dict__).get(key)
        perfectValue = dict(perfect_invoice['footer']).get(key)
        result = result + fuzz.ratio(analizedValue, perfectValue)
        itemsCompared = itemsCompared + 1
            
    print( result / itemsCompared )
    
    
    
    

#print(fuzz.ratio("18/02/1932", "18/02/19832")/100)
    