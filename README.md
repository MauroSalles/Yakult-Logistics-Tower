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

### Funcionalidades do dashboard

O dashboard abre no navegador padrão e permite:

- editar paradas do itinerário (com validação de entrada e botão ✕ por parada)
- configurar veículo (modelo/eixos)
- ajustar velocidade média de operação (slider 40–120 km/h)
- visualizar custo total com breakdown diesel/pedágio em tooltip
- tempo estimado de direção em horas e minutos
- mapa tático em dark mode com rota OSRM e marcadores por parada
- ETA por parada com status "Partida 🚀" / "No Prazo ✅" e exportação CSV
- gráfico de emissões CO2 (Diesel / Híbrido / Elétrico) com fórmula consistente
- monitoramento de cadeia de frio com alertas em 3 níveis (estável / atenção / crítico)
- contador de paradas no painel de métricas

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
pytest -q                         # executa a suíte de testes
```

A suíte cobre: `calcula_custos`, `formatar_tempo_conducao`, `calcular_eta_paradas`, `calcular_co2` e `buscar_coords`.

## Licença

Este projeto está licenciado sob a [MIT](LICENSE).
