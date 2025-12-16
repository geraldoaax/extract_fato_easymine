import logging
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import pyodbc
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Classe para gerenciar conexão com banco de dados SQL Server.
    """

    def __init__(self):
        self.server = os.getenv("DB_SERVER")
        self.database = os.getenv("DB_DATABASE")
        self.username = os.getenv("DB_USERNAME")
        self.password = os.getenv("DB_PASSWORD")
        self.driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
        self.trust_cert = os.getenv("DB_TRUST_CERT", "yes").lower() == "yes"
        self.encrypt = os.getenv("DB_ENCRYPT", "no").lower()

        if not all([self.server, self.database, self.username, self.password]):
            raise ValueError(
                "Configurações de banco de dados incompletas. Verifique as variáveis de ambiente."
            )

    def _get_connection_string(self) -> str:
        """
        Monta a string de conexão com o banco de dados.

        Returns:
            String de conexão formatada
        """
        conn_str = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"TrustServerCertificate={'yes' if self.trust_cert else 'no'};"
            f"Encrypt={self.encrypt}"
        )
        return conn_str

    @contextmanager
    def connection(self):
        """
        Context manager para gerenciar a conexão com o banco de dados.

        Yields:
            Conexão ativa com o banco de dados
        """
        conn = None
        try:
            conn_str = self._get_connection_string()
            conn = pyodbc.connect(conn_str)
            yield conn
        except pyodbc.Error as e:
            raise Exception(f"Erro de conexão com o banco de dados: {e}")
        finally:
            if conn:
                conn.close()

    def execute_procedure(
        self, procedure_name: str, params: Optional[List[Any]] = None
    ) -> pd.DataFrame:
        """
        Executa uma procedure SQL Server e retorna os resultados como DataFrame.

        Esta implementação usa diretamente o cursor do pyodbc para executar a
        procedure e construir o DataFrame a partir do resultado. Evita problemas
        de compatibilidade com pandas.read_sql quando se usa uma conexão pyodbc.

        Adiciona logs para inspecionar o SQL executado e os parâmetros enviados.
        """
        if not procedure_name:
            raise ValueError("Nome da procedure é obrigatório")

        # Monta SQL com placeholders "?" quando há parâmetros
        sql = f"EXEC {procedure_name}"
        if params:
            placeholders = ", ".join("?" for _ in params)
            sql = f"{sql} {placeholders}"

        # Convert datetime params to SQL-friendly string format when needed,
        # because some stored procedures expect date/time as string literals.
        params_converted = None
        if params:
            params_converted = []
            for p in params:
                try:
                    if isinstance(p, datetime):
                        params_converted.append(p.strftime("%Y%m%d %H:%M:%S"))
                    else:
                        params_converted.append(p)
                except Exception:
                    params_converted.append(p)
        else:
            params_converted = params

        # Log SQL and converted parameters for debugging
        try:
            logger.info("Executing SQL: %s", sql)
            logger.info("With params: %s", params_converted)
        except Exception:
            pass

        try:
            with self.connection() as conn:
                cursor = conn.cursor()
                # Adiciona SET NOCOUNT ON para evitar mensagens de contagem de linhas
                cursor.execute("SET NOCOUNT ON")
                
                # Use parameterized execution
                try:
                    if params_converted:
                        cursor.execute(sql, params_converted)
                    else:
                        cursor.execute(sql)
                except Exception as e:
                    logger.info("Parameterized execute failed, will retry using interpolated literals: %s", e)
                    # If parameterized fails, retry with interpolated literals
                    if params_converted:
                        def _quote_literal(v):
                            if isinstance(v, datetime):
                                s = v.strftime("%Y%m%d")
                                return f"'{s}'"
                            if isinstance(v, str):
                                return "'" + v.replace("'", "''") + "'"
                            return str(v)

                        literals = ", ".join(_quote_literal(p) for p in params_converted)
                        sql_interpolated = f"EXEC {procedure_name} {literals}"
                        try:
                            logger.info("Retrying with interpolated SQL: %s", sql_interpolated)
                            cursor.execute(sql_interpolated)
                        except Exception as e2:
                            logger.info("Interpolated execute failed as well: %s", e2)
                            # Nothing more to try
                            return pd.DataFrame()
                    else:
                        return pd.DataFrame()

                # Tenta obter descrição das colunas; se None => nenhum resultado
                description = cursor.description
                if not description:
                    logger.info("No result set returned by procedure %s for params %s", procedure_name, params_converted)
                    return pd.DataFrame()

                columns = [col[0] for col in description]
                rows = cursor.fetchall()

                try:
                    logger.info("Rows fetched: %d", len(rows))
                except Exception:
                    pass

                # Constrói DataFrame a partir dos registros
                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
        except pyodbc.Error as e:
            logger.error("pyodbc error executing %s with params %s: %s", procedure_name, params_converted, e)
            raise Exception(f"Erro ao executar procedure {procedure_name}: {e}")
        except Exception as e:
            logger.error("General error executing %s with params %s: %s", procedure_name, params_converted, e)
            raise Exception(f"Erro geral ao executar procedure {procedure_name}: {e}")

    def test_connection(self) -> bool:
        """
        Testa a conexão com o banco de dados.

        Returns:
            True se a conexão for bem-sucedida, False caso contrário
        """
        try:
            with self.connection() as conn:
                # Executa uma consulta simples para testar
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                return True
        except:
            return False

    def execute_select(self, table_name: str, start_dt: datetime, end_dt: datetime, date_column: str = "Data") -> pd.DataFrame:
        """
        Executa um SELECT simples na tabela informada filtrando entre duas datas.

        Args:
            table_name: Nome da tabela (pode ser schema.tabela)
            start_dt: Data/hora inicial
            end_dt: Data/hora final
            date_column: Nome da coluna de data a ser usada no WHERE

        Returns:
            DataFrame com os resultados
        """
        if not table_name:
            raise ValueError("Nome da tabela é obrigatório para SELECT")

        sql = f"SELECT * FROM {table_name} WHERE {date_column} BETWEEN ? AND ?"

        # Converte datetimes para formato aceito pelo banco
        params_converted = []
        for p in (start_dt, end_dt):
            if isinstance(p, datetime):
                params_converted.append(p.strftime("%Y%m%d %H:%M:%S"))
            else:
                params_converted.append(p)

        try:
            logger.info("Executing SELECT: %s", sql)
            logger.info("With params: %s", params_converted)
        except Exception:
            pass

        try:
            with self.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SET NOCOUNT ON")
                try:
                    cursor.execute(sql, params_converted)
                except Exception as e:
                    logger.info("Parameterized SELECT failed, retrying with interpolated literals: %s", e)
                    def _quote_literal(v):
                        if isinstance(v, datetime):
                            s = v.strftime("%Y%m%d %H:%M:%S")
                            return f"'{s}'"
                        if isinstance(v, str):
                            return "'" + v.replace("'", "''") + "'"
                        return str(v)

                    literals = ", ".join(_quote_literal(p) for p in params_converted)
                    sql_interpolated = f"SELECT * FROM {table_name} WHERE {date_column} BETWEEN {literals.split(',')[0]} AND {literals.split(',')[1]}"
                    logger.info("Retrying with interpolated SQL: %s", sql_interpolated)
                    cursor.execute(sql_interpolated)

                description = cursor.description
                if not description:
                    logger.info("No result set returned by SELECT %s", table_name)
                    return pd.DataFrame()

                columns = [col[0] for col in description]
                rows = cursor.fetchall()
                try:
                    logger.info("Rows fetched: %d", len(rows))
                except Exception:
                    pass

                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
        except pyodbc.Error as e:
            logger.error("pyodbc error executing SELECT %s with params %s: %s", table_name, params_converted, e)
            raise Exception(f"Erro ao executar SELECT {table_name}: {e}")
        except Exception as e:
            logger.error("General error executing SELECT %s with params %s: %s", table_name, params_converted, e)
            raise Exception(f"Erro geral ao executar SELECT {table_name}: {e}")