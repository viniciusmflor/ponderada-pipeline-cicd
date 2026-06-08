"""
Driver 4 — SEGURANCA
Testes de SQL Injection, validacao de CNPJ e autenticacao JWT.
"""


class TestSegurancaBugV1:

    def test_v1_sql_injection_retorna_dados_de_outros_cnpjs(self, client, seed_notas):
        cnpj_legitimo = seed_notas[0].emitente_cnpj
        response_legitima = client.get(f"/v1/notas/busca?cnpj={cnpj_legitimo}")
        count_legitimo = len(response_legitima.json()) if response_legitima.status_code == 200 else 0

        payload_injecao = "' OR '1'='1"
        response_injecao = client.get(f"/v1/notas/busca?cnpj={payload_injecao}")

        if response_injecao.status_code == 200:
            count_injecao = len(response_injecao.json())
            assert count_injecao > count_legitimo
            assert count_injecao > 0

    def test_v1_aceita_cnpj_invalido(self, client):
        response = client.get("/v1/notas/busca?cnpj=abc')--")
        assert response.status_code in [200, 500]


class TestSegurancaFixV2:

    def test_v2_sql_injection_bloqueado(self, client, seed_notas):
        payload = "' OR '1'='1"
        response = client.get(f"/v2/notas/busca?cnpj={payload}")
        assert response.status_code == 422

    def test_v2_valida_formato_cnpj(self, client):
        response = client.get("/v2/notas/busca?cnpj=11222333000100")
        assert response.status_code == 200

        response = client.get("/v2/notas/busca?cnpj=abcdefghijklmn")
        assert response.status_code == 422

        response = client.get("/v2/notas/busca?cnpj=1122233")
        assert response.status_code == 422

        response = client.get("/v2/notas/busca?cnpj=11.222.333/0001")
        assert response.status_code == 422

    def test_v2_busca_retorna_apenas_cnpj_especifico(self, client, seed_notas):
        cnpj = seed_notas[0].emitente_cnpj
        response = client.get(f"/v2/notas/busca?cnpj={cnpj}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        for nota in data:
            assert nota["emitente_cnpj"] == cnpj

    def test_v2_autenticacao_sem_token(self, client):
        response = client.get("/v2/notas/protegido")
        assert response.status_code == 401

    def test_v2_autenticacao_token_invalido(self, client):
        response = client.get(
            "/v2/notas/protegido",
            headers={"Authorization": "Bearer token-forjado-123"}
        )
        assert response.status_code == 401

    def test_v2_autenticacao_token_valido(self, client):
        login_response = client.post(
            "/v2/auth/token",
            json={"username": "admin", "password": "admin123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        assert token

        response = client.get(
            "/v2/notas/protegido",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["user"] == "admin"

    def test_v2_login_credenciais_invalidas(self, client):
        response = client.post(
            "/v2/auth/token",
            json={"username": "admin", "password": "senha-errada-123"}
        )
        assert response.status_code == 401
