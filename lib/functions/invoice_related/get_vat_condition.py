from fuzzywuzzy import fuzz

vatConditions = [
    {"id": 1, "name": "IVA Responsable Inscripto"},
    {"id": 2, "name": "IVA Responsable no Inscripto"},
    {"id": 3, "name": "IVA no Responsable"},
    {"id": 4, "name": "IVA Sujeto Exento"},
    {"id": 5, "name": "Consumidor Final"},
    {"id": 6, "name": "Responsable Monotributo"},
    {"id": 7, "name": "Sujeto No Categorizado"},
    {"id": 8, "name": "Proveedor del Exterior"},
    {"id": 9, "name": "Cliente del Exterior"},
    {"id": 10, "name": "IVA Liberado - Ley Nº 19.640"},
    {"id": 11, "name": "IVA Responsable Inscripto - Agente de Percepción"},
    {"id": 12, "name": "Pequeño Contribuyente Eventual"},
    {"id": 13, "name": "Monotributista Social"},
    {"id": 14, "name": "Pequeño Contribuyente Eventual Social"},
]


def getVatCondition(key_to_match):
    max_ratio = 0
    result = 0
    for vatCondition in vatConditions:
        ratio = fuzz.ratio(vatCondition["name"], key_to_match)
        if ratio > max_ratio:
            result = vatCondition["id"]
            max_ratio = ratio
    return result
