# Yakult Elite Logistics

Projeto de visualização e análise logística para a cadeia de distribuição da Yakult. Inclui um dashboard interativo construído com **Streamlit**, mapeamento espacial com **Folium**, cálculo de rotas via **OSRM** e persistência de dados em **banco de dados PostgreSQL na nuvem**.

## Arquivos principais

- `app_logistica.py`: aplicação principal em Streamlit. Exibe itinerário, métricas, mapa e simulações de ETA, custos e sustentabilidade.
- `config.py`: configurações centralizadas (constantes de custo, emissão, limiares de temperatura, URL do banco, etc.).
- `database.py`: camada de persistência com SQLAlchemy — conecta a qualquer PostgreSQL na nuvem (Supabase, Neon, Railway, etc.).
- `mapa_yakult.ipynb`: notebook exploratório com exemplos de geocodificação, plotting e cálculos de custo.
- `Relatorio_Logistica_Yakult.pdf`: relatório final do projeto.

## Pré-requisitos

- Python 3.10+ (testado em 3.11)
- Virtualenv ou venv para isolar dependências
- (Opcional) Conta em um provedor de PostgreSQL na nuvem para ativar o histórico de rotas

Instalação das dependências:

```bash
python -m venv env2             # cria ambiente
source env2/Scripts/activate     # Windows (PowerShell)
# ou `source env2/bin/activate` no Unix
pip install -r requirements.txt
```

## Banco de Dados na Nuvem

O projeto suporta persistência de rotas em um banco de dados **PostgreSQL na nuvem**. Configure a variável de ambiente `DATABASE_URL` com a URL de conexão do seu provedor:

```bash
# Copie o arquivo de exemplo e edite com suas credenciais
cp .env.example .env
```

Provedores compatíveis (todos com plano gratuito):

| Provedor | Exemplo de URL |
|----------|---------------|
| **Supabase** | `postgresql://postgres.[ref]:[senha]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres` |
| **Neon** | `postgresql://user:senha@ep-xxx.sa-east-1.aws.neon.tech/neondb?sslmode=require` |
| **Railway** | `postgresql://postgres:senha@host.railway.app:5432/railway` |

Ao iniciar a aplicação com `DATABASE_URL` configurada, as tabelas são criadas automaticamente e o dashboard exibe a seção **Histórico de Rotas** para salvar e consultar rotas anteriores.

> Sem `DATABASE_URL` o dashboard funciona normalmente — apenas o histórico fica desativado.

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
- monitoramento de cadeia de frio com alertes em 3 níveis (estável / atenção / crítico)
- contador de paradas no painel de métricas
- **💾 salvar e consultar histórico de rotas no banco de dados na nuvem**

## Estrutura de projeto

```
Projeto_Yakult/
├── app_logistica.py       # dashboard Streamlit
├── config.py              # configurações centralizadas
├── database.py            # camada de persistência (SQLAlchemy)
├── .env.example           # modelo de variáveis de ambiente
├── mapa_yakult.ipynb
├── Relatorio_Logistica_Yakult.pdf
├── requirements.txt
└── tests/
    └── test_app.py
```

## Testes

Após instalar as dependências você pode validar a lógica com `pytest`:

```bash
pip install -r requirements.txt    # garante pytest instalado
pytest -q                         # executa a suíte de testes
```

A suíte cobre: `calcula_custos`, `formatar_tempo_conducao`, `calcular_eta_paradas`, `calcular_co2`, `buscar_coords`, constantes de `config.py` e operações CRUD do `database.py` (usando SQLite em memória nos testes).

## Licença

Este projeto está licenciado sob a [MIT](LICENSE).
