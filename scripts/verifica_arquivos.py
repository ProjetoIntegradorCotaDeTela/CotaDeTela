# Configuração do ambiente

import os
import csv

from carrega_arquivos import carrega_arquivos

arquivos = carrega_arquivos()
print(f"\n{len(arquivos)} arquivos carregados.")

# Parâmetros

SEPARADOR = ";"
ENCODING = "utf-8"

# Verifica index dos arquivos csv

print("\nVerificação do Índice dos Arquivos CSV:\n")

IndexPadrao = [
    'DATA_EXIBICAO', 'SESSAO', 'TITULO_ORIGINAL', 'TITULO_BRASIL',
    'CPB_ROE', 'AUDIO', 'LEGENDADA', 'PAIS_OBRA', 'REGISTRO_SALA',
    'NOME_SALA', 'PUBLICO', 'REGISTRO_GRUPO_EXIBIDOR', 'REGISTRO_EXIBIDOR',
    'REGISTRO_COMPLEXO', 'MUNICIPIO_SALA_COMPLEXO', 'UF_SALA_COMPLEXO',
    'RAZAO_SOCIAL_EXIBIDORA', 'CNPJ_EXIBIDORA',
]

print("\nÍndice Padrão: ", IndexPadrao)

divergentes = []

for arq in arquivos:
    with open(arq, encoding=ENCODING) as f:
        header = next(csv.reader(f, delimiter=SEPARADOR))
    if header != IndexPadrao:
        divergentes.append((os.path.basename(arq), header))

if not divergentes:
    print(f"Todos os {len(arquivos)} arquivos têm o schema esperado.")
else:
    print(f"{len(divergentes)} arquivos divergentes:\n")
    for nome, cols in divergentes:
        print(f"  {nome}")
        print(f"    {cols}")