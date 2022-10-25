# CloudFaster Academy: Demo de aplicação que recebe dados enviados via Api Gateway e grava no DynamoDB
# Pré-requisitos: 
# 1) Tabela do DynamoDB
# 2) IAM Role com permissão de escrita/leitura na tabela do DynamoDB

import json
import boto3 #AWS SDK para Python3
import decimal
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from botocore.paginate import TokenEncoder

# substitua essa variavel com o nome da tabela criada no DynamoDB
DYNAMODB_TABLE = "lab-dynamodb"
# subistitua essa variavel com a região da AWS onde sua tabela do DynamoDB foi criada
AWS_REGION = "us-east-1"

def defaultDecimal(o):
    if isinstance(o, decimal.Decimal):
        return float(o)
    raise TypeError

def scanItensDynamoDB():
    """Busca todos os dados de uma tabela no dynamo
    """
    client = boto3.client('dynamodb', region_name=AWS_REGION)
    try:
        s = TypeSerializer()
        d = TypeDeserializer()
        encoder = TokenEncoder()
        paginator = client.get_paginator('scan')
        nextToken = None
        totalRows = 0
        items = []
        # inicia as opcoes do scan
        scan_options = {
            "TableName": DYNAMODB_TABLE
        }
        # faz a consulta com paginacao
        page_iterator = paginator.paginate(**scan_options)
        for i, page in enumerate(page_iterator):
            if "Items" in page:
                for item in page['Items']:
                    items.append({ k: d.deserialize(value=v) for k, v in item.items() })
            if "LastEvaluatedKey" in page:
                nextToken = encoder.encode({"ExclusiveStartKey": page["LastEvaluatedKey"]})
        return { 
            "success": True, 
            "message": "Dados recuperados com sucesso.", 
            "data": { 
                "totalRows": totalRows if totalRows > 0 else len(items), 
                "numRows": len(items),
                "nextToken": nextToken,
                "result": json.loads(json.dumps(items, default=defaultDecimal))
            }
        }
    except Exception as err:
        print("Falha ao obter dados do DynamoDB")
        print("Table: ", DYNAMODB_TABLE)
        print("Region: ", AWS_REGION)
        print(err)
        return { "success": False, "msg": str(err), "data": {} }

def lambda_handler(event, context):
    """Função principal da aplicação, essa função deve ser informada como a "handler" do Lambda
    Parâmetros: 
        event: dict - Contém os dados do evento que foi o acionador do Lambda
        context: dict - Contém os dados do contexto da requisição, dados do ambiente, id da requisição, etc...
    """
    # funcao principal da aplicação, responsável por receber os dados do evento e contexto da requisição
    print("Dados do evento recebido:")
    print(event)
    print("Dados do contexto recebido:")
    print(context)
    # le e retorna o resultado do DynamoDB
    return scanItensDynamoDB()