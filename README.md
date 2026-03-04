# Yakult Elite Logistics

Projeto de visualização e análise logística para a cadeia de distribuição da Yakult. Inclui um dashboard interativo construído com **Streamlit**, mapeamento espacial com **Folium** e cálculo de rotas via **OSRM**.

## Arquivos principais

- `app_logistica.py`: aplicação principal em Streamlit. Exibe itinerário, métricas, mapa e simulações de ETA, custos e sustentabilidade.
- `mapa_yakult.ipynb`: notebook exploratório com exemplos de geocodificação, plotting e cálculos de custo.
- `Relatorio_Logistica_Yakult.pdf`: relatório final do projeto.

## Pré-requisitos

- Python 3.10+ (testado em 3.11)
- Virtualenv ou venv para isolar dependências

Instalação das dependências:

```bash
python -m venv env2             # cria ambiente
source env2/Scripts/activate     # Windows (PowerShell)
# ou `source env2/bin/activate` no Unix
pip install -r requirements.txt
```

## Uso

```bash
streamlit run app_logistica.py
```

### Versionamento

O dashboard abre no navegador padrão e permite:

- editar paradas do itinerário
- configurar veículo (modelo/eixos)
- visualizar custo, distância, ETA e emissões
- verificar integridade da cadeia fria (temperatura)

## Estrutura de projeto

```
Projeto_Yakult/
├── app_logistica.py
├── mapa_yakult.ipynb
├── Relatorio_Logistica_Yakult.pdf
├── requirements.txt
├── README.md
└── .gitignore
``` 

## Testes

Após instalar as dependências você pode validar a lógica com `pytest`:

```bash
pip install -r requirements.txt    # garante pytest instalado
pytest -q                         # executa a suíte mínima de testes
```

## Melhorias sugeridas

- adicionar tratamento de exceções e logging mais robusto
- modularizar código em funções e classes para facilitar testes
- criar testes automatizados (pytest)
- usar um `setup.py`/`pyproject.toml` se for transformar em pacote
- incluir autorização/configuração de chaves (TomTom) usando variáveis de ambiente

## Licença

Este projeto está licenciado sob a [MIT](LICENSE).
