# SQL Procedure Executor

Uma aplicação Python para executar procedures do SQL Server dividindo automaticamente o período em meses para não sobrecarregar o banco de dados, exportando cada resultado para arquivos Excel.

## Estrutura do Projeto

```
sql_procedure_executor/
├── .env.example              # Exemplo de configuração de ambiente
├── config/procedures.yaml    # Configuração das procedures
├── src/
│   ├── __init__.py          # Inicialização do pacote
│   ├── database.py          # Conexão com banco de dados
│   ├── executor.py          # Executor principal
│   ├── date_utils.py        # Utilitários de data
│   └── exporter.py          # Exportação para Excel
├── main.py                  # Interface CLI
├── requirements.txt         # Dependências
└── README.md               # Documentação
```

## Funcionalidades

- **Divisão automática de períodos**: Divide automaticamente o período em intervalos mensais
- **Exportação para Excel**: Exporta os resultados de cada período para arquivos Excel separados
- **Configuração YAML**: Configuração flexível das procedures através de arquivo YAML
- **CLI completa**: Interface de linha de comando com todas as opções necessárias
- **Gerenciamento de parâmetros**: Suporte a parâmetros de diferentes tipos (datetime, int, string)
- **Valores padrão**: Suporte a valores padrão para parâmetros opcionais

## Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd sql_procedure_executor
```

2. Crie e ative um ambiente virtual (recomendado)

- Windows (cmd.exe / PowerShell):
```bash
python -m venv .venv
.venv\Scripts\activate
# Em PowerShell: .venv\Scripts\Activate.ps1 (pode precisar ajustar ExecutionPolicy)
```

- Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Estrutura típica do ambiente virtual criado:
```text
.venv/
├── pyvenv.cfg
├── Lib/            # Windows: pacotes e dependências (site-packages)
├── Scripts/        # Windows: activate, python.exe, pip.exe
└── bin/            # Linux/macOS: activate, python, pip
```

Para desativar o ambiente:
```bash
deactivate
```

> **⚠️ IMPORTANTE**: Certifique-se de que o ambiente virtual está ativado antes de instalar as dependências. Você deve ver `(.venv)` no início da linha de comando.

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o ambiente:
```bash
cp .env.example .env
# No Windows (cmd): copy .env.example .env
```

## Configuração

### 1. Variáveis de Ambiente (.env)

Configure as variáveis de ambiente no arquivo `.env`:

```env
# Database Configuration
DB_SERVER=seu_servidor
DB_DATABASE=sua_database
DB_USERNAME=seu_usuario
DB_DATABASE=sua_senha
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUST_CERT=yes
```

### 2. Procedures (config/procedures.yaml)

Configure as procedures no arquivo `config/procedures.yaml`:

```yaml
procedures:
  - name: fato.ciclodetalhado
    output_folder: ciclo_detalhado
    params:
      - name: data_inicial
        type: datetime
        position: 1
      - name: data_final
        type: datetime
        position: 2

  - name: fato.outra_procedure
    output_folder: outra_procedure
    params:
      - name: data_inicial
        type: datetime
        position: 1
      - name: data_final
        type: datetime
        position: 2
      - name: id_empresa
        type: int
        position: 3
        default: 1
```

## Uso

### Comandos Básicos

Listar procedures disponíveis:
```bash
python main.py --list
```

Testar conexão com o banco:
```bash
python main.py --test
```

### Executar Procedures

Executar procedure sem parâmetros adicionais:
```bash
python main.py -p fato.ciclodetalhado -s 20250101 -e 20251031
```

Executar procedure com parâmetros adicionais:
```bash
python main.py -p fato.outra_procedure -s 20250101 -e 20251031 -P id_empresa=5
```

Executar com múltiplos parâmetros adicionais:
```bash
python main.py -p fato.outra_procedure -s 20250101 -e 20251031 -P id_empresa=5 tipo=ANALISE
```

### Parâmetros da CLI

- `-p, --procedure`: Nome da procedure a ser executada
- `-s, --start`: Data inicial no formato YYYYMMDD
- `-e, --end`: Data final no formato YYYYMMDD
- `-P, --params`: Parâmetros adicionais no formato key=value (pode ser usado múltiplas vezes)
- `--list`: Lista todas as procedures configuradas
- `--test`: Testa a conexão com o banco de dados

## Saída

Os arquivos são gerados na pasta `output/` seguindo a estrutura:

```
output/
├── ciclo_detalhado/
│   ├── fato.ciclodetalhado_202501.xlsx
│   ├── fato.ciclodetalhado_202502.xlsx
│   └── ...
└── outra_procedure/
    ├── fato.outra_procedure_202501.xlsx
    ├── fato.outra_procedure_202502.xlsx
    └── ...
```

## Exemplo de Execução

```bash
$ python main.py -p fato.ciclodetalhado -s 20250101 -e 20250331

Executando procedure 'fato.ciclodetalhado' para 3 período(s) mensal(is)
Executando período 1/3: 01/01/2025 a 31/01/2025
Arquivo gerado com sucesso: output/ciclo_detalhado/fato.ciclodetalhado_202501.xlsx
  1250 registros exportados
Executando período 2/3: 01/02/2025 a 28/02/2025
Arquivo gerado com sucesso: output/ciclo_detalhado/fato.ciclodetalhado_202502.xlsx
  980 registros exportados
Executando período 3/3: 01/03/2025 a 31/03/2025
Arquivo gerado com sucesso: output/ciclo_detalhado/fato.ciclodetalhado_202503.xlsx
  1430 registros exportados

Execução concluída. 3 arquivo(s) gerado(s)

Arquivos gerados:
  - output/ciclo_detalhado/fato.ciclodetalhado_202501.xlsx
  - output/ciclo_detalhado/fato.ciclodetalhado_202502.xlsx
  - output/ciclo_detalhado/fato.ciclodetalhado_202503.xlsx
```

## Procedures Disponíveis

### 1. fato.prQDataCicloDetalhado

Extrai dados de ciclo detalhado.

**Parâmetros:**
- `@DataInicial` (datetime): Data inicial **[OBRIGATÓRIO]**
- `@DataFinal` (datetime): Data final **[OBRIGATÓRIO]**

**Exemplo de uso:**
```bash
python main.py -p fato.prQDataCicloDetalhado -s 20250101 -e 20251130
```

**Saída:** `output/ciclo_detalhado/`

---

### 2. fato.prQDataCicloDetalhadoLatLon

Extrai dados de ciclo detalhado com coordenadas de latitude e longitude.

**Parâmetros:**
- `@dataInicial` (datetime): Data inicial **[OBRIGATÓRIO]**
- `@dataFinal` (datetime): Data final **[OBRIGATÓRIO]**
- `@equipamentoSetorID` (nvarchar): ID do setor do equipamento (padrão: '-1')
- `@equipamentoClassificacaoID` (nvarchar): ID da classificação do equipamento (padrão: '-1')
- `@equipamentoID` (nvarchar): ID do equipamento (padrão: '-1')
- `@tipoAtividadeID` (nvarchar): ID do tipo de atividade (padrão: '-1')
- `@especMaterialID` (nvarchar): ID da especificação do material (padrão: '-1')
- `@materialID` (nvarchar): ID do material (padrão: '-1')
- `@origemID` (nvarchar): ID da origem (padrão: '-1')
- `@destinoID` (nvarchar): ID do destino (padrão: '-1')
- `@dmtCheioInicial` (int): DMT cheio inicial (padrão: -1)
- `@dmtCheioFinal` (int): DMT cheio final (padrão: -1)
- `@proprietarioID` (nvarchar): ID do proprietário (padrão: '-1')
- `@turnoID` (nvarchar): ID do turno (padrão: '-1')
- `@turmaID` (nvarchar): ID da turma (padrão: '-1')
- `@equipamentoCargaID` (nvarchar): ID do equipamento de carga (padrão: '-1')
- `@operadorID` (nvarchar): ID do operador (padrão: '-1')
- `@frotaTransporteID` (nvarchar): ID da frota de transporte (padrão: '-1')
- `@cicloID` (varchar): ID do ciclo (padrão: '-1')

**Exemplo de uso:**
```bash
python main.py -p fato.prQDataCicloDetalhadoLatLon -s 20250101 -e 20251130
```

**Exemplo com filtros:**
```bash
python main.py -p fato.prQDataCicloDetalhadoLatLon -s 20250101 -e 20251130 -P equipamentoID=5 -P turnoID=1
```

**Saída:** `output/ciclo_detalhado_latlon/`

---

### 3. fato.prQDataApropriacoes

Extrai dados de apropriações com múltiplos filtros.

**Parâmetros:**
- `@DT1` (datetime): Data inicial **[OBRIGATÓRIO]**
- `@DT2` (datetime): Data final **[OBRIGATÓRIO]**
- `@TPR` (varchar): Tipo de produção **[OBRIGATÓRIO]** (ex: 'PRODUCAO')
- `@CLASSIFICACAO` (nvarchar): Classificação (padrão: '-1')
- `@SETORID` (nvarchar): ID do setor (padrão: '-1')
- `@USUARIOID` (int): ID do usuário (padrão: 2115)
- `@proprietarioID` (nvarchar): ID do proprietário (padrão: '-1')
- `@turnoID` (nvarchar): ID do turno (padrão: '-1')
- `@turmaID` (nvarchar): ID da turma (padrão: '-1')
- `@operadorID` (nvarchar): ID do operador (padrão: '-1')
- `@frotaTransporteID` (nvarchar): ID da frota de transporte (padrão: '-1')
- `@equipamentoID` (nvarchar): ID do equipamento (padrão: '-1')

**Exemplo de uso (mínimo - apenas parâmetros obrigatórios):**
```bash
python main.py -p fato.prQDataApropriacoes -s 20250101 -e 20251130 -P TPR=PRODUCAO
```

**Exemplo de uso (com parâmetros personalizados):**
```bash
python main.py -p fato.prQDataApropriacoes -s 20250101 -e 20251130 \
  -P TPR=PRODUCAO \
  -P USUARIOID=2115 \
  -P SETORID=5
```

**Saída:** `output/apropriacoes/`

## Dependências

- `pyodbc`: Driver ODBC para SQL Server
- `python-dotenv`: Gerenciamento de variáveis de ambiente
- `pandas`: Manipulação de dados e leitura SQL
- `openpyxl`: Manipulação de arquivos Excel
- `pyyaml`: Leitura de arquivos YAML

## Notas

- A aplicação divide automaticamente o período em intervalos mensais para evitar sobrecarga
- Cada mês gera um arquivo Excel separado
- Parâmetros do tipo datetime são automaticamente identificados e substituídos pelos períodos mensais
- Parâmetros com valores padrão são automaticamente preenchidos se não fornecidos
- A aplicação valida a conexão com o banco antes de executar as procedures