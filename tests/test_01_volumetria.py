"""
Driver 1 — VOLUMETRIA
Testes de paginacao e controle de volume de dados.
"""


class TestVolumetriaBugV1:

    def test_v1_retorna_todos_registros_sem_limite(self, client, seed_notas):
        response = client.get("/v1/notas")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 50

    def test_v1_nao_aceita_parametro_limit(self, client, seed_notas):
        response = client.get("/v1/notas?limit=5")
        data = response.json()
        assert len(data) > 5


class TestVolumetriaFixV2:

    def test_v2_paginacao_padrao_20(self, client, seed_notas):
        response = client.get("/v2/notas")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 20

    def test_v2_paginacao_com_limit(self, client, seed_notas):
        response = client.get("/v2/notas?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_v2_paginacao_com_offset(self, client, seed_notas):
        page1 = client.get("/v2/notas?limit=10&offset=0").json()
        page2 = client.get("/v2/notas?limit=10&offset=10").json()
        ids_page1 = {n["id"] for n in page1}
        ids_page2 = {n["id"] for n in page2}
        assert ids_page1.isdisjoint(ids_page2)

    def test_v2_limite_maximo_100(self, client, seed_notas):
        response = client.get("/v2/notas?limit=500")
        assert response.status_code == 422

    def test_v2_limit_minimo_1(self, client, seed_notas):
        response = client.get("/v2/notas?limit=0")
        assert response.status_code == 422
