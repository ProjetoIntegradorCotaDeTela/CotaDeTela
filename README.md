EXIBIÇÃO DE FILMES E COTA DE TELA
============================================================

Pipeline que baixa os dados de bilheteria diária da ANCINE,
consolida em Parquet e sobe um dashboard Streamlit.


ESTRUTURA
------------------------------------------------------------

    ├── main.py                       roda o pipeline e sobe o dashboard
    ├── requirements.txt
    ├── data/
    │   └── bilheteria.parquet        gerado pelo pipeline
    └── scripts/
        ├── baixa_arquivos.py         baixa e extrai o ZIP
        ├── carrega_arquivos.py       lista os CSVs
        ├── verifica_arquivos.py      confere o schema
        ├── criar_parquet.py          consolida em Parquet
        └── dashboard_basico.py       dashboard Streamlit


INSTALAÇÃO
------------------------------------------------------------

    pip install -r requirements.txt

Requer Python 3.10+ e conexão com a internet.


USO
------------------------------------------------------------

Pipeline completo:

    python main.py

Dashboard abre em http://localhost:8501

Etapas isoladas:

    python scripts/baixa_arquivos.py
    python scripts/carrega_arquivos.py
    python scripts/verifica_arquivos.py
    python scripts/criar_parquet.py
    streamlit run scripts/dashboard_basico.py


FONTE
------------------------------------------------------------

Dados abertos da ANCINE:

    https://dados.ancine.gov.br/dados-abertos/bilheteria-diaria-obras-por-exibidoras-csv.zip

O ZIP traz um CSV por semana com público e sessões por obra,
sala e exibidora.