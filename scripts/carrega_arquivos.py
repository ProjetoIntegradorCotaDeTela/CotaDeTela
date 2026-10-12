"""
Módulo para carregar os arquivos CSV de bilheteria da ANCINE.
"""

from pathlib import Path

# Parâmetros

PASTA_RAIZ = Path(__file__).resolve().parent.parent
PASTA_CSV = PASTA_RAIZ / "bilheteria-diaria-obras-por-exibidoras-csv"
SEPARADOR = ";"
ENCODING = "utf-8"

# Função principal

def carrega_arquivos(pasta_csv=None, verbose=True):
    """
    Localiza todos os arquivos CSV em uma pasta.

    Parâmetros
    ----------
    pasta_csv : Path | str | None
        Pasta onde estão os CSVs. Se None, usa o padrão do projeto.
    verbose : bool
        Se True, imprime informações no terminal.

    Retorna
    -------
    list[Path]
        Lista ordenada de caminhos dos CSVs encontrados.

    Levanta
    ------
    FileNotFoundError
        Se a pasta não existir ou nenhum CSV for encontrado.
    """
    print("\nCarregamento de Arquivos CSV\n")

    if pasta_csv is None:
        pasta_csv = PASTA_CSV
    pasta_csv = Path(pasta_csv)

    # Verifica se a pasta existe
    if not pasta_csv.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {pasta_csv}")

    # Lista os arquivos
    arquivos = sorted(pasta_csv.glob("*.csv"))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {pasta_csv}")

    if verbose:
        print(f"Total de arquivos encontrados: {len(arquivos)}\n")
        print(f"Primeiro: {arquivos[0].name}")
        print(f"Último:   {arquivos[-1].name}")

    return arquivos

# Execução direta

if __name__ == "__main__":
    try:
        arquivos = carrega_arquivos()
        print(f"\n{len(arquivos)} arquivos prontos para uso")
    except FileNotFoundError as e:
        print(f"ERRO: {e}")