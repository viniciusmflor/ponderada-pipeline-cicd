"""Teste com falha proposital para experimento CI/CD."""


def test_soma_incorreta():
    """Falha proposital: 1+1 nao eh 3."""
    assert 1 + 1 == 2, "Corrigido: soma correta"
