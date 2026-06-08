"""Testes extras para aumentar volume e medir impacto."""


class TestStringOperacoes:

    def test_upper(self):
        assert "hello".upper() == "HELLO"

    def test_lower(self):
        assert "WORLD".lower() == "world"

    def test_strip(self):
        assert "  abc  ".strip() == "abc"

    def test_replace(self):
        assert "foo bar".replace("foo", "baz") == "baz bar"

    def test_split(self):
        assert "a,b,c".split(",") == ["a", "b", "c"]

    def test_join(self):
        assert ",".join(["x", "y"]) == "x,y"

    def test_startswith(self):
        assert "python".startswith("py")

    def test_endswith(self):
        assert "python".endswith("on")

    def test_contains(self):
        assert "th" in "python"

    def test_len(self):
        assert len("abc") == 3
