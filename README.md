# 🔄 SQLite to Oracle Migration Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Oracle](https://img.shields.io/badge/Oracle-XE-red.svg)](https://www.oracle.com/database/technologies/xe-downloads.html)

Uma ferramenta robusta, resiliente e profissional para migração de dados de bancos SQLite para Oracle Database (XE), com interface de linha de comando, barra de progresso visual e logging detalhado.

---

## 📑 Índice

- [Visão Geral](#-visão-geral)
- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Funcionalidades Detalhadas](#-funcionalidades-detalhadas)
- [Mapeamento de Tipos](#-mapeamento-de-tipos)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Solução de Problemas](#-solução-de-problemas)
- [Arquitetura](#-arquitetura)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)
- [Contato](#-contato)

---

## 🎯 Visão Geral

Esta ferramenta foi desenvolvida para facilitar a migração de dados de bancos SQLite para Oracle Database, oferecendo uma solução completa e automatizada que lida com:

- ✅ Detecção automática de estrutura de tabelas
- ✅ Conversão inteligente de tipos de dados
- ✅ Normalização de nomes (espaços para underscores)
- ✅ Dois modos de operação (append/truncate)
- ✅ Inserções em lote para alta performance
- ✅ Barra de progresso visual em tempo real
- ✅ Logging detalhado de todas as operações
- ✅ Tratamento robusto de erros
- ✅ Multiplataforma (Windows, Linux, macOS)

---

## ✨ Características

### 🚀 Performance

- **Inserções em Lote (Batch Inserts)**: Processa milhares de registros por segundo
- **Tamanho de Lote Configurável**: Ajuste conforme memória disponível
- **Commit Otimizado**: Minimiza overhead de transações
- **Processamento Eficiente**: Usa cursores e generators para economia de memória

### 🛡️ Robustez

- **Tratamento Completo de Erros**: Captura e reporta todas as exceções
- **Validação de Configurações**: Verifica parâmetros antes da execução
- **Rollback Automático**: Em caso de falha, não deixa dados corrompidos
- **Interrupção Segura**: Suporta Ctrl+C sem corromper dados

### 📊 Visualização

- **Barra de Progresso Visual**: Mostra porcentagem e contadores em tempo real
- **Logging Detalhado**: Cada passo é documentado na tela
- **Estatísticas Finais**: Relatório completo ao final da migração
- **Velocidade de Processamento**: Exibe registros por segundo

### 🔧 Flexibilidade

- **Dois Modos de Operação**:
  - `append`: Adiciona dados às tabelas existentes
  - `truncate`: Recria tabelas do zero
- **Normalização Configurável**: Escolha preservar ou normalizar nomes
- **Configuração Externa**: Todas as opções em arquivo .cfg
- **Multiplataforma**: Funciona em qualquer OS com Python

---

## 📋 Requisitos

### Software Necessário

#### Python
- **Versão**: Python 3.6 ou superior
- **Download**: [python.org](https://www.python.org/downloads/)

#### Biblioteca cx_Oracle
```bash
pip install cx_Oracle
```

#### Oracle Instant Client

A biblioteca cx_Oracle requer o Oracle Instant Client instalado no sistema.

**Windows:**
1. Baixe em: [Oracle Instant Client Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)
2. Extraia em uma pasta (ex: `C:\oracle\instantclient_21_3`)
3. Adicione a pasta ao PATH do sistema:
   - Painel de Controle → Sistema → Configurações Avançadas → Variáveis de Ambiente
   - Edite "Path" e adicione o caminho do Instant Client

**Linux (Ubuntu/Debian):**
```bash
# Instalar dependências
sudo apt-get update
sudo apt-get install libaio1 wget unzip

# Baixar e instalar Instant Client
wget https://download.oracle.com/otn_software/linux/instantclient/219000/instantclient-basic-linux.x64-21.9.0.0.0dbru.zip
sudo mkdir -p /opt/oracle
sudo unzip instantclient-basic-linux.x64-21.9.0.0.0dbru.zip -d /opt/oracle

# Configurar biblioteca
sudo sh -c "echo /opt/oracle/instantclient_21_9 > /etc/ld.so.conf.d/oracle-instantclient.conf"
sudo ldconfig
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install libaio
wget https://download.oracle.com/otn_software/linux/instantclient/219000/instantclient-basic-linux.x64-21.9.0.0.0dbru.zip
sudo mkdir -p /opt/oracle
sudo unzip instantclient-basic-linux.x64-21.9.0.0.0dbru.zip -d /opt/oracle
sudo sh -c "echo /opt/oracle/instantclient_21_9 > /etc/ld.so.conf.d/oracle-instantclient.conf"
sudo ldconfig
```

**macOS:**
```bash
# Usando Homebrew
brew tap InstantClientTap/instantclient
brew install instantclient-basic
```

### Bancos de Dados

- **SQLite**: Qualquer versão (arquivo .db, .sqlite, .sqlite3)
- **Oracle**: Oracle Database 10g ou superior (testado com Oracle XE)

---

## 🚀 Instalação

### Método 1: Clone do Repositório

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/sqlite-oracle-migration.git
cd sqlite-oracle-migration

# Instale as dependências
pip install -r requirements.txt

# Crie o arquivo de configuração
python migration.py --create-config
```

### Método 2: Download Direto

1. Baixe os arquivos:
   - `migration.py`
   - `requirements.txt`

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Crie o arquivo de configuração:
```bash
python migration.py --create-config
```

### Arquivo requirements.txt

```txt
cx_Oracle>=8.3.0
```

---

## ⚙️ Configuração

### Criar Arquivo de Configuração

Execute o comando para gerar um arquivo `migration.cfg` de exemplo:

```bash
python migration.py --create-config
```

### Estrutura do Arquivo migration.cfg

```ini
[SQLITE]
# Caminho para o arquivo SQLite (relativo ou absoluto)
# Exemplos:
#   database = data.db
#   database = /caminho/completo/para/banco.db
#   database = C:\Users\Usuario\Documents\banco.sqlite
database = data.db

[ORACLE]
# Configurações de conexão Oracle XE
# 
# user: Nome do usuário Oracle (ex: system, hr, seu_schema)
user = system

# password: Senha do usuário Oracle
password = oracle

# host: Endereço do servidor Oracle
#   localhost - para conexão local
#   IP ou hostname - para conexão remota
host = localhost

# port: Porta do Oracle Listener (padrão: 1521)
port = 1521

# sid: Service Identifier do Oracle
#   XE - para Oracle Express Edition
#   ORCL - para Oracle Standard/Enterprise (padrão)
#   Consulte seu DBA para outros valores
sid = XE

[MIGRATION]
# Modo de migração:
#
#   'append' (Modo Incremental)
#   - Mantém dados existentes nas tabelas Oracle
#   - Adiciona novos dados do SQLite
#   - Não apaga tabelas
#   - Pode gerar duplicatas se executado múltiplas vezes
#   - Ideal para: cargas incrementais, atualização de dados
#
#   'truncate' (Modo Completo)
#   - Remove (DROP) tabelas existentes no Oracle
#   - Recria estrutura das tabelas
#   - Carrega todos os dados do SQLite
#   - Dados anteriores são perdidos
#   - Ideal para: migrações completas, refresh total
#
mode = truncate

# Normalizar nomes de tabelas e colunas:
#
#   true (Recomendado)
#   - Substitui espaços por underscores
#   - Converte para MAIÚSCULAS
#   - Exemplo: "Nome do Cliente" → "NOME_DO_CLIENTE"
#   - Compatível com padrões Oracle
#   - Evita problemas com identificadores delimitados
#
#   false (Preservar Original)
#   - Mantém nomes exatamente como no SQLite
#   - Requer aspas duplas em consultas: SELECT * FROM "Nome do Cliente"
#   - Pode causar problemas em ferramentas Oracle
#   - Use apenas se absolutamente necessário
#
normalize_names = true

# Tamanho do lote para inserções (batch size)
#
# Define quantos registros são inseridos por comando
# Valores maiores = mais rápido, mas usa mais memória
# Valores menores = mais lento, mas mais estável
#
# Recomendações:
#   - 500-1000: Servidores com pouca memória
#   - 1000-2000: Configuração padrão (equilibrado)
#   - 2000-5000: Servidores com muita memória
#   - 5000+: Apenas para grandes volumes e muita RAM
#
batch_size = 1000
```

### Parâmetros Detalhados

#### Seção [SQLITE]

| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| `database` | string | Caminho do arquivo SQLite | `data.db` ou `/path/to/db.sqlite` |

#### Seção [ORACLE]

| Parâmetro | Tipo | Descrição | Padrão | Exemplo |
|-----------|------|-----------|--------|---------|
| `user` | string | Usuário Oracle | - | `system`, `hr` |
| `password` | string | Senha do usuário | - | `oracle123` |
| `host` | string | Endereço do servidor | `localhost` | `192.168.1.100` |
| `port` | integer | Porta do listener | `1521` | `1521` |
| `sid` | string | Service Identifier | - | `XE`, `ORCL` |

#### Seção [MIGRATION]

| Parâmetro | Tipo | Valores | Descrição |
|-----------|------|---------|-----------|
| `mode` | string | `append`, `truncate` | Modo de operação |
| `normalize_names` | boolean | `true`, `false` | Normalização de nomes |
| `batch_size` | integer | 100-10000 | Tamanho do lote |

---

## 📖 Uso

### Execução Básica

```bash
python migration.py
```

### Flags de Linha de Comando

```bash
# Criar arquivo de configuração de exemplo
python migration.py --create-config

# Ajuda (futura implementação)
python migration.py --help
```

### Saída Esperada

```
================================================================================
SQLITE TO ORACLE MIGRATION TOOL
================================================================================

[1/7] Carregando configurações de 'migration.cfg'...

✓ Configurações carregadas com sucesso:
  • SQLite Database: data.db
  • Oracle User: system
  • Oracle Host: localhost
  • Oracle Port: 1521
  • Oracle SID: XE
  • Modo de migração: TRUNCATE
  • Normalizar nomes: SIM (espaços → underscores)
  • Tamanho do lote: 1000 registros

[2/7] Conectando ao SQLite...
✓ Conectado ao SQLite: data.db

[3/7] Conectando ao Oracle...
✓ Conectado ao Oracle: system@XE

[4/7] Analisando estrutura do SQLite...
✓ Encontradas 5 tabelas no SQLite

[5/7] Analisando tabelas...
  • clientes: 3 colunas, 1,250 registros
  • produtos: 5 colunas, 500 registros
  • vendas: 6 colunas, 10,000 registros
  • estoque: 4 colunas, 800 registros
  • fornecedores: 7 colunas, 150 registros

[6/7] Criando estruturas no Oracle...
  • clientes → CLIENTES... ✓
  • produtos → PRODUTOS... ✓
  • vendas → VENDAS... ✓
  • estoque → ESTOQUE... ✓
  • fornecedores → FORNECEDORES... ✓

[7/7] Migrando dados...

  [1/5] clientes → CLIENTES (1,250 registros)
    [██████████████████████████████████████████████████] 100.0% (1,250/1,250) ✓ Concluído

  [2/5] produtos → PRODUTOS (500 registros)
    [██████████████████████████████████████████████████] 100.0% (500/500) ✓ Concluído

  [3/5] vendas → VENDAS (10,000 registros)
    [██████████████████████████████████████████████████] 100.0% (10,000/10,000) ✓ Concluído

  [4/5] estoque → ESTOQUE (800 registros)
    [██████████████████████████████████████████████████] 100.0% (800/800) ✓ Concluído

  [5/5] fornecedores → FORNECEDORES (150 registros)
    [██████████████████████████████████████████████████] 100.0% (150/150) ✓ Concluído

================================================================================
MIGRAÇÃO CONCLUÍDA COM SUCESSO!
================================================================================
  • Tabelas migradas: 5
  • Total de registros: 12,700
  • Tempo decorrido: 8.45 segundos
  • Registros/segundo: 1,503
================================================================================
```

---

## 🔍 Funcionalidades Detalhadas

### 1. Detecção Automática de Estrutura

A ferramenta analisa automaticamente:
- Todas as tabelas do banco SQLite
- Estrutura de colunas (nome, tipo, nullable)
- Quantidade de registros por tabela
- Primary keys e constraints (reconhece, mas não migra)

### 2. Mapeamento de Tipos de Dados

Conversão inteligente de tipos SQLite para Oracle:

| SQLite | Oracle | Observações |
|--------|--------|-------------|
| `INTEGER` | `NUMBER` | Sem perda de precisão |
| `INT` | `NUMBER` | Sem perda de precisão |
| `REAL` | `NUMBER` | Ponto flutuante |
| `FLOAT` | `NUMBER` | Ponto flutuante |
| `DOUBLE` | `NUMBER` | Ponto flutuante |
| `TEXT` | `VARCHAR2(4000)` | Limite Oracle: 4000 bytes |
| `VARCHAR` | `VARCHAR2(4000)` | Ajustável se necessário |
| `CHAR` | `VARCHAR2(4000)` | Flexibilidade aumentada |
| `BLOB` | `BLOB` | Dados binários preservados |
| `DATE` | `DATE` | Formato data mantido |
| `DATETIME` | `TIMESTAMP` | Com hora, minuto, segundo |
| `TIMESTAMP` | `TIMESTAMP` | Alta precisão temporal |
| `BOOLEAN` | `NUMBER(1)` | 0 = false, 1 = true |
| `NUMERIC` | `NUMBER` | Decimal/numérico |

**Notas Importantes:**
- Tipos não reconhecidos são convertidos para `VARCHAR2(4000)`
- `TEXT` no SQLite pode ter >4000 caracteres → use `CLOB` manualmente se necessário
- `BLOB` preserva dados binários sem alteração

### 3. Normalização de Nomes

#### Quando `normalize_names = true`:

**Transformações aplicadas:**
1. Espaços → Underscores
2. Caracteres especiais → Removidos ou substituídos
3. Conversão para MAIÚSCULAS

**Exemplos:**
```
"Nome do Cliente"     → NOME_DO_CLIENTE
"Endereço - Completo" → ENDERECO_COMPLETO
"Data/Hora Cadastro"  → DATAHORA_CADASTRO
"Valor (R$)"          → VALOR_R
```

#### Quando `normalize_names = false`:

Nomes preservados exatamente como no SQLite, porém:
- Requer aspas duplas em todas as consultas SQL
- Sensível a maiúsculas/minúsculas
- Pode causar problemas em ferramentas Oracle

### 4. Modos de Operação

#### Modo `append`:
```
1. Verifica se tabela existe
2. Se existe: Mantém estrutura e dados
3. Insere novos dados do SQLite
4. CUIDADO: Pode gerar duplicatas!
```

**Casos de Uso:**
- Carga incremental diária
- Atualização de dados de logs
- Adicionar registros históricos

**⚠️ Atenção:**
- Não verifica duplicatas
- Não atualiza registros existentes
- Pode violar constraints (unique, primary key)

#### Modo `truncate`:
```
1. DROP TABLE (se existe)
2. CREATE TABLE com nova estrutura
3. Insere todos os dados do SQLite
4. Dados anteriores são PERDIDOS
```

**Casos de Uso:**
- Migração inicial
- Refresh completo dos dados
- Correção de estrutura de tabelas

**⚠️ Atenção:**
- APAGA TODOS OS DADOS anteriores
- Sempre faça backup antes!

### 5. Performance e Otimização

#### Inserções em Lote (Batch Inserts)

Ao invés de:
```sql
INSERT INTO tabela VALUES (1, 'a');
INSERT INTO tabela VALUES (2, 'b');
INSERT INTO tabela VALUES (3, 'c');
-- 1000 comandos SQL individuais
```

A ferramenta usa:
```sql
INSERT ALL
  INTO tabela VALUES (1, 'a')
  INTO tabela VALUES (2, 'b')
  INTO tabela VALUES (3, 'c')
  -- ... até 1000 registros
SELECT 1 FROM DUAL;
-- 1 comando SQL para 1000 registros
```

**Benefícios:**
- ⚡ 10-50x mais rápido que inserts individuais
- 📉 Reduz overhead de rede
- 💾 Menos operações de I/O no disco
- 🔒 Menos locks na tabela

#### Ajuste de `batch_size`

| Cenário | batch_size | Motivo |
|---------|------------|--------|
| Poucos dados (<10k registros) | 500-1000 | Não faz diferença significativa |
| Dados médios (10k-100k) | 1000-2000 | Balanceado |
| Grandes volumes (>100k) | 2000-5000 | Maximiza throughput |
| Memória limitada | 100-500 | Evita OutOfMemory |
| Servidor potente | 5000+ | Aproveita recursos |

### 6. Barra de Progresso

```
[██████████████████████████████░░░░░░░░░░░░░░░░░░░░] 60.5% (6,050/10,000)
```

**Componentes:**
- **Barra visual**: 50 caracteres de largura
- **Porcentagem**: Precisão de 1 casa decimal
- **Contador**: Registros processados / Total
- **Atualização**: Em tempo real (a cada lote)

### 7. Tratamento de Erros

A ferramenta captura e trata:

```python
✓ Arquivo de configuração não encontrado
✓ Parâmetros inválidos ou faltando
✓ SQLite database não existe
✓ Erro de conexão Oracle (credenciais, rede, listener)
✓ Tabela já existe (modo append)
✓ Permissões insuficientes
✓ Tipos de dados incompatíveis
✓ Violação de constraints
✓ Espaço insuficiente no tablespace
✓ Timeout de conexão
✓ Interrupção pelo usuário (Ctrl+C)
✓ Erros de memória (OutOfMemory)
```

**Comportamento em Erro:**
1. Exibe mensagem clara do erro
2. Faz rollback de transações incompletas
3. Fecha conexões adequadamente
4. Retorna exit code diferente de 0
5. Não deixa dados corrompidos

---

## 🗺️ Mapeamento de Tipos

### Conversão SQLite → Oracle

#### Tipos Numéricos

```sql
SQLite: INTEGER, INT
Oracle: NUMBER
Exemplo: 
  SQLite: id INTEGER PRIMARY KEY
  Oracle: ID NUMBER
```

```sql
SQLite: REAL, FLOAT, DOUBLE
Oracle: NUMBER
Exemplo:
  SQLite: preco REAL
  Oracle: PRECO NUMBER
```

#### Tipos Texto

```sql
SQLite: TEXT, VARCHAR, CHAR
Oracle: VARCHAR2(4000)
Exemplo:
  SQLite: nome TEXT
  Oracle: NOME VARCHAR2(4000)
```

**⚠️ Limitação:** VARCHAR2 no Oracle tem limite de 4000 bytes. Para textos maiores:
```sql
-- Solução manual após migração:
ALTER TABLE tabela MODIFY coluna CLOB;
```

#### Tipos Binários

```sql
SQLite: BLOB
Oracle: BLOB
Exemplo:
  SQLite: foto BLOB
  Oracle: FOTO BLOB
```

#### Tipos Temporais

```sql
SQLite: DATE
Oracle: DATE
Exemplo:
  SQLite: data_cadastro DATE
  Oracle: DATA_CADASTRO DATE
```

```sql
SQLite: DATETIME, TIMESTAMP
Oracle: TIMESTAMP
Exemplo:
  SQLite: ultima_atualizacao DATETIME
  Oracle: ULTIMA_ATUALIZACAO TIMESTAMP
```

#### Tipos Especiais

```sql
SQLite: BOOLEAN
Oracle: NUMBER(1)
Conversão: 0 = FALSE, 1 = TRUE
Exemplo:
  SQLite: ativo BOOLEAN
  Oracle: ATIVO NUMBER(1)
```

---

## 💡 Exemplos de Uso

### Exemplo 1: Migração Simples

**Cenário:** Migrar banco SQLite de clientes para Oracle

```bash
# 1. Criar configuração
python migration.py --create-config

# 2. Editar migration.cfg
# [SQLITE]
# database = clientes.db
# 
# [ORACLE]
# user = hr
# password = hr123
# sid = XE
#
# [MIGRATION]
# mode = truncate

# 3. Executar
python migration.py
```

### Exemplo 2: Carga Incremental

**Cenário:** Adicionar novos registros diariamente

```ini
[MIGRATION]
mode = append
batch_size = 2000
```

```bash
# Executar diariamente via cron/agendador
python migration.py
```

### Exemplo 3: Grande Volume de Dados

**Cenário:** Migrar 10 milhões de registros

```ini
[MIGRATION]
mode = truncate
batch_size = 5000  # Lotes maiores para performance
```

**Recomendações adicionais:**
```sql
-- Antes da migração (no Oracle):
ALTER TABLE sua_tabela NOLOGGING;
ALTER INDEX seus_indices UNUSABLE;

-- Depois da migração:
ALTER TABLE sua_tabela LOGGING;
ALTER INDEX seus_indices REBUILD;
```

### Exemplo 4: Múltiplos Ambientes

**Estrutura de arquivos:**
```
projeto/
├── migration.py
├── migration_dev.cfg
├── migration_test.cfg
└── migration_prod.cfg
```

**Execução:**
```bash
# Desenvolvimento
cp migration_dev.cfg migration.cfg
python migration.py

# Teste
cp migration_test.cfg migration.cfg
python migration.py

# Produção (com backup)
cp migration_prod.cfg migration.cfg
# Fazer backup do Oracle antes!
python migration.py
```

### Exemplo 5: Automação com Scripts

**Windows (PowerShell):**
```powershell
# migrate.ps1
$ErrorActionPreference = "Stop"

Write-Host "Iniciando migração..."
python migration.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migração concluída com sucesso!" -ForegroundColor Green
} else {
    Write-Host "Erro na migração!" -ForegroundColor Red
    exit 1
}
```

**Linux/macOS (Bash):**
```bash
#!/bin/bash
# migrate.sh

set -e

echo "Iniciando migração..."
python3 migration.py

if [ $? -eq 0 ]; then
    echo "Migração concluída com sucesso!"
    # Enviar notificação, email, etc.
else
    echo "Erro na migração!"
    exit 1
fi
```

---

## 🔧 Solução de Problemas

### Problema 1: cx_Oracle não encontrado

**Erro:**
```
ModuleNotFoundError: No module named 'cx_Oracle'
```

**Solução:**
```bash
pip install cx_Oracle
# ou
pip3 install cx_Oracle
```

### Problema 2: Oracle Instant Client não encontrado

**Erro:**
```
DPI-1047: Cannot locate a 64-bit Oracle Client library
```

**Solução Windows:**
1. Baixe Instant Client: https://www.oracle.com/database/technologies/instant-client/downloads.html
2. Extraia em `C:\oracle\instantclient_XX_X`
3. Adicione ao PATH:
   ```powershell
   $env:PATH += ";C:\oracle\instantclient_21_3"
   ```

**Solução Linux:**
```bash
# Verificar se está instalado
ls /opt/oracle/instantclient*

# Se não estiver, instalar:
sudo apt-get install libaio1
# Baixar e extrair conforme seção de instalação
sudo ldconfig
```

### Problema 3: Erro de Conexão Oracle

**Erro:**
```
ORA-12541: TNS:no listener
```

**Soluções:**
1. Verificar se Oracle está rodando:
   ```bash
   # Linux
   sudo systemctl status oracle-xe
   
   # Windows
   services.msc → Procurar OracleServiceXE
   ```

2. Verificar listener:
   ```bash
   lsnrctl status
   ```

3. Testar conectividade:
   ```bash
   telnet localhost 1521
   ```

4. Verificar configuração:
   ```ini
   [ORACLE]
   host = localhost  # Tente 127.0.0.1
   port = 1521       # Porta correta?
   sid = XE          # SID correto?
   ```

### Problema 4: Credenciais Inválidas

**Erro:**
```
ORA-01017: invalid username/password; logon denied
```

**Soluções:**
1. Verificar usuário e senha no `migration.cfg`
2. Testar login via SQL*Plus:
   ```bash
   sqlplus system/senha@localhost:1521/XE
   ```
3. Resetar senha (se necessário):
   ```sql
   ALTER USER system IDENTIFIED BY nova_senha;
   ```

### Problema 5: Permissões Insuficientes

**Erro:**
```
ORA-01031: insufficient privileges
```

**Solução:**
```sql
-- Conectar como SYSTEM ou DBA
GRANT CREATE TABLE TO seu_usuario;
GRANT CREATE SESSION TO seu_usuario;
GRANT UNLIMITED TABLESPACE TO seu_usuario;
```

### Problema 6: Tabela Já Existe (Modo Append)

**Erro:**
```
ORA-00955: name is already used by an existing object
```

**Soluções:**
1. Mudar para modo truncate:
   ```ini
   [MIGRATION]
   mode = truncate
   ```

2. Ou remover tabelas manualmente:
   ```sql
   DROP TABLE nome_tabela PURGE;
   ```

### Problema 7: VARCHAR2 Muito Pequeno

**Erro:**
```
ORA-12899: value too large for column
```

**Causa:** Dados no SQLite excedem 4000 bytes

**Solução:**
```sql
-- Após migração, converter para CLOB:
ALTER TABLE tabela MODIFY coluna CLOB;

-- Re-executar migração em modo append
```

### Problema 8: Espaço Insuficiente

**Erro:**
```
ORA-01653: unable to extend table
```

**Solução:**
```sql
-- Verificar espaço disponível
SELECT tablespace_name, 
       ROUND(SUM(bytes)/1024/1024, 2) AS size_mb
FROM dba_free_space
GROUP BY tablespace_name;

-- Adicionar datafile
ALTER TABLESPACE USERS 
ADD DATAFILE '/path/to/datafile.dbf' 
SIZE 1G AUTOEXTEND ON;
```

### Problema 9: Performance Lenta

**Sintomas:**
- Migração muito lenta
- Menos de 100 registros/segundo

**Soluções:**
1. Aumentar `batch_size`:
   ```ini
   [MIGRATION]
   batch_size = 5000
   ```

2. Desabilitar logs temporariamente:
   ```sql
   ALTER TABLE tabela NOLOGGING;
   ```

3. Desabilitar índices:
   ```sql
   ALTER INDEX idx_nome UNUSABLE;
   -- Migrar
   ALTER INDEX idx_nome REBUILD

   [Luiz Antonio Carlin]
   [luiz.carlin@gmail.com]
   [https://www.linkedin.com/in/luizcarlin/]
   [@lcarlin]
