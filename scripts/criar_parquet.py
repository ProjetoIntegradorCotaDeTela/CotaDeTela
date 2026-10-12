"""
Consolida os CSVs de bilheteria da ANCINE em um único arquivo Parquet.
"""

import sys
from pathlib import Path

import duckdb

from carrega_arquivos import carrega_arquivos, SEPARADOR, ENCODING

# --- Parâmetros padrão ---

PASTA_RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS = PASTA_RAIZ / "data"
NOME_PARQUET = "bilheteria.parquet"

# --- Tipagem explícita das colunas ---

COLUNAS = {
    "DATA_EXIBICAO": "DATE",
    "SESSAO": "TIMESTAMP",
    "TITULO_ORIGINAL": "VARCHAR",
    "TITULO_BRASIL": "VARCHAR",
    "CPB_ROE": "VARCHAR",
    "AUDIO": "VARCHAR",
    "LEGENDADA": "VARCHAR",
    "PAIS_OBRA": "VARCHAR",
    "REGISTRO_SALA": "BIGINT",
    "NOME_SALA": "VARCHAR",
    "PUBLICO": "BIGINT",
    "REGISTRO_GRUPO_EXIBIDOR": "BIGINT",
    "REGISTRO_EXIBIDOR": "BIGINT",
    "REGISTRO_COMPLEXO": "BIGINT",
    "MUNICIPIO_SALA_COMPLEXO": "VARCHAR",
    "UF_SALA_COMPLEXO": "VARCHAR",
    "RAZAO_SOCIAL_EXIBIDORA": "VARCHAR",
    "CNPJ_EXIBIDORA": "VARCHAR",
}


def _gerar_colunas_select():
    """Gera a lista de colunas com CAST para os tipos corretos."""
    partes = []
    for nome, tipo in COLUNAS.items():
        if tipo == "DATE":
            partes.append(f'strptime("{nome}", \'%d/%m/%Y\')::DATE AS "{nome}"')
        elif tipo == "TIMESTAMP":
            partes.append(f'strptime("{nome}", \'%d/%m/%Y %H:%M:%S\')::TIMESTAMP AS "{nome}"')
        elif tipo in ("BIGINT", "INTEGER"):
            partes.append(f'CAST("{nome}" AS {tipo}) AS "{nome}"')
        else:
            partes.append(f'"{nome}"')
    return ",\n            ".join(partes)


# --- Função principal ---

def cria_parquet(
    pasta_csv=None,
    arquivo_parquet=None,
    separador=SEPARADOR,
    encoding=ENCODING,
    memory_limit="4GB",
    threads=2,
    verbose=True,
):
    """
    Consolida todos os CSVs de uma pasta em um único arquivo Parquet.

    Parâmetros
    ----------
    pasta_csv : Path | str | None
        Pasta com os CSVs. Se None, usa a pasta padrão do projeto.
    arquivo_parquet : Path | str | None
        Caminho do Parquet de saída. Se None, usa data/bilheteria.parquet.
    separador : str
        Separador dos CSVs. Padrão: ";".
    encoding : str
        Encoding dos CSVs. Padrão: "utf-8".
    memory_limit : str
        Limite de memória do DuckDB. Padrão: "4GB".
    threads : int
        Número de threads. Padrão: 2.
    verbose : bool
        Se True, imprime progresso.

    Retorna
    -------
    Path
        Caminho do arquivo Parquet gerado.
    """
    # Localiza os arquivos
    arquivos = carrega_arquivos(pasta_csv=pasta_csv, verbose=verbose)

    # Define destino
    if arquivo_parquet is None:
        arquivo_parquet = PASTA_DADOS / NOME_PARQUET
    arquivo_parquet = Path(arquivo_parquet)
    arquivo_parquet.parent.mkdir(parents=True, exist_ok=True)

    # Remove Parquet anterior, se existir
    if arquivo_parquet.exists():
        if verbose:
            print(f"\nRemovendo Parquet anterior: {arquivo_parquet}")
        arquivo_parquet.unlink()

    # Pasta onde estão os CSVs
    pasta = Path(arquivos[0]).parent

    # Diretório de spill
    temp_dir = Path("/tmp/duckdb_temp")
    temp_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"\nConsolidando {len(arquivos)} arquivos em Parquet...")
        print(f"Memory limit: {memory_limit} | Threads: {threads}\n")

    # Conecta ao DuckDB
    con = duckdb.connect()
    con.execute(f"SET memory_limit = '{memory_limit}';")
    con.execute(f"SET threads = {threads};")
    con.execute("SET preserve_insertion_order = false;")
    con.execute(f"SET temp_directory = '{temp_dir}';")

    # Gera a lista de colunas com CAST
    colunas_select = _gerar_colunas_select()

    try:
        con.execute(f"""
            COPY (
                SELECT
                    {colunas_select},
                    regexp_extract(filename, '([^/]+)$', 1) AS arquivo_origem,
                    regexp_extract(filename, '(\\d{{4}})-(\\d{{2}})-s(\\d{{2}})', 1) AS ano,
                    regexp_extract(filename, '(\\d{{4}})-(\\d{{2}})-s(\\d{{2}})', 2) AS mes,
                    regexp_extract(filename, '(\\d{{4}})-(\\d{{2}})-s(\\d{{2}})', 3) AS semana
                FROM read_csv(
                    '{pasta}/*.csv',
                    delim='{separador}',
                    header=true,
                    union_by_name=true,
                    filename=true,
                    all_varchar=true
                )
            ) TO '{arquivo_parquet}' (FORMAT PARQUET, COMPRESSION SNAPPY)
        """)
    except Exception as e:
        con.close()
        raise RuntimeError(f"Falha ao consolidar: {e}")

    # Verificação
    total = con.sql(f"SELECT COUNT(*) FROM '{arquivo_parquet}'").fetchone()[0]

    if verbose:
        print(f"Total de linhas: {total:,}")

        print("\nLinhas por ano:")
        df_anos = con.sql(f"""
            SELECT ano, COUNT(*) AS linhas
            FROM '{arquivo_parquet}'
            GROUP BY ano
            ORDER BY ano
        """).df()
        print(df_anos.to_string(index=False))

        print("\nAmostra:")
        df_amostra = con.sql(f"""
            SELECT * FROM '{arquivo_parquet}' LIMIT 3
        """).df()
        print(df_amostra.to_string(index=False))

        print("\nSchema:")
        df_schema = con.sql(f"DESCRIBE SELECT * FROM '{arquivo_parquet}'").df()
        print(df_schema.to_string(index=False))

    con.close()

    # Resumo
    tamanho_mb = arquivo_parquet.stat().st_size / (1024 * 1024)

    if verbose:
        print(f"\nParquet salvo: {arquivo_parquet}")
        print(f"Tamanho:       {tamanho_mb:.2f} MB")

    return arquivo_parquet


# --- Execução direta ---

if __name__ == "__main__":
    try:
        arquivo = cria_parquet()
        print(f"\nConcluído: {arquivo}")

    except (FileNotFoundError, RuntimeError) as e:
        print(f"\nERRO: {e}")
        sys.exit(1)