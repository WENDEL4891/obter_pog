query_pog = '''
    SELECT * FROM
        bisp_rat_bos_pmmg
        
        WHERE
            nome_municipio IN (
                'DIVINOPOLIS',
                'SAO GONCALO DO PARA',
                'CARMO DO CAJURU',
                'CLAUDIO'            
            )
            AND
                unidade_responsavel_registro_nome NOT REGEXP ('(CPRV)|(MAMB)|(CPE)')
            AND
                natureza_codigo IN (
                    'Y01002', 'Y01003', 'Y01999', 'Y02001', 'Y02002', 'Y02003', 'Y02004', 'Y02005', 'Y02006',
                    'Y02007', 'Y02999', 'Y04001', 'Y04002', 'Y04003', 'Y04004', 'Y04005', 'Y04007', 'Y04008',
                    'Y04010', 'Y04999', 'Y07002', 'Y07006', 'Y07007', 'Y07008', 'Y07009', 'Y07010', 'Y07011',
                    'Y07999', 'Y08001', 'Y08002', 'Y08003', 'Y08005', 'Y08006', 'Y08007', 'Y08008', 'Y08009',
                    'Y08010', 'Y08999', 'Y09001', 'Y09003', 'Y09004', 'Y09005', 'Y09006', 'Y09007', 'Y09999',
                    'Y10001', 'Y10002', 'Y10003', 'Y10004', 'Y10007', 'Y10008', 'Y10009', 'Y10010', 'Y10999',
                    'Y15001', 'Y15010', 'Y15020', 'Y15030', 'Y15040', 'Y15050', 'Y15051', 'Y15052', 'Y15070',
                    'Y15099'
                )
            AND
                data_hora_fato >= '2022-01-01 00:00:00'        
'''

