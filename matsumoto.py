import requests
from bs4 import BeautifulSoup
import json
from base64 import b64encode
import upload_bling

def main():
    # url_produto = "https://www.lojasmatsumoto.com.br/mascara-para-festa-palhaco-colorido/p"
    # url_produto = "https://www.lojasmatsumoto.com.br/algema-prata/p"
    # url_produto = "https://www.lojasmatsumoto.com.br/kit-infantil-asa-de-borboleta-com-tiara-e-varinha-7/p"
    # categoria = "casa-e-decor/linha-disney"
    # categoria = "descartaveis-e-embalagens/caixa-de-pvc"

    with open('config.json', 'r') as arq:
        config = json.load(arq)

    api_code = config["api_code"]
    categorias = config["categorias"]
    fornecedor = config["fornecedor_id"]

    for categoria in categorias:
        dados_produtos = busca_produtos(categoria)

        dados_extraidos = []

        for produto in dados_produtos:
            dados_produto = extrai_dados_produto(produto["url"], 1.20, produto["marca"], fornecedor, produto['nome_produto'])
            dados_extraidos.append(dados_produto)

        upload_bling.upload_produtos(api_code, json.dumps(dados_extraidos))
        # print(json.dumps(dados_produto, indent=4))



def extrai_dados_produto(url, porcentagem, marca, fornecedor, nome_produto = None, json_produtos = None):
    infos = {}

    nome_url_produto = url.split("/")[-2]
    print(f'[INFO] -> Buscando informações do produto {nome_produto}')

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    a = soup.find_all("template")
    json_dados = json.loads(a[-1].script.text)

    # Tributação Origem 
    infos['origem'] = '0'
    # Peso Bruto
    infos['peso_bruto'] = 0.3
    # Peso Liquido
    infos['peso_liq'] = 0.3
    # Unidade
    infos['un'] = 'UN'
    infos['altura'] = 15
    infos['largura'] = 15
    infos['profundidade'] = 15
    infos["marca"] = marca

    # Fornecedor
    infos['idFabricante'] = fornecedor

    # Nome Produto
    infos['descricao'] = json_dados[f"Product:{nome_url_produto}"]["productName"]

    # Valor
    valor = json_dados[f'$Product:{nome_url_produto}.items.0.sellers.0.commertialOffer']['Price']
    valor = float(valor)
    valor = int(valor*porcentagem) + 0.9
    infos['vlr_unit'] = valor

    # URL Imagens
    local_id_imagens = json_dados[f'Product:{nome_url_produto}.items.0']["images"]
    
    url_imagens = []
    for image in local_id_imagens:
        id_imagem = image['id']

        obj_imagem = {
            'url': json_dados[id_imagem]['imageUrl']
        }
        url_imagens.append(obj_imagem)

    infos['imagens'] = url_imagens

    infos['estoque'] = int(json_dados[f'$Product:{nome_url_produto}.items.0.sellers.0.commertialOffer']['AvailableQuantity'])


    infos['codigo'] = json_dados[f"Product:{nome_url_produto}"]['productId']
    
    # Descricao
    descricao_complementar = json_dados[f'Product:{nome_url_produto}']['description']
    infos['descricaoCurta'] = descricao_complementar


    return infos

    print(json.dumps(infos, indent=4))

    
def busca_produtos(categoria: str):
    base_url_site = "https://www.lojasmatsumoto.com.br"
    url_pesquisa = "https://www.lojasmatsumoto.com.br/_v/segment/graphql/v1"
    base_json_busca = {
        "hideUnavailableItems": False,
        "skusFilter": "ALL",
        "simulationBehavior": "skip",
        "installmentCriteria": "MAX_WITHOUT_INTEREST",
        "productOriginVtex": False,
        "map": "c,c",
        "query": "casa-e-decor/linha-disney",
        "orderBy": "OrderByReleaseDateDESC",
        "from": 0,
        "to": 70,
        "selectedFacets": [
           
        ],
        "operator": "and",
        "fuzzy": "0",
        "searchState": None,
        "facetsBehavior": "Static",
        "categoryTreeBehavior": "default",
        "withFacets": False
    }

    base_json_envio = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": "67d0a6ef4d455f259737e4edb1ed58f6db9ff823570356ebc88ae7c5532c0866",
            "sender": "vtex.store-resources@0.x",
            "provider": "vtex.search-graphql@0.x"
        },
        "variables": ""
    }
    
    result_split = categoria.split("/")
    lista_parametros_busca = []
    for result in result_split:
        object_consulta = {
            "key": "c",
            "value": result
        }
        lista_parametros_busca.append(object_consulta)
    base_json_busca["selectedFacets"] = lista_parametros_busca

    query = b64encode(json.dumps(base_json_busca).encode("ascii")).decode("ascii")

    base_json_envio["variables"] = query

    params = {
        "extensions": json.dumps(base_json_envio)
    }

    response = requests.get(url_pesquisa, params)

    produtos = json.loads(response.text)
    dados_itens = []

    for produto in produtos["data"]["productSearch"]["products"]:
        dados_item = {}
        dados_item["url"] = f"{base_url_site}" + produto["link"]
        dados_item["marca"] = produto["brand"]
        dados_item["nome_produto"] = produto["productName"]

        dados_itens.append(dados_item)
        
    print(json.dumps(dados_itens, indent=4))
    return dados_itens    

if __name__ == "__main__":
    main()