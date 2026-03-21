# 🚛 Yakult Logística Elite

> Dashboard interativo de logística para a rede de distribuição Yakult com cadeia de frio na América do Sul.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.54-red)
![Licença: MIT](https://img.shields.io/badge/licença-MIT-green)

---

## Visão Geral

**Yakult Logística Elite** é um dashboard de comando e controle baseado em Streamlit que
oferece planejamento de rotas em tempo real, análise de custos, estimativa de pegada
de CO₂ e monitoramento de integridade da cadeia de frio para a frota de distribuição
Yakult operando no Brasil, Argentina e Chile.

### Funcionalidades principais

| Funcionalidade | Descrição |
|----------------|-----------|
| **Planejamento de rotas** | Adicionar / remover paradas, geocodificar via Nominatim e calcular rotas rodoviárias ótimas pela API OSRM |
| **Análise de custos** | Breakdown diesel + pedágio por km, com tipo de veículo configurável (2 / 3 / 6 eixos) |
| **Previsão de ETA** | Horário de chegada por parada baseado em velocidade média ajustável (40 – 120 km/h) com exportação CSV |
| **Dashboard ESG** | Comparação lado a lado de CO₂ — Diesel vs Híbrido vs Elétrico |
| **Monitor de cadeia de frio** | Slider de temperatura com sistema de alerta em 3 níveis (estável / atenção / crítico) |
| **Mapa tático** | Mapa Folium em dark mode com sobreposição de rota GeoJSON e marcadores de caminhão |

---

## Pré-requisitos

- **Python 3.10+** (testado em 3.11 / 3.12)
- Ambiente virtual é recomendado

## Início rápido

```bash
# 1. Clone o repositório
git clone https://github.com/MauroSalles/Yakult-Logistics-Tower.git
cd Yakult-Logistics-Tower/Projeto\ Yakult

# 2. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate    # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o dashboard
streamlit run app_logistica.py
```

O dashboard abre automaticamente no navegador padrão.

---

## Estrutura do projeto

```
Projeto Yakult/
├── app_logistica.py          # Aplicação principal em Streamlit
├── config.py                 # Configuração centralizada (constantes, limiares, APIs)
├── tests/
│   └── test_app.py           # Suíte de testes Pytest (31 testes)
├── mapa_yakult.ipynb          # Notebook Jupyter exploratório
├── requirements.txt           # Dependências Python fixadas
├── pyproject.toml             # Metadados do projeto + configs de ferramentas (ruff, pytest)
├── Makefile                   # Atalhos para desenvolvedores (run, test, lint, format)
├── Relatorio_Logistica_Yakult.pdf  # Relatório final do projeto
└── LICENSE                    # MIT
```

## Configuração

Todos os parâmetros ajustáveis estão centralizados em [`config.py`](Projeto%20Yakult/config.py).
Cada constante pode ser sobrescrita via variáveis de ambiente — sem necessidade de alterar código:

```bash
export OSRM_BASE_URL="http://seu-osrm-instance:5000"
export CUSTO_DIESEL_POR_KM="2.50"
export TEMP_CRITICO="10"
streamlit run app_logistica.py
```

Veja a lista completa de valores configuráveis no cabeçalho do arquivo.

---

## Testes

```bash
# Executar a suíte completa
make test
# ou
python -m pytest

# Executar com saída detalhada
python -m pytest -v
```

A suíte cobre: `calcula_custos`, `formatar_tempo_conducao`, `calcular_eta_paradas`,
`calcular_co2`, `buscar_coords` e o módulo de configuração.

## Desenvolvimento

```bash
# Lint (somente leitura)
make lint

# Auto-formatação
make format

# Limpar caches
make clean
```

---

## Arquitetura

```
┌──────────────┐   HTTP/JSON   ┌───────────────────┐
│  Nominatim   │◄─────────────►│                   │
│ (geocodific.)│               │   app_logistica   │
└──────────────┘               │      .py          │
                               │                   │
┌──────────────┐   HTTP/JSON   │   ┌───────────┐   │   ┌────────────┐
│   API OSRM   │◄─────────────►│   │ config.py │   │──►│  Streamlit │
│   (rotas)    │               │   └───────────┘   │   │  Navegador │
└──────────────┘               └───────────────────┘   └────────────┘
```

## Licença

Este projeto está licenciado sob a [Licença MIT](Projeto%20Yakult/LICENSE).
