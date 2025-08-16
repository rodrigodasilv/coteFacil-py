# Desafio Scrapy N3


### Este projeto usa Scrapy para coleta de produtos e RQ (Redis Queue) para execução assíncrona.
### As execuções dos spiders não são chamadas diretamente, mas sim enfileiradas através de um endpoint HTTP.


## Instalação

1. Clonar o repositório:
```
git clone https://github.com/rodrigodasilv/coteFacil-py.git
git checkout n3
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

- Recebe informações de usuario, senha, callback_url e produtosIn pela API.
- Enfileira os processos usando Redis Queue.
- Realiza login no sistema Servimed via Scrapy e captura cookies e token JWT para autenticação.
- Faz um pedido para o endpoint TrasmitirPedido a partir dos produtos informados na Queue.
- Realiza login no callback_url e envia o status do pedido (pedido_realizado) após a execução.

## Observações

Certifique-se de que o usuario e senha que serão enfileirados são credenciais válidas.
O worker precisa estar rodando para processar as tasks.
O Redis deve estar acessível no mesmo host/rede em que o worker será executado.

##Exemplo
Pedido criado no endpoint "/pedido"
<img width="1365" height="767" alt="image" src="https://github.com/user-attachments/assets/025d5822-3ca6-41d2-bcb5-29de614ddf14" />
Envio dos dados para enfileirar o processamento:
<img width="1365" height="767" alt="image" src="https://github.com/user-attachments/assets/e3b6acc0-0de4-471f-91ea-08c2611ac15c" />
Worker processando a fila para criar o pedido e atualizar o status do pedido através do endpoint "/pedido/:id"
<img width="940" height="567" alt="image" src="https://github.com/user-attachments/assets/26645797-1f38-4166-a173-334ca256400f" />
Pedido criado no website:
<img width="1290" height="571" alt="image" src="https://github.com/user-attachments/assets/99fc4373-b36b-4277-a5e4-c2317ee64f25" />
Status do pedido atualizado no endpoint "/pedido/:id"
<img width="1365" height="718" alt="image" src="https://github.com/user-attachments/assets/e832f089-83c7-46db-b1d1-05c631e8a903" />

