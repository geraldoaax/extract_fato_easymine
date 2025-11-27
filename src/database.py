import pyodbc
import pandas as pd
from typing import Any, Dict, List, Optional
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


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
            f"TrustServerCertificate={'yes' if self.trust_cert else 'no'}"
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

        Args:
            procedure_name: Nome da procedure a ser executada
            params: Lista de parâmetros para a procedure (opcional)

        Returns:
            DataFrame pandas com os resultados da procedure
        """
        if not procedure_name:
            raise ValueError("Nome da procedure é obrigatório")

        sql = f"EXEC {procedure_name}"

        # Adiciona placeholders para os parâmetros
        if params:
            param_placeholders = ", ".join(["?" for _ in params])
            sql += f" {param_placeholders}"

        try:
            with self.connection() as conn:
                if params:
                    df = pd.read_sql(sql, conn, params=params)
                else:
                    df = pd.read_sql(sql, conn)
                return df
        except pyodbc.Error as e:
            raise Exception(f"Erro ao executar procedure {procedure_name}: {e}")
        except Exception as e:
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