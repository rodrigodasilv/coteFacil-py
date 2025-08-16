import scrapy
import json
import time
import jwt
from urllib.parse import urlencode

class ProductsSpider(scrapy.Spider):
    name = "ProductsSpider"
    cookies = {}
    pedido_payload_itens = []
    login_url = 'https://peapi.servimed.com.br/api/usuario/login'
    scrap_url = 'https://peapi.servimed.com.br/api/carrinho/oculto?siteVersion=4.0.27'
    scrap_payload = {"filtro": "",
                     "pagina": 1,
                     "registrosPorPagina": None,
                     "ordenarDecrescente": False,
                     "colunaOrdenacao": "nenhuma",
                     "clienteId": 267511,
                     "tipoVendaId": 1,
                     "fabricanteIdFiltro": 0,
                     "pIIdFiltro": 0,
                     "cestaPPFiltro": False,
                     "codigoExterno": 0,
                     "codigoUsuario": 22850,
                     "promocaoSelecionada": "",
                     "indicadorTipoUsuario": "CLI",
                     "kindUser": 0,
                     "xlsx": [],
                     "principioAtivo": "",
                     "master": False,
                     "kindSeller": 0,
                     "grupoEconomico": "",
                     "users": [518565, 267511],
                     "list": True}
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    login_callback_payload = {"username":"rodrigodasilva4", "password":"teste1234"}
    produtos = {}

    def __init__(self, usuario=None, senha=None,callback_url=None, id_pedido=None, produtosIn=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not usuario or not senha or not callback_url:
            raise ValueError("Usuario, senha e callback_url são obrigatórios")
        self.login_payload = {
            "usuario": usuario,
            "senha": senha
        }
        self.callback_url = callback_url
        self.id_pedido = id_pedido
        self.produtos = produtosIn

    def start_requests(self):
        self.logger.info("Iniciando login")
        try:
            yield scrapy.Request(
                self.login_url,
                method='POST',
                body=json.dumps(self.login_payload),
                headers=self.headers,
                callback=self.after_login,
                meta={'handle_httpstatus_list': [500]},
            )
        except Exception as e:
            self.logger.exception(f"Erro ao enviar request de login: {e}")

    def after_login(self, response):
        try:
            if "Usuário ou senha inválidos" in response.text:
                self.logger.error("Erro no login: usuário ou senha inválidos")
                return
            else:
                self.logger.info("Login realizado com sucesso")

            # Captura cookies da resposta de login
            cookies = response.headers.getlist('Set-Cookie')
            self.build_cookies(cookies)
            self.build_headers(cookies)
            for produto in self.produtos:
                yield self.build_request(produto)
        except Exception as e:
            self.logger.exception(f"Erro no after_login: {e}")

    def build_cookies(self, cookies):
        self.logger.info("Construindo cookies.")
        try:
            for cookie in cookies:
                cookie_str = cookie.decode()
                key_value = cookie_str.split(';')[0].split('=', 1)
                if len(key_value) == 2:
                    key, value = key_value
                    self.cookies[key] = value
        except Exception as e:
            self.logger.warning(f"Erro ao processar cookie: {cookie} | {e}")

    def build_headers(self, cookies):
        self.logger.info("Construindo headers.")
        try:
            if 'accesstoken' in self.cookies:
                    self.headers['Accesstoken'] = jwt.decode(self.cookies['accesstoken'], options={"verify_signature": False})['token']
            else:
                self.logger.warning("Cookie 'accesstoken' não encontrado!")
        except Exception as e:
            self.logger.exception(f"Erro ao construir headers com token JWT: {e}")
            
    def build_request(self, produto):
        self.logger.info("Construindo request para produto.")
        payload = self.scrap_payload.copy()
        payload["filtro"] = produto.get('gtin')
        return scrapy.Request(
            self.scrap_url,
            method='POST',
            body=json.dumps(payload),
            headers=self.headers,
            cookies=self.cookies,
            callback=self.parse,
            meta={'produto': produto}
        )

    def parse(self, response):
        produtoIn = response.meta.get('produto')
        try:
            data = json.loads(response.text)
            if isinstance(data, dict):
                produtoCompleto = data.get('lista', [])
            elif isinstance(data, list):
                produtoCompleto = data
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON: {e}")
            return
        if not produtoCompleto:
            self.logger.info(f"Nenhum produto encontrado. Finalizando spider.")
            return
        for produto in produtoCompleto:
            self.pedido_payload_itens.append({
                "id": str(produto.get('id')),
                "selectedPromotionID": -1,
                "taxValue": produto.get('valorImposto'),
                "quantityRequested": produtoIn.get('quantidade'),
                "baseValue": produto.get('valorBase'),
                "totalStIvaValue": produto.get('valorImposto'),
                "totalValue": produto.get('valorComDesconto') * produtoIn.get('quantidade'),
                "discount": produto.get('desconto'),
                "discountValue": produto.get('valorComDesconto'),
                "stIVA": produto.get('stIVA')
            })
        if len(self.pedido_payload_itens) == len(self.produtos):
            yield self.envia_pedido()


    def envia_pedido(self):
        pedido_payload = {
            "customerId": 267511,
            "userCode": 22850,
            "daysOfPlots": 28,
            "pieces": [21, 28, 35],
            "quantityPlots": 1,
            "sellId": 1,
            "itens": self.pedido_payload_itens
        }
        self.logger.info("Fazendo o pedido")
        return scrapy.Request(
            "https://peapi.servimed.com.br/api/Pedido/TrasmitirPedido",
            method='POST',
            body=json.dumps(pedido_payload),
            callback=self.after_pedido,
            cookies=self.cookies,
            headers=self.headers,
            meta={'handle_httpstatus_list': [400]}
        )
        
    def after_pedido(self, response):
        self.logger.info("Pedido realizado, iniciando callback")
        yield scrapy.Request(
            self.callback_url + '/oauth/token',
            method='POST',
            body=urlencode(self.login_callback_payload),
            callback=self.after_login_callback,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            },
            meta={'handle_httpstatus_list': [400]}
        )
            
    def after_login_callback(self, response):
        try:
            if response.status == 400:
                self.logger.error("Erro no login do callback: usuário ou senha inválidos")
                return
            else:
                self.logger.info("Login no callback realizado com sucesso")

            headers = {}
            headers['Authorization'] = f"Bearer {response.json().get('access_token', '')}"
            
            callback_json = {
                "codigo_confirmacao": self.id_pedido,
                "status": "pedido_realizado"
            }
            # Enviar payload para o callback
            self.logger.info("Enviando payload ao callback")
            yield scrapy.Request(
                self.callback_url + '/pedido/' + str(self.id_pedido),
                method='PATCH',
                body=json.dumps(callback_json),
                headers=headers,
                callback=self.after_callback,
                meta={'handle_httpstatus_list': [404]}
            )
        except Exception as e:
            self.logger.exception(f"Erro no after_login_callback: {e}")
            
    def after_callback(self, response):
        try:
            if response.status == 200:
                self.logger.info("Payload enviado com sucesso ao callback")
            else:
                self.logger.error(f"Erro ao enviar payload ao callback: Status {response.status}")
        except Exception as e:
            self.logger.exception(f"Erro no after_callback: {e}")

