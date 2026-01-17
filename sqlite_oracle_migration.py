#!/usr/bin/env python3
"""
SQLite to Oracle Migration Tool
Migrates data from SQLite database to Oracle Database (XE)
"""

import sqlite3
import configparser
import sys
import os
from datetime import datetime
from typing import List, Tuple, Dict, Any
import time

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
        
    def load_config(self) -> bool:
        """Carrega arquivo de configuração"""
        print("=" * 80)
        print("SQLITE TO ORACLE MIGRATION TOOL")
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
            print(f"  • Oracle SID: {self.config['ORACLE']['sid']}")
            
            self.mode = self.config['MIGRATION'].get('mode', 'append').lower()
            self.batch_size = int(self.config['MIGRATION'].get('batch_size', '1000'))
            self.normalize_names = self.config['MIGRATION'].getboolean('normalize_names', True)
            
            print(f"  • Modo de migração: {self.mode.upper()}")
            print(f"  • Normalizar nomes: {'SIM (espaços → underscores)' if self.normalize_names else 'NÃO'}")
            print(f"  • Tamanho do lote: {self.batch_size} registros")
            
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
        """Conecta ao banco Oracle"""
        print(f"\n[3/7] Conectando ao Oracle...")
        try:
            dsn = cx_Oracle.makedsn(
                self.config['ORACLE']['host'],
                self.config['ORACLE']['port'],
                sid=self.config['ORACLE']['sid']
            )
            
            self.oracle_conn = cx_Oracle.connect(
                user=self.config['ORACLE']['user'],
                password=self.config['ORACLE']['password'],
                dsn=dsn,
                encoding="UTF-8"
            )
            
            print(f"✓ Conectado ao Oracle: {self.config['ORACLE']['user']}@{self.config['ORACLE']['sid']}")
            return True
        except Exception as e:
            print(f"ERRO ao conectar Oracle: {str(e)}")
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
    
    def get_table_info(self, table_name: str) -> Tuple[List[Tuple], int]:
        """Obtém informações da tabela SQLite"""
        cursor = self.sqlite_conn.cursor()
        
        # Informações das colunas
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = cursor.fetchall()
        
        # Contagem de registros
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        count = cursor.fetchone()[0]
        
        return columns, count
    
    def map_sqlite_to_oracle_type(self, sqlite_type: str) -> str:
        """Mapeia tipos SQLite para Oracle"""
        sqlite_type = sqlite_type.upper()
        
        type_map = {
            'INTEGER': 'NUMBER',
            'INT': 'NUMBER',
            'REAL': 'NUMBER',
            'FLOAT': 'NUMBER',
            'DOUBLE': 'NUMBER',
            'TEXT': 'VARCHAR2(4000)',
            'VARCHAR': 'VARCHAR2(4000)',
            'CHAR': 'VARCHAR2(4000)',
            'BLOB': 'BLOB',
            'DATE': 'DATE',
            'DATETIME': 'TIMESTAMP',
            'TIMESTAMP': 'TIMESTAMP',
            'BOOLEAN': 'NUMBER(1)',
            'NUMERIC': 'NUMBER'
        }
        
        for key, value in type_map.items():
            if key in sqlite_type:
                return value
        
        return 'VARCHAR2(4000)'  # Default
    
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
                col_type = self.map_sqlite_to_oracle_type(col[2] if col[2] else 'TEXT')
                nullable = "" if col[3] == 0 else ""  # Oracle permite NULL por padrão
                col_defs.append(f"{col_name} {col_type}")
            
            create_sql = f"CREATE TABLE {oracle_table_name} ({', '.join(col_defs)})"
            cursor.execute(create_sql)
            self.oracle_conn.commit()
            
            return True
            
        except Exception as e:
            print(f"    ERRO ao criar tabela: {str(e)}")
            return False
    
    def show_progress_bar(self, current: int, total: int, bar_length: int = 50):
        """Exibe barra de progresso"""
        percent = current / total if total > 0 else 0
        filled = int(bar_length * percent)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\r    [{bar}] {percent*100:.1f}% ({current:,}/{total:,})", end='', flush=True)
    
    def migrate_table_data(self, table_name: str) -> bool:
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
                for val in row:
                    if isinstance(val, bytes):
                        converted_row.append(val)
                    elif val is None:
                        converted_row.append(None)
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
            
            print(f"\n  [{idx}/{len(tables)}] {table} → {oracle_name} ({count:,} registros)")
            
            if self.migrate_table_data(table):
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
sid = XE

[MIGRATION]
# Modo de migração: 'append' (adicionar) ou 'truncate' (recriar)
mode = truncate

# Normalizar nomes (substituir espaços por underscores)
normalize_names = true

# Tamanho do lote para inserções
batch_size = 1000
"""
    
    with open('migration.cfg', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("Arquivo de configuração 'migration.cfg' criado com sucesso!")
    print("Edite o arquivo antes de executar a migração.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--create-config':
        create_sample_config()
        sys.exit(0)
    
    tool = MigrationTool()
    success = tool.run()
    sys.exit(0 if success else 1)