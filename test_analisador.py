import tempfile
import unittest
from pathlib import Path

from analisador import analisar_log


class AnalisadorLogTest(unittest.TestCase):
    def criar_log(self, conteudo: str) -> Path:
        self.pasta = tempfile.TemporaryDirectory()
        caminho = Path(self.pasta.name) / "teste.log"
        caminho.write_text(conteudo, encoding="utf-8")
        return caminho

    def tearDown(self) -> None:
        if hasattr(self, "pasta"):
            self.pasta.cleanup()

    def test_conta_sucessos_e_falhas(self) -> None:
        caminho = self.criar_log(
            "2026-08-13 08:00:00 | 192.168.1.10 | LOGIN_SUCESSO | ana\n"
            "2026-08-13 08:00:10 | 192.168.1.20 | LOGIN_FALHA | bob\n"
        )
        resultado = analisar_log(caminho)
        self.assertEqual(resultado["total_sucessos"], 1)
        self.assertEqual(resultado["total_falhas"], 1)

    def test_detecta_tres_falhas_em_sessenta_segundos(self) -> None:
        caminho = self.criar_log(
            "2026-08-13 08:00:00 | 192.168.1.25 | LOGIN_FALHA | admin\n"
            "2026-08-13 08:00:10 | 192.168.1.25 | LOGIN_FALHA | admin\n"
            "2026-08-13 08:00:20 | 192.168.1.25 | LOGIN_FALHA | admin\n"
        )
        resultado = analisar_log(caminho)
        self.assertEqual(resultado["alertas"][0]["ip"], "192.168.1.25")
        self.assertEqual(resultado["alertas"][0]["intervalo"], 20)

    def test_ignora_linha_invalida(self) -> None:
        caminho = self.criar_log("LINHA INVÁLIDA\n")
        resultado = analisar_log(caminho)
        self.assertEqual(resultado["total_sucessos"], 0)
        self.assertEqual(resultado["total_falhas"], 0)


if __name__ == "__main__":
    unittest.main()
