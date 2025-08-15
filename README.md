# Desafio Scrapy N1

Este projeto é um **spider Scrapy** que faz login em um sistema, acessa a listagem de produtos e extrai informações específicas de cada produto.

---

## Instalação

1. Clonar o repositório:
```
git clone https://github.com/rodrigodasilv/coteFacil-py.git
cd <PASTA_DO_PROJETO>
```
2. Instale as dependências:
```
pip install -r requirements.txt
```
3. Executar o spider:
```
scrapy crawl ProductsSpider -o produtos.json
```
Este comando irá executar o spider e gerar um arquivo produtos.json com a lista de produtos extraídos.

## Funcionalidades

- Realiza login no site via API.
- Captura cookies e token JWT para autenticação.
- Consulta a listagem de produtos página por página.
- Extrai os seguintes campos de cada produto:
- - gtin: Código de barras (EAN)
- - cod: Código externo do produto
- - desc: Descrição completa do produto (descrição + fabricante)
- - preco: Valor base do produto
- - estoque: Quantidade em estoque
- Logging detalhado durante a execução, incluindo erros de login, processamento de cookies e parsing de JSON.

## Observações

Certifique-se de atualizar o login_payload com credenciais válidas.
