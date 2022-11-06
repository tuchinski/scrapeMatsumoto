import json
import requests
import dicttoxml
import time
import logging

def upload_produtos(apikey, json_file = None, ):
    dicttoxml.LOG.setLevel(logging.ERROR)
    
    if(json_file == None):
        with open('teste_produtos.json','r') as file:
            produtos = json.loads(file.read())
    else:
        produtos = json.loads(json_file)
    # apikey = "7545bc9c59aa9d752f77af8516b423db305e3c90354280af5b6d6023cfa6e70d0767111a"
    i = 1
    for produto in produtos:
        try:
            print('[INFO] -> Cadastrando produto {}'.format(produto['descricao']))
            xml_file = dicttoxml.dicttoxml(produto,custom_root='produto' , attr_type=False).decode('utf-8')
            xml_file = xml_file.replace("<item>"," ")
            xml_file = xml_file.replace("</item>"," ")
            
            # print(xml_file)
            # exit()

            payload  = {
                'apikey': apikey,
                'xml': xml_file
            }
            # with open('a','a') as teste:
            #     teste.write(xml_file)
            response = requests.post('https://bling.com.br/Api/v2/produto/json/', payload)
            time.sleep(0.5)
            
            if response.status_code == 201:
                logging.info('Produto {} cadastrado com sucesso!!'.format(produto['descricao']))
                print('[INFO] -> Produto {} cadastrado com sucesso!!'.format(produto['descricao']))
            else:
                print('[WARN] -> Erro ao cadastrar produto {}'.format(produto['descricao']))
                logging.error(f"Erro ao cadastrar o produto {produto['descricao']}")
                logging.error(response.text)
        except Exception as ex:
            logging.error('Erro ao cadastrar produto no bling')
            print('[ERR] -> Erro ao cadastrar o produto no BLING')
            print('[ERR] -> Erro: {}'.format(ex))
            
        # print(i, response)
        # exit()
        i += 1

if __name__ == "__main__":
    upload_produtos()