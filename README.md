# Desafio Scrapy N2


### Este projeto usa Scrapy para coleta de produtos e RQ (Redis Queue) para execução assíncrona.
### As execuções dos spiders não são chamadas diretamente, mas sim enfileiradas através de um endpoint HTTP.


## Instalação

1. Clonar o repositório:
```
git clone https://github.com/rodrigodasilv/coteFacil-py.git
git checkout n2
```
2. Instale as dependências:
```
pip install -r requirements.txt
```
3. Subir o banco de dados Redis e a API feita com flask:
```
docker compose up --build
```
4. Iniciar um worker (Utilizar Linux ou WSL)
```
rq worker
```

## Funcionalidades

- Recebe informações de usuario, senha e callback_url na API
- Enfileira os processos com Redis Queue 
- Posteriormente, o worker realiza login no site via dados recebidos anteriormente pela API.
- Captura cookies e token JWT para autenticação.
- Consulta a listagem de produtos página por página.
- Faz login na callback_url e cadastra o produto no endpoint /produto.

## Observações

Certifique-se de que o usuario e senha que serão enfileirados são credenciais válidas.
O worker precisa estar rodando para processar as tasks.
O Redis deve estar acessível no mesmo host/rede em que o worker será executado.
