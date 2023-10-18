import re


PATTERN_RA = "^[A-z0-9]{7}$"
PATTERN_NOME = "^(?=^.{2,60}$)^[A-ZÀÁÂĖÈÉÊÌÍÒÓÔÕÙÚÛÇ][a-zàáâãèéêìíóôõùúç]+(?:[ ](?:das?|dos?|de|e|[A-ZÀÁÂĖÈÉÊÌÍÒÓÔÕÙÚÛÇ][a-zàáâãèéêìíóôõùúç]+))*$"


dados_validos = ["NADFASD", "Abobrinho Santos",
        "11912345678"]

dados_invalidos = ["NADFASD@", "Abobrinho 123 Santos",
        "11912345678 40028922 é o funk do yudi que vai dar playstation 2"]


# Valida os campos com regex
ra_valido = re.match(PATTERN_RA, dados_validos[0])
nome_valido = re.match(PATTERN_NOME, dados_validos[1])
print(ra_valido)
print(nome_valido)

ra_invalido = re.match(PATTERN_RA, dados_invalidos[0])
nome_invalido = re.match(PATTERN_NOME, dados_invalidos[1])
print(ra_invalido)
print(nome_invalido)