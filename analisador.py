from datetime import datetime
from pathlib import Path


LIMITE_FALHAS = 3
JANELA_SEGUNDOS = 60


def analisar_log(caminho_log: Path) -> dict:
    total_sucessos = 0
    total_falhas = 0
    falhas_por_ip: dict[str, int] = {}
    horarios_falhas_por_ip: dict[str, list[datetime]] = {}

    with caminho_log.open("r", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        dados = linha.split("|")
        if len(dados) != 4:
            print(f"AVISO: linha inválida ignorada: {linha}")
            continue

        data_hora, endereco_ip, evento, usuario = (
            dado.strip() for dado in dados
        )

        try:
            momento = datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"AVISO: data inválida ignorada: {data_hora}")
            continue

        if evento == "LOGIN_SUCESSO":
            total_sucessos += 1
        elif evento == "LOGIN_FALHA":
            total_falhas += 1
            falhas_por_ip[endereco_ip] = falhas_por_ip.get(endereco_ip, 0) + 1
            horarios_falhas_por_ip.setdefault(endereco_ip, []).append(momento)

        print(f"Data: {data_hora}")
        print(f"IP: {endereco_ip}")
        print(f"Evento: {evento}")
        print(f"Usuário: {usuario}")
        print("-" * 40)

    alertas = []
    for ip, horarios in horarios_falhas_por_ip.items():
        for indice in range(len(horarios) - LIMITE_FALHAS + 1):
            primeira_falha = horarios[indice]
            ultima_falha = horarios[indice + LIMITE_FALHAS - 1]
            intervalo = (ultima_falha - primeira_falha).total_seconds()
            if intervalo <= JANELA_SEGUNDOS:
                alertas.append({"ip": ip, "intervalo": intervalo})
                break

    return {
        "total_sucessos": total_sucessos,
        "total_falhas": total_falhas,
        "falhas_por_ip": falhas_por_ip,
        "alertas": alertas,
    }


def exibir_resumo(resultado: dict) -> None:
    print("\nRESUMO DA ANÁLISE")
    print(f"Logins com sucesso: {resultado['total_sucessos']}")
    print(f"Logins com falha: {resultado['total_falhas']}")
    print("\nFALHAS POR IP")
    for ip, quantidade in resultado["falhas_por_ip"].items():
        print(f"{ip}: {quantidade} falhas")

    print("\nANÁLISE POR TEMPO")
    for alerta in resultado["alertas"]:
        print(f"IP: {alerta['ip']}")
        print(
            f"ALERTA: {LIMITE_FALHAS} falhas em "
            f"{alerta['intervalo']} segundos"
        )


def main() -> None:
    caminho_log = Path(__file__).parent / "logs" / "exemplo.log"
    exibir_resumo(analisar_log(caminho_log))


if __name__ == "__main__":
    main()
