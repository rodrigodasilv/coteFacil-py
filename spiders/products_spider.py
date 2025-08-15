import scrapy
import json
import time
import jwt

class ProductsSpider(scrapy.Spider):
    name = "ProductsSpider"
    cookies = {}
    login_url = 'https://peapi.servimed.com.br/api/usuario/login'
    login_payload = {
        "usuario": "juliano@farmaprevonline.com.br",
        "senha": "a007299A"
    }
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
    scrap_cookies = {}
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

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
            yield self.build_request(1)
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
            
    def build_request(self, pagina):
        self.logger.info(f"Solicitando página {pagina}...")
        self.scrap_payload["pagina"] = pagina
        return scrapy.Request(
            self.scrap_url,
            method='POST',
            body=json.dumps(self.scrap_payload),
            headers=self.headers,
            cookies=self.cookies,
            callback=self.parse,
            cb_kwargs={'pagina': pagina}
        )

    def parse(self, response, pagina):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON na página {pagina}: {e}")
            return
        produtos = data.get('lista', [])

        if not produtos:
            self.logger.info(f"Nenhum produto encontrado na página {pagina}. Finalizando spider.")
            return

        for produto in produtos:
            try:
                yield {
                    'gtin': produto.get('codigoBarras'),
                    'cod': produto.get('codigoExterno'),
                    'desc': f"{produto.get('descricao')} - {produto.get('fabricanteNome')}",
                    'preco': round(float(produto.get('valorBase', 0)), 2),
                    'estoque': produto.get('quantidadeEstoque')
                }
            except Exception as e:
                self.logger.warning(f"Erro ao processar produto {produto.get('codigoExterno')}: {e}")

        # Próxima página
        yield self.build_request(pagina + 1)
        
