import re


PATTERN_RA = "^[A-z0-9]{7}$"
PATTERN_NOME = "^(?=^.{2,60}$)^[A-ZÀÁÂĖÈÉÊÌÍÒÓÔÕÙÚÛÇ][a-zàáâãèéêìíóôõùúç]+(?:[ ](?:das?|dos?|de|e|[A-ZÀÁÂĖÈÉÊÌÍÒÓÔÕÙÚÛÇ][a-zàáâãèéêìíóôõùúç]+))*$"
PATTERN_TELEFONE = "^\(?(?:[14689][1-9]|2[12478]|3[1234578]|5[1345]|7[134579])?\)? ?(?:[2-8]|9[0-9])[0-9]{3}\-?[0-9]{4}$"
PATTERN_EMAIL = "^[a-z0-9.]+@aluno\.unip\.br$"

dados_validos = ["NADFASD", "Abobrinho Santos",
        "980443231", "abobrinho.santos13@aluno.unip.br"]

dados_invalidos = ["NADFASD@", "Abobrinho 123 Santos",
        "11912345678 40028922 é o funk do yudi que vai dar playstation 2", "daljksbanfsjdgkvadsga asdhgkgl  isgdaoig hashdgap .com"]


# Valida os campos com regex
nome_valido = re.match(PATTERN_NOME, dados_validos[1])
ra_valido = re.match(PATTERN_RA, dados_validos[0])
tel_valido = re.match(PATTERN_TELEFONE, dados_validos[2])
email_valido = re.match(PATTERN_EMAIL, dados_validos[3])
print(ra_valido)
print(nome_valido)
print(tel_valido)
print(email_valido)

ra_invalido = re.match(PATTERN_RA, dados_invalidos[0])
nome_invalido = re.match(PATTERN_NOME, dados_invalidos[1])
tel_invalido = re.match(PATTERN_TELEFONE, dados_invalidos[2])
email_invalido = re.match(PATTERN_EMAIL, dados_invalidos[3])
print(ra_invalido)
print(nome_invalido)
print(tel_invalido)
print(email_invalido)
