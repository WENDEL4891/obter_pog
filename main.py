print('Iniciando execução...')

from socket import gaierror
import pandas as pd
import numpy as np
import geopandas as gpd
from impala.dbapi import connect
from datetime import datetime
from datetime import timedelta
import sys

import constants
print('Bibliotecas importadas')

# CONEXÃO COM BANCO DE DADOS CLOUDERA
try:
    conn = connect(host='clouderalb.prodemge.gov.br', port=21050, use_ssl=True, auth_mechanism="PLAIN",
               user='s134894', password='vndrls', database='reds_reporting')
    cursor = conn.cursor()
except:
    print('Conexão com o banco de dados OK')
    print('Conecte com a rede da PRODEMGE, desconecte outras redes, aguarde cerca de 30 segundos e execute novamente.')
    sys.exit()


# EXECUTA QUERY E TRATA DADOS
try:
    cursor.execute(constants.query_pog)
    results = cursor.fetchall()
    columns = [c[0] for c in cursor.description]
except:
    print('Conexão com o banco de dados OK')
    print('Conecte com a rede da PRODEMGE, desconecte outras redes, aguarde cerca de 30 segundos e execute novamente.')
    sys.exit()

df = pd.DataFrame(results, columns=columns)

cursor.close()
conn.close()
print('Dados retornados OK')

df['MES'] = df['data_hora_fato'].dt.month
df['DIA'] = df['data_hora_fato'].dt.day
df['numero_latitude'].fillna(0.0, inplace=True)
df['numero_longitude'].fillna(0.0, inplace=True)
df = gpd.GeoDataFrame(df, crs = "EPSG:4674", geometry=gpd.points_from_xy(df['numero_longitude'], df['numero_latitude']))

df_gpkg = gpd.read_file('7RPM_Setores_2021v8.gpkg', epg = "EPSG:4674", encoding='utf-8')


df = gpd.sjoin(df, df_gpkg[['CIA','SETOR', 'geometry']], 'left', predicate ='within')
df['CIA'].fillna('INDEFINIDA', inplace=True)

for index, row in df.iterrows():
    if row['CIA'] == 'INDEFINIDA':
        if df.loc[index, 'nome_municipio'] in ('CARMO DO CAJURU', 'SAO GONCALO DO PARA'):
            df.loc[index, 'CIA'] = '142ª CIA'
        elif df.loc[index, 'nome_municipio'] == 'CLAUDIO':
            df.loc[index, 'CIA'] = '139ª CIA'

df = df[
    [
        'numero_ocorrencia', 'data_hora_inclusao', 'data_hora_alteracao', 'data_hora_fechamento', 'digitador_cargo_efetivo', 'digitador_matricula', 'data_hora_fato', 'data_hora_comunicacao', 'natureza_codigo', 'natureza_descricao', 'natureza_descricao_longa', 'complemento_natureza_descricao_longa', 'logradouro_nome', 'tipo_logradouro_descricao', 'descricao_endereco', 'descricao_endereco_2', 'numero_endereco', 'descricao_complemento_endereco', 'nome_bairro', 'nome_municipio', 'descricao_ponto_referencia', 'numero_latitude', 'numero_longitude', 'data_hora_local', 'data_hora_final', 'historico_ocorrencia', 'relator_matricula', 'relator_nome', 'relator_cargo', 'relator_nome_unidade', 'unidade_area_militar_nome', 'unidade_responsavel_registro_nome', 'cep', 'data_hora_fim_preenchimento', 'MES', 'DIA', 'geometry', 'CIA', 'SETOR'        
    ]
]

df.rename(columns = {
            'complemento_natureza_descricao_longa': 'COMPLEMENTO_NATUREZA',
            'tipo_logradouro_descricao': 'LOGRADOURO_TIPO',
            'nome_municipio': 'MUNICIPIO',
            'numero_ocorrencia': 'NUMERO_RAT',
            'digitador_cargo_efetivo': 'POSTO_OU_GRADUACAO'
        }, inplace=True
)
df.columns = df.columns.str.upper()

print('Dados tratados OK')

# RESUME DADOS POR CIAS
df_cias = pd.pivot_table(df, columns='MES', index='CIA', aggfunc='count', values='NUMERO_RAT', fill_value=0)
df_cias['ACUM'] = df_cias.sum(axis=1)
df_cias.loc['Total'] = df_cias.sum(axis=0)
df_cias

print('Dados resumidos por Cias OK')

# RESUME DADOS POR CIAS E MUNICÍPIOS
df_cias_municipios = pd.pivot_table(df, columns='MES', index=('CIA', 'MUNICIPIO'), aggfunc='count', values='NUMERO_RAT', fill_value=0)
df_cias_municipios['ACUM'] = df_cias_municipios.iloc[:,:].sum(axis=1)
df_cias_municipios.loc[('23 BPM', 'TOTAL'), :] = df_cias_municipios.sum(axis=0)
df_cias_municipios = df_cias_municipios.astype('int16')
df_cias_municipios

print('Dados resumidos por Cias e municípios OK')

# SALVA DADOS EM EXCEL NA PASTA resultados/
hoje = datetime.now()
ontem = hoje - timedelta(days=1)
ontem_formatado = datetime.strftime(ontem,"%d-%m-%Y")

# Usando o ExcelWriter, cria um doc .xlsx, usando engine='xlsxwriter'
writer = pd.ExcelWriter(f'resultados/POG_01-01-2022_A_{ontem_formatado}.xlsx', engine='xlsxwriter')

# Armazena cada df em uma planilha diferente do mesmo arquivo
df_cias.to_excel(writer, sheet_name='por_cias')
df_cias_municipios.to_excel(writer, sheet_name='por_cias_e_municipios')
df.to_excel(writer, sheet_name='lista_todos_os_registros', index=False)

# Fecha o ExcelWriter e gera o arquivo .xlsx
writer.save()

print('Dados salvos na pasta resultados/')