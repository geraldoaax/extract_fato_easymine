# Extrator de Dados Fato - SQL Server

Uma aplicação Python para extrair dados de tabelas do schema `fato` no SQL Server, dividindo automaticamente o período em meses para não sobrecarregar o banco de dados, exportando cada resultado para arquivos Excel.

## Funcionamento

O sistema realiza **consultas SELECT diretas** nas tabelas do schema `fato`, aplicando filtros de data no formato:

```sql
SELECT * FROM fato.<tabela> WHERE <coluna_data> BETWEEN 'YYYYMMDD 00:00:00' AND 'YYYYMMDD 23:59:59'
```

**Não são executadas procedures (stored procedures)** - o sistema consulta as tabelas diretamente. As datas são automaticamente ajustadas para:
- **Data inicial**: `00:00:00` (início do dia)
- **Data final**: `23:59:59` (fim do dia)

## Estrutura do Projeto

```
extract_fato_easymine/
├── .env.example              # Exemplo de configuração de ambiente
├── config/procedures.yaml    # Configuração das tabelas/queries
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

- **Consulta direta em tabelas**: Executa SELECT nas tabelas do schema `fato` sem usar stored procedures
- **Divisão automática de períodos**: Divide automaticamente o período em intervalos mensais
- **Exportação para Excel**: Exporta os resultados de cada período para arquivos Excel separados
- **Configuração YAML**: Configuração flexível das tabelas através de arquivo YAML
- **CLI completa**: Interface de linha de comando com todas as opções necessárias
- **Horários padronizados**: Data inicial com `00:00:00` e data final com `23:59:59`
- **Coluna de data configurável**: Permite especificar qual coluna usar no filtro WHERE (padrão: `Data`)

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

### 2. Tabelas (config/procedures.yaml)

Configure as tabelas no arquivo `config/procedures.yaml`:

```yaml
procedures:
  - name: fato.prQDataCicloDetalhado
    output_folder: ciclo_detalhado
    table: fato.prQDataCicloDetalhado  # Tabela a ser consultada
    date_column: Data                   # Coluna de data para filtro (padrão: 'Data')
    params:                            # Mantido para compatibilidade
      - name: DataInicial
        type: datetime
        position: 1
      - name: DataFinal
        type: datetime
        position: 2

  - name: fato.prQDataApropriacoes
    output_folder: apropriacoes
    table: fato.prQDataApropriacoes
    date_column: DT1                    # Usando coluna DT1 para filtro
    params:
      - name: DT1
        type: datetime
        position: 1
      - name: DT2
        type: datetime
        position: 2
```

**Campos de configuração:**
- `name`: Identificador da configuração
- `output_folder`: Pasta onde os arquivos Excel serão salvos
- `table`: Nome da tabela a ser consultada (se omitido, usa o valor de `name`)
- `date_column`: Nome da coluna de data para o filtro WHERE (padrão: `Data`)
- `params`: Mantido para compatibilidade, mas não é mais usado para executar procedures

## Uso

### Comandos Básicos

Listar tabelas configuradas:
```bash
python main.py --list
```

Testar conexão com o banco:
```bash
python main.py --test
```

### Extrair Dados das Tabelas

Extrair dados de uma tabela:
```bash
python main.py -p fato.prQDataCicloDetalhado -s 20250101 -e 20251031
```

Extrair com período mais longo (será dividido em meses automaticamente):
```bash
python main.py -p fato.prQDataApropriacoes -s 20250101 -e 20251231
```

### Parâmetros da CLI

- `-p, --procedure`: Nome/identificador da tabela configurada (ex: `fato.prQDataCicloDetalhado`)
- `-s, --start`: Data inicial no formato YYYYMMDD (será ajustada para 00:00:00)
- `-e, --end`: Data final no formato YYYYMMDD (será ajustada para 23:59:59)
- `-P, --params`: Parâmetros adicionais (mantido para compatibilidade)
- `--list`: Lista todas as tabelas configuradas
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
$ python main.py -p fato.prQDataCicloDetalhado -s 20250101 -e 20250331

Executando extração de 'fato.prQDataCicloDetalhado' para 3 período(s) mensal(is)
Executando período 1/3: 01/01/2025 00:00:00 a 31/01/2025 23:59:59
  SELECT * FROM fato.prQDataCicloDetalhado WHERE Data BETWEEN '20250101 00:00:00' AND '20250131 23:59:59'
Arquivo gerado com sucesso: output/ciclo_detalhado/fato.prQDataCicloDetalhado_202501.xlsx
  1250 registros exportados
Executando período 2/3: 01/02/2025 00:00:00 a 28/02/2025 23:59:59
  SELECT * FROM fato.prQDataCicloDetalhado WHERE Data BETWEEN '20250201 00:00:00' AND '20250228 23:59:59'
Arquivo gerado com sucesso: output/ciclo_detalhado/fato.prQDataCicloDetalhado_202502.xlsx
  980 registros exportados
Executando período 3/3: 01/03/2025 00:00:00 a 31/03/2025 23:59:59
  SELECT * FROM fato.prQDataCicloDetalhado WHERE Data BETWEEN '20250301 00:00:00' AND '20250331 23:59:59'
Arquivo gerado com sucesso: output/ciclo_detalhado/fato.prQDataCicloDetalhado_202503.xlsx
  1430 registros exportados

Execução concluída. 3 arquivo(s) gerado(s)

Arquivos gerados:
  - output/ciclo_detalhado/fato.prQDataCicloDetalhado_202501.xlsx
  - output/ciclo_detalhado/fato.prQDataCicloDetalhado_202502.xlsx
  - output/ciclo_detalhado/fato.prQDataCicloDetalhado_202503.xlsx
```

## Tabelas Disponíveis

### 1. fato.prQDataCicloDetalhado

Tabela com dados detalhados de ciclos de equipamentos.

**Query executada:**
```sql
SELECT * FROM fato.prQDataCicloDetalhado 
WHERE Data BETWEEN '20250101 00:00:00' AND '20251130 23:59:59'
```

**Coluna de data:** `Data`

**Exemplo de uso:**
```bash
python main.py -p fato.prQDataCicloDetalhado -s 20250101 -e 20251130
```

**Saída:** `output/ciclo_detalhado/`

---

### 2. fato.prQDataCicloDetalhadoLatLon

Tabela com dados de ciclo detalhado incluindo coordenadas de latitude e longitude.

**Query executada:**
```sql
SELECT * FROM fato.prQDataCicloDetalhadoLatLon 
WHERE Data BETWEEN '20250101 00:00:00' AND '20251130 23:59:59'
```

**Coluna de data:** `Data`

**Exemplo de uso:**
```bash
python main.py -p fato.prQDataCicloDetalhadoLatLon -s 20250101 -e 20251130
```

**Saída:** `output/ciclo_detalhado_latlon/`

---

### 3. fato.prQDataApropriacoes

Tabela com dados de apropriações de equipamentos e atividades.

**Query executada:**
```sql
SELECT * FROM fato.prQDataApropriacoes 
WHERE Data BETWEEN '20250101 00:00:00' AND '20251130 23:59:59'
```

**Coluna de data:** `Data` (ou configure `DT1` no YAML se necessário)

**Exemplo de uso:**
```bash
python main.py -p fato.prQDataApropriacoes -s 20250101 -e 20251130
```

**Saída:** `output/apropriacoes/`

## Dependências

- `pyodbc`: Driver ODBC para SQL Server
- `python-dotenv`: Gerenciamento de variáveis de ambiente
- `pandas`: Manipulação de dados e leitura SQL
- `openpyxl`: Manipulação de arquivos Excel
- `pyyaml`: Leitura de arquivos YAML

## Notas

- **Não executa procedures**: O sistema faz SELECT direto nas tabelas `fato.*`
- **Divisão mensal**: Períodos longos são divididos automaticamente em intervalos mensais para evitar sobrecarga
- **Horários fixos**: Data inicial sempre em `00:00:00` e data final em `23:59:59`
- **Coluna de data configurável**: Use `date_column` no YAML para especificar a coluna de filtro
- **Validação de conexão**: A aplicação testa a conexão com o banco antes de extrair dados
- **Um arquivo por mês**: Cada período mensal gera um arquivo Excel separado