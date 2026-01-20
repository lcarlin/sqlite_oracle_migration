#!/usr/bin/env python3
"""
#############################################################################################
# Author  : Carlin, Luiz A. .'.
# e-mail  : luiz.carlin@gmail.com
# Date    : 16-JAN-2026
# purpose : Import SQLite3 FULL Database into Oracle Database 
#           ET&L -> Extract, Transform & Loader
# Licence : MIT
#
# Copyright (c) 2026 Luiz Antonio Carlin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#############################################################################################
# Version control
# Date       #  Version #    What                                      #   Who
# 2026-01-16 #      1.0 # Merge With Version 6.1 and 7                 # Carlin, Luiz A. .'.

#############################################################################################
# Current Version : 1.0
#############################################################################################
# TODO:
#############################################################################################
Dependencies:
configparser==7.2.0
cx_Oracle==8.3.0

"""
import sqlite3
import configparser
import sys
import os
import re
import time
from datetime import datetime
from typing import List, Tuple, Dict, Any

try:
    import cx_Oracle
except ImportError:
    print("ERRO: Biblioteca cx_Oracle não encontrada.")
    print("Instale com: pip install cx_Oracle")
    sys.exit(1)


class MigrationTool:
    """Ferramenta de migração SQLite -> Oracle"""
    
    def __init__(self, config_file: str = "migration.cfg"):
        self.config_file = config_file
        self.config = None
        self.sqlite_conn = None
        self.oracle_conn = None
        self.mode = None
        self.batch_size = 1000
        self.normalize_names = True
        self.debug_mode = False
        
    def load_config(self) -> bool:
        """Carrega arquivo de configuração"""
        print("=" * 80)
        print("SQLITE TO ORACLE MIGRATION TOOL - v14")
        print("=" * 80)
        print(f"\n[1/7] Carregando configurações de '{self.config_file}'...")
        
        if not os.path.exists(self.config_file):
            print(f"ERRO: Arquivo de configuração '{self.config_file}' não encontrado!")
            return False
            
        self.config = configparser.ConfigParser()
        try:
            self.config.read(self.config_file, encoding='utf-8')
            
            # Validar seções obrigatórias
            required_sections = ['SQLITE', 'ORACLE', 'MIGRATION']
            for section in required_sections:
                if section not in self.config:
                    print(f"ERRO: Seção [{section}] não encontrada no arquivo de configuração!")
                    return False
            
            # Exibir configurações carregadas
            print("\n✓ Configurações carregadas com sucesso:")
            print(f"  • SQLite Database: {self.config['SQLITE']['database']}")
            print(f"  • Oracle User: {self.config['ORACLE']['user']}")
            print(f"  • Oracle Host: {self.config['ORACLE']['host']}")
            print(f"  • Oracle Port: {self.config['ORACLE']['port']}")
            
            # Exibir SID ou Service Name
            service_name = self.config['ORACLE'].get('service_name', None)
            sid = self.config['ORACLE'].get('sid', None)
            
            if service_name:
                print(f"  • Oracle Service Name: {service_name}")
            if sid:
                print(f"  • Oracle SID: {sid}")
            
            if not service_name and not sid:
                print("  ⚠ AVISO: Nenhum 'service_name' ou 'sid' configurado!")
                print("  Configure um deles na seção [ORACLE]")
            
            self.mode = self.config['MIGRATION'].get('mode', 'append').lower()
            self.batch_size = int(self.config['MIGRATION'].get('batch_size', '1000'))
            self.normalize_names = self.config['MIGRATION'].getboolean('normalize_names', True)
            self.debug_mode = self.config['MIGRATION'].getboolean('debug_mode', False)
            
            print(f"  • Modo de migração: {self.mode.upper()}")
            print(f"  • Normalizar nomes: {'SIM (espaços → underscores)' if self.normalize_names else 'NÃO'}")
            print(f"  • Tamanho do lote: {self.batch_size} registros")
            if self.debug_mode:
                print(f"  • Modo DEBUG: ATIVADO")
            
            return True
            
        except Exception as e:
            print(f"ERRO ao ler configuração: {str(e)}")
            return False
    
    def connect_sqlite(self) -> bool:
        """Conecta ao banco SQLite"""
        print(f"\n[2/7] Conectando ao SQLite...")
        try:
            db_path = self.config['SQLITE']['database']
            if not os.path.exists(db_path):
                print(f"ERRO: Database SQLite '{db_path}' não encontrado!")
                return False
                
            self.sqlite_conn = sqlite3.connect(db_path)
            print(f"✓ Conectado ao SQLite: {db_path}")
            return True
        except Exception as e:
            print(f"ERRO ao conectar SQLite: {str(e)}")
            return False
    
    def connect_oracle(self) -> bool:
        """Conecta ao banco Oracle (suporta SID e Service Name)"""
        print(f"\n[3/7] Conectando ao Oracle...")
        
        host = self.config['ORACLE']['host']
        port = self.config['ORACLE']['port']
        user = self.config['ORACLE']['user']
        password = self.config['ORACLE']['password']
        
        # Verificar se existe service_name ou sid no config
        service_name = self.config['ORACLE'].get('service_name', None)
        sid = self.config['ORACLE'].get('sid', None)
        
        # Validar que pelo menos um está configurado
        if not service_name and not sid:
            print("ERRO: Configure 'service_name' OU 'sid' na seção [ORACLE]")
            return False
        
        # Tentar conexão com Service Name (prioridade)
        if service_name:
            try:
                print(f"  • Tentando conexão com Service Name: {service_name}")
                dsn = cx_Oracle.makedsn(
                    host,
                    port,
                    service_name=service_name
                )
                
                self.oracle_conn = cx_Oracle.connect(
                    user=user,
                    password=password,
                    dsn=dsn,
                    encoding="UTF-8"
                )
                
                print(f"✓ Conectado ao Oracle: {user}@{service_name} (Service Name)")
                return True
                
            except cx_Oracle.DatabaseError as e:
                error_obj, = e.args
                print(f"  ✗ Falha com Service Name: {error_obj.message}")
                
                # Se SID também está configurado, tentar como fallback
                if sid:
                    print(f"  • Tentando fallback com SID: {sid}")
                else:
                    print(f"ERRO ao conectar Oracle: {error_obj.message}")
                    return False
        
        # Tentar conexão com SID
        if sid:
            try:
                if not service_name:  # Só exibe se não tentou service_name antes
                    print(f"  • Tentando conexão com SID: {sid}")
                
                dsn = cx_Oracle.makedsn(
                    host,
                    port,
                    sid=sid
                )
                
                self.oracle_conn = cx_Oracle.connect(
                    user=user,
                    password=password,
                    dsn=dsn,
                    encoding="UTF-8"
                )
                
                print(f"✓ Conectado ao Oracle: {user}@{sid} (SID)")
                return True
                
            except cx_Oracle.DatabaseError as e:
                error_obj, = e.args
                print(f"  ✗ Falha com SID: {error_obj.message}")
                print(f"\nERRO ao conectar Oracle: {error_obj.message}")
                return False
        
        return False
    
    def normalize_name(self, name: str) -> str:
        """Normaliza nome de tabela/coluna"""
        if self.normalize_names:
            return name.replace(' ', '_').upper()
        return name
    
    def get_sqlite_tables(self) -> List[str]:
        """Obtém lista de tabelas do SQLite"""
        print(f"\n[4/7] Analisando estrutura do SQLite...")
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✓ Encontradas {len(tables)} tabelas no SQLite")
        return tables
    
    def extract_column_type_from_ddl(self, ddl: str, column_name: str) -> str:
        """Extrai o tipo exato de uma coluna do DDL"""
        if not ddl:
            return None
        
        # Remover comentários e quebras de linha extras
        ddl_clean = re.sub(r'--.*$', '', ddl, flags=re.MULTILINE)
        ddl_clean = ' '.join(ddl_clean.split())
        
        # Pattern para encontrar a definição da coluna
        # Procura: nome_coluna TIPO(params) ou nome_coluna TIPO
        # Suporta espaços e variações de case
        pattern = rf'\b{re.escape(column_name)}\s+([A-Z][A-Z0-9_]*(?:\s*\([^)]+\))?)'
        
        match = re.search(pattern, ddl_clean, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def get_table_info(self, table_name: str) -> Tuple[List[Tuple], int]:
        """Obtém informações da tabela SQLite"""
        cursor = self.sqlite_conn.cursor()
        
        # Informações das colunas via PRAGMA (básico)
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        pragma_columns = cursor.fetchall()
        
        # Obter DDL real da tabela para tipos precisos
        cursor.execute(f"""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='{table_name}'
        """)
        ddl_result = cursor.fetchone()
        ddl = ddl_result[0] if ddl_result else None
        
        # Enriquecer informações com tipos do DDL
        enhanced_columns = []
        for col in pragma_columns:
            col_name = col[1]
            # Tentar extrair tipo real do DDL
            real_type = self.extract_column_type_from_ddl(ddl, col_name) if ddl else None
            
            # col é uma tupla: (cid, name, type, notnull, dflt_value, pk)
            # Substituir type (índice 2) pelo tipo real se encontrado
            if real_type:
                col_list = list(col)
                col_list[2] = real_type
                enhanced_columns.append(tuple(col_list))
            else:
                enhanced_columns.append(col)
        
        # Contagem de registros
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        count = cursor.fetchone()[0]
        
        return enhanced_columns, count
    
    def map_sqlite_to_oracle_type(self, sqlite_type: str) -> str:
        """Mapeia tipos SQLite para Oracle (preservando precisão e escala)"""
        if not sqlite_type:
            return 'VARCHAR2(4000)'
        
        sqlite_type_upper = sqlite_type.upper().strip()
        
        # Mapeamento direto para tipos já compatíveis com Oracle
        direct_map = {
            'DATE': 'DATE',
            'TIMESTAMP': 'TIMESTAMP',
            'BLOB': 'BLOB',
            'CLOB': 'CLOB',
            'RAW': 'RAW'
        }
        
        # Verificar mapeamento direto
        for key, value in direct_map.items():
            if sqlite_type_upper == key:
                return value
        
        # NUMBER com precisão e escala: NUMBER(9), NUMBER(11,2), etc.
        number_match = re.match(r'NUMBER\s*\(\s*(\d+)\s*(?:,\s*(\d+)\s*)?\)', sqlite_type_upper)
        if number_match:
            precision = number_match.group(1)
            scale = number_match.group(2)
            if scale:
                return f'NUMBER({precision},{scale})'
            else:
                return f'NUMBER({precision})'
        
        # NUMBER genérico
        if sqlite_type_upper == 'NUMBER' or sqlite_type_upper == 'NUMERIC':
            return 'NUMBER'
        
        # INTEGER e variações
        if sqlite_type_upper in ('INTEGER', 'INT', 'SMALLINT', 'BIGINT', 'TINYINT', 'MEDIUMINT'):
            return 'NUMBER'
        
        # REAL, FLOAT, DOUBLE
        if sqlite_type_upper in ('REAL', 'FLOAT', 'DOUBLE', 'DOUBLE PRECISION'):
            return 'NUMBER'
        
        # DECIMAL com precisão
        decimal_match = re.match(r'DECIMAL\s*\(\s*(\d+)\s*(?:,\s*(\d+)\s*)?\)', sqlite_type_upper)
        if decimal_match:
            precision = decimal_match.group(1)
            scale = decimal_match.group(2)
            if scale:
                return f'NUMBER({precision},{scale})'
            else:
                return f'NUMBER({precision})'
        
        # VARCHAR2 já definido no SQLite (Oracle syntax em SQLite)
        varchar2_match = re.match(r'VARCHAR2\s*\(\s*(\d+)\s*\)', sqlite_type_upper)
        if varchar2_match:
            size = varchar2_match.group(1)
            return f'VARCHAR2({size})'
        
        # VARCHAR com tamanho
        varchar_match = re.match(r'VARCHAR\s*\(\s*(\d+)\s*\)', sqlite_type_upper)
        if varchar_match:
            size = varchar_match.group(1)
            return f'VARCHAR2({size})'
        
        # CHAR com tamanho
        char_match = re.match(r'CHAR\s*\(\s*(\d+)\s*\)', sqlite_type_upper)
        if char_match:
            size = char_match.group(1)
            return f'CHAR({size})'
        
        # TEXT, VARCHAR genérico, STRING
        if sqlite_type_upper in ('TEXT', 'VARCHAR', 'STRING', 'NVARCHAR', 'NTEXT'):
            return 'VARCHAR2(4000)'
        
        # CHAR genérico
        if sqlite_type_upper == 'CHAR':
            return 'CHAR(1)'
        
        # BOOLEAN
        if sqlite_type_upper in ('BOOLEAN', 'BOOL'):
            return 'NUMBER(1)'
        
        # DATETIME
        if sqlite_type_upper == 'DATETIME':
            return 'TIMESTAMP'
        
        # Default: VARCHAR2(4000) para tipos não reconhecidos
        return 'VARCHAR2(4000)'
    
    def create_oracle_table(self, table_name: str, columns: List[Tuple]) -> bool:
        """Cria tabela no Oracle"""
        oracle_table_name = self.normalize_name(table_name)
        cursor = self.oracle_conn.cursor()
        
        try:
            # Se modo truncate, dropar tabela existente
            if self.mode == 'truncate':
                try:
                    cursor.execute(f"DROP TABLE {oracle_table_name} PURGE")
                    self.oracle_conn.commit()
                except cx_Oracle.DatabaseError:
                    pass  # Tabela não existe
            
            # Verificar se tabela já existe
            cursor.execute("""
                SELECT COUNT(*) FROM user_tables 
                WHERE table_name = :1
            """, (oracle_table_name,))
            
            exists = cursor.fetchone()[0] > 0
            
            if exists and self.mode == 'append':
                return True  # Tabela já existe, modo append
            
            # Criar tabela
            col_defs = []
            for col in columns:
                col_name = self.normalize_name(col[1])
                sqlite_type = col[2] if col[2] else 'TEXT'
                oracle_type = self.map_sqlite_to_oracle_type(sqlite_type)
                col_defs.append(f"{col_name} {oracle_type}")
                
                if self.debug_mode:
                    print(f"      {col_name}: {sqlite_type} → {oracle_type}")
            
            create_sql = f"CREATE TABLE {oracle_table_name} ({', '.join(col_defs)})"
            
            if self.debug_mode:
                print(f"      SQL: {create_sql}")
            
            cursor.execute(create_sql)
            self.oracle_conn.commit()
            
            return True
            
        except Exception as e:
            print(f"    ERRO ao criar tabela: {str(e)}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            return False
    
    def show_progress_bar(self, current: int, total: int, bar_length: int = 50):
        """Exibe barra de progresso"""
        percent = current / total if total > 0 else 0
        filled = int(bar_length * percent)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\r    [{bar}] {percent*100:.1f}% ({current:,}/{total:,})", end='', flush=True)
    
    def parse_date(self, date_str: str):
        """Converte string de data para objeto datetime Python"""
        if not date_str:
            return None
        
        # Formatos comuns de data no SQLite
        date_formats = [
            '%Y-%m-%d',              # 2024-01-15
            '%Y-%m-%d %H:%M:%S',     # 2024-01-15 14:30:00
            '%Y-%m-%d %H:%M:%S.%f',  # 2024-01-15 14:30:00.123
            '%d/%m/%Y',              # 15/01/2024
            '%d/%m/%Y %H:%M:%S',     # 15/01/2024 14:30:00
            '%Y/%m/%d',              # 2024/01/15
            '%Y/%m/%d %H:%M:%S',     # 2024/01/15 14:30:00
            '%d-%m-%Y',              # 15-01-2024
            '%d-%m-%Y %H:%M:%S',     # 15-01-2024 14:30:00
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except (ValueError, TypeError):
                continue
        
        # Se nenhum formato funcionar, retornar string original
        # Oracle tentará converter
        return date_str
    
    def migrate_table_data(self, table_name: str, column_types: List[str]) -> bool:
        """Migra dados de uma tabela"""
        oracle_table_name = self.normalize_name(table_name)
        
        try:
            # Obter estrutura e dados
            cursor_sqlite = self.sqlite_conn.cursor()
            cursor_sqlite.execute(f'SELECT * FROM "{table_name}"')
            
            # Obter nomes das colunas
            columns = [desc[0] for desc in cursor_sqlite.description]
            oracle_columns = [self.normalize_name(col) for col in columns]
            
            # Preparar statement de insert
            placeholders = ', '.join([f':{i+1}' for i in range(len(columns))])
            insert_sql = f"INSERT INTO {oracle_table_name} ({', '.join(oracle_columns)}) VALUES ({placeholders})"
            
            cursor_oracle = self.oracle_conn.cursor()
            
            # Contar registros
            cursor_count = self.sqlite_conn.cursor()
            cursor_count.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            total_rows = cursor_count.fetchone()[0]
            
            if total_rows == 0:
                print(f"    ⚠ Tabela vazia")
                return True
            
            # Migrar em lotes
            inserted = 0
            batch = []
            
            for row in cursor_sqlite:
                # Converter tipos especiais
                converted_row = []
                for idx, val in enumerate(row):
                    if val is None:
                        converted_row.append(None)
                    elif isinstance(val, bytes):
                        # BLOB - manter como está
                        converted_row.append(val)
                    elif column_types[idx].upper() in ('DATE', 'TIMESTAMP'):
                        # Converter strings de data para objetos datetime
                        if isinstance(val, str):
                            converted_row.append(self.parse_date(val))
                        else:
                            converted_row.append(val)
                    else:
                        converted_row.append(val)
                
                batch.append(converted_row)
                
                if len(batch) >= self.batch_size:
                    cursor_oracle.executemany(insert_sql, batch)
                    self.oracle_conn.commit()
                    inserted += len(batch)
                    self.show_progress_bar(inserted, total_rows)
                    batch = []
            
            # Inserir registros restantes
            if batch:
                cursor_oracle.executemany(insert_sql, batch)
                self.oracle_conn.commit()
                inserted += len(batch)
            
            self.show_progress_bar(total_rows, total_rows)
            print(f" ✓ Concluído")
            
            return True
            
        except Exception as e:
            print(f"\n    ERRO: {str(e)}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            return False
    
    def migrate(self) -> bool:
        """Executa migração completa"""
        start_time = time.time()
        
        # Obter tabelas
        tables = self.get_sqlite_tables()
        if not tables:
            print("Nenhuma tabela encontrada no SQLite!")
            return False
        
        print(f"\n[5/7] Analisando tabelas...")
        table_info = {}
        for table in tables:
            columns, count = self.get_table_info(table)
            table_info[table] = {'columns': columns, 'count': count}
            print(f"  • {table}: {len(columns)} colunas, {count:,} registros")
        
        # Criar estruturas no Oracle
        print(f"\n[6/7] Criando estruturas no Oracle...")
        for table in tables:
            oracle_name = self.normalize_name(table)
            print(f"  • {table} → {oracle_name}...", end='')
            if self.create_oracle_table(table, table_info[table]['columns']):
                print(" ✓")
            else:
                print(" ✗")
                return False
        
        # Migrar dados
        print(f"\n[7/7] Migrando dados...")
        total_migrated = 0
        
        for idx, table in enumerate(tables, 1):
            oracle_name = self.normalize_name(table)
            count = table_info[table]['count']
            
            # Extrair tipos Oracle das colunas para conversão
            oracle_types = []
            for col in table_info[table]['columns']:
                sqlite_type = col[2] if col[2] else 'TEXT'
                oracle_type = self.map_sqlite_to_oracle_type(sqlite_type)
                oracle_types.append(oracle_type)
            
            print(f"\n  [{idx}/{len(tables)}] {table} → {oracle_name} ({count:,} registros)")
            
            if self.migrate_table_data(table, oracle_types):
                total_migrated += count
            else:
                print(f"    ✗ Falha na migração")
        
        # Sumário final
        elapsed = time.time() - start_time
        print("\n" + "=" * 80)
        print("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        print(f"  • Tabelas migradas: {len(tables)}")
        print(f"  • Total de registros: {total_migrated:,}")
        print(f"  • Tempo decorrido: {elapsed:.2f} segundos")
        if elapsed > 0:
            print(f"  • Registros/segundo: {total_migrated/elapsed:,.0f}")
        print("=" * 80)
        
        return True
    
    def close_connections(self):
        """Fecha conexões"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        if self.oracle_conn:
            self.oracle_conn.close()
    
    def run(self):
        """Executa ferramenta completa"""
        try:
            if not self.load_config():
                return False
            
            if not self.connect_sqlite():
                return False
            
            if not self.connect_oracle():
                return False
            
            success = self.migrate()
            
            return success
            
        except KeyboardInterrupt:
            print("\n\nMigração interrompida pelo usuário!")
            return False
        except Exception as e:
            print(f"\n\nERRO FATAL: {str(e)}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            return False
        finally:
            self.close_connections()


def create_sample_config():
    """Cria arquivo de configuração de exemplo"""
    config_content = """[SQLITE]
# Caminho para o arquivo SQLite
database = data.db

[ORACLE]
# Configurações de conexão Oracle
user = system
password = oracle
host = localhost
port = 1521

# IMPORTANTE: Configure service_name OU sid (não ambos)
#
# Service Name (RECOMENDADO - mais moderno)
# Usado em Oracle Cloud, RAC, PDB (Pluggable Database)
# Exemplos: XEPDB1, orcl, myservice.example.com
service_name = XEPDB1

# SID (tradicional)
# Usado em Oracle XE antigo, instalações standalone
# Exemplos: XE, ORCL
# sid = XE

# Como descobrir qual usar:
# 1. SQL*Plus: SELECT value FROM v$parameter WHERE name = 'service_names';
# 2. Listener: lsnrctl status
# 3. tnsnames.ora: Procure SERVICE_NAME ou SID

[MIGRATION]
# Modo de migração: 'append' (adicionar) ou 'truncate' (recriar)
mode = truncate

# Normalizar nomes (substituir espaços por underscores)
normalize_names = true

# Tamanho do lote para inserções
batch_size = 1000

# Modo debug (exibe informações detalhadas de tipos e SQL)
# true = mostra mapeamento de tipos e comandos SQL
# false = modo normal (recomendado)
debug_mode = false
"""
    
    with open('migration.cfg', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("=" * 80)
    print("Arquivo 'migration.cfg' criado com sucesso!")
    print("=" * 80)
    print("\n⚠️  IMPORTANTE: Configure service_name OU sid")
    print("\nPara descobrir qual usar:")
    print("  1. Via SQL*Plus:")
    print("     SELECT value FROM v$parameter WHERE name = 'service_names';")
    print("\n  2. Via Listener:")
    print("     lsnrctl status")
    print("\n  3. Teste sua conexão:")
    print("     sqlplus usuario/senha@//localhost:1521/XEPDB1  (Service Name)")
    print("     sqlplus usuario/senha@localhost:1521:XE        (SID)")
    print("\nEdite o arquivo migration.cfg antes de executar a migração.")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--create-config':
        create_sample_config()
        sys.exit(0)
    
    tool = MigrationTool()
    success = tool.run()
    sys.exit(0 if success else 1)

## EOP => End Of Program 
