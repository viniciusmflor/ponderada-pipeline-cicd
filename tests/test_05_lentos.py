"""Testes lentos artificiais para medir impacto no tempo do pipeline."""
import time


class TestLentos:

    def test_lento_0(self):
        time.sleep(0.5)
        assert True

    def test_lento_1(self):
        time.sleep(0.5)
        assert True

    def test_lento_2(self):
        time.sleep(0.5)
        assert True

    def test_lento_3(self):
        time.sleep(0.5)
        assert True

    def test_lento_4(self):
        time.sleep(0.5)
        assert True
