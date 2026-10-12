"""
Baixa e descompacta o arquivo CSV de bilheteria diária da ANCINE.
"""

import sys
import zipfile
import requests
from pathlib import Path


# --- Parâmetros padrão ---

URL_CSV = "https://dados.ancine.gov.br/dados-abertos/bilheteria-diaria-obras-por-exibidoras-csv.zip"

PASTA_RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS = PASTA_RAIZ / "data"
NOME_ZIP = "bilheteria-diaria-obras-por-exibidoras-csv.zip"
PASTA_EXTRACAO = PASTA_RAIZ / "bilheteria-diaria-obras-por-exibidoras-csv"


# --- Funções auxiliares ---

def formatar_tamanho(bytes_):
    """Converte bytes para formato legível (KB, MB, GB)."""
    for unidade in ["B", "KB", "MB", "GB"]:
        if bytes_ < 1024:
            return f"{bytes_:.2f} {unidade}"
        bytes_ /= 1024
    return f"{bytes_:.2f} TB"

def baixar_arquivo(url, destino, verbose=True):
    """
    Baixa um arquivo da URL para o destino, com barra de progresso.

    Parâmetros
    ----------
    url : str
        URL do arquivo a baixar.
    destino : Path
        Caminho onde salvar o arquivo.
    verbose : bool
        Se True, imprime progresso.

    Retorna
    -------
    Path
        Caminho do arquivo baixado.
    """
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"Baixando: {url}")
        print(f"Destino:  {destino}")

    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Falha ao baixar {url}: {e}")

    total = int(response.headers.get("content-length", 0))
    baixado = 0

    with open(destino, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                baixado += len(chunk)

                if verbose and total:
                    pct = (baixado / total) * 100
                    print(
                        f"\r  {pct:5.1f}%  ({formatar_tamanho(baixado)} / {formatar_tamanho(total)})",
                        end="",
                        flush=True,
                    )

    if verbose:
        print()  # quebra a linha da barra de progresso

    return destino


def extrair_zip(caminho_zip, pasta_destino, verbose=True):
    """
    Extrai um arquivo ZIP para a pasta de destino.

    Parâmetros
    ----------
    caminho_zip : Path
        Caminho do arquivo ZIP.
    pasta_destino : Path
        Pasta onde extrair os arquivos.
    verbose : bool
        Se True, imprime progresso.

    Retorna
    -------
    list[str]
        Lista de nomes dos arquivos extraídos.
    """
    caminho_zip = Path(caminho_zip)
    pasta_destino = Path(pasta_destino)
    pasta_destino.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"Extraindo: {caminho_zip}")
        print(f"Para:      {pasta_destino}\n")

    try:
        with zipfile.ZipFile(caminho_zip, "r") as z:
            arquivos = z.namelist()
            if verbose:
                print(f"Total de arquivos no ZIP: {len(arquivos)}")
            z.extractall(pasta_destino)
    except zipfile.BadZipFile:
        raise RuntimeError(f"{caminho_zip} não é um ZIP válido")

    if verbose:
        print(f"Extração concluída: {len(arquivos)} arquivos\n")

    return arquivos


# --- Função principal ---

def baixar_e_extrair(url=None, pasta_dados=None, pasta_extracao=None, verbose=True):
    """
    Baixa o ZIP e extrai os CSVs.

    Parâmetros
    ----------
    url : str | None
        URL do ZIP. Se None, usa a URL padrão da ANCINE.
    pasta_dados : Path | None
        Pasta onde salvar o ZIP. Se None, usa data/.
    pasta_extracao : Path | None
        Pasta onde extrair os CSVs. Se None, usa a pasta padrão.
    verbose : bool
        Se True, imprime progresso.

    Retorna
    -------
    tuple[Path, Path, list[str]]
        (caminho_zip, pasta_extracao, lista_de_arquivos)
    """
    url = url or URL_CSV
    pasta_dados = Path(pasta_dados) if pasta_dados else PASTA_DADOS
    pasta_extracao = Path(pasta_extracao) if pasta_extracao else PASTA_EXTRACAO

    caminho_zip = pasta_dados / NOME_ZIP

    # Baixa
    baixar_arquivo(url, caminho_zip, verbose=verbose)

    # Verifica tamanho mínimo
    tamanho = caminho_zip.stat().st_size
    if tamanho < 1000:
        raise RuntimeError(f"Arquivo suspeito ({tamanho} bytes): {caminho_zip}")

    if verbose:
        print(f"Arquivo salvo: {caminho_zip}")
        print(f"Tamanho:       {formatar_tamanho(tamanho)}\n")

    # Extrai
    arquivos = extrair_zip(caminho_zip, pasta_extracao, verbose=verbose)

    return caminho_zip, pasta_extracao, arquivos


# --- Execução direta ---

if __name__ == "__main__":
    try:
        caminho_zip, pasta, arquivos = baixar_e_extrair()
        print(f"Concluído — {len(arquivos)} arquivos em {pasta}")

    except (RuntimeError, requests.exceptions.RequestException) as e:
        print(f"\nERRO: {e}")
        sys.exit(1)