#!/usr/bin/env python3
"""
Script de diagnóstico para verificar por que a procedure não retorna dados
"""

import logging
import sys
from datetime import datetime
from src.database import DatabaseConnection
from src.executor import ProcedureExecutor

# Configure logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def test_procedure_directly():
    """
    Testa a procedure diretamente sem o executor.
    """
    logger.info("=" * 80)
    logger.info("TESTE 1: Executando procedure diretamente via DatabaseConnection")
    logger.info("=" * 80)
    
    try:
        db = DatabaseConnection()
        
        # Testa a conexão primeiro
        logger.info("Testando conexão...")
        if not db.test_connection():
            logger.error("Falha na conexão com o banco de dados")
            return
        logger.info("✓ Conexão OK")
        
        # Define os parâmetros
        procedure_name = "fato.prQDataCicloDetalhado"
        data_inicial = datetime(2025, 1, 1)
        data_final = datetime(2025, 1, 31, 23, 59, 59)
        
        logger.info(f"\nExecutando: {procedure_name}")
        logger.info(f"Parâmetro 1 (DataInicial): {data_inicial}")
        logger.info(f"Parâmetro 2 (DataFinal): {data_final}")
        
        # Executa a procedure com diferentes formatos de parâmetro
        logger.info("\n--- Tentativa 1: Parâmetros como datetime ---")
        df1 = db.execute_procedure(procedure_name, [data_inicial, data_final])
        logger.info(f"Resultado: {len(df1)} linhas retornadas")
        if not df1.empty:
            logger.info(f"Colunas: {list(df1.columns)}")
            logger.info(f"Primeiras linhas:\n{df1.head()}")
        
        # Tentativa com strings formatadas
        logger.info("\n--- Tentativa 2: Parâmetros como strings YYYYMMDD ---")
        df2 = db.execute_procedure(
            procedure_name, 
            [data_inicial.strftime("%Y%m%d"), data_final.strftime("%Y%m%d")]
        )
        logger.info(f"Resultado: {len(df2)} linhas retornadas")
        if not df2.empty:
            logger.info(f"Colunas: {list(df2.columns)}")
            logger.info(f"Primeiras linhas:\n{df2.head()}")
        
        # Tentativa com strings formatadas diferentes
        logger.info("\n--- Tentativa 3: Parâmetros como strings YYYY-MM-DD ---")
        df3 = db.execute_procedure(
            procedure_name, 
            [data_inicial.strftime("%Y-%m-%d"), data_final.strftime("%Y-%m-%d")]
        )
        logger.info(f"Resultado: {len(df3)} linhas retornadas")
        if not df3.empty:
            logger.info(f"Colunas: {list(df3.columns)}")
            logger.info(f"Primeiras linhas:\n{df3.head()}")
        
        # Tentativa com parâmetros nomeados
        logger.info("\n--- Tentativa 4: Usando parâmetros nomeados ---")
        with db.connection() as conn:
            cursor = conn.cursor()
            sql_named = """
            EXEC fato.prQDataCicloDetalhado 
                @dataInicial = ?, 
                @dataFinal = ?
            """
            logger.info(f"SQL: {sql_named}")
            cursor.execute(sql_named, data_inicial, data_final)
            
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                logger.info(f"Resultado: {len(rows)} linhas retornadas")
                if rows:
                    logger.info(f"Colunas: {columns}")
            else:
                logger.info("Nenhum result set retornado")
            
    except Exception as e:
        logger.error(f"Erro no teste direto: {e}", exc_info=True)


def test_procedure_via_executor():
    """
    Testa a procedure através do ProcedureExecutor.
    """
    logger.info("\n" + "=" * 80)
    logger.info("TESTE 2: Executando procedure via ProcedureExecutor")
    logger.info("=" * 80)
    
    try:
        executor = ProcedureExecutor()
        
        procedure_name = "fato.prQDataCicloDetalhado"
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31, 23, 59, 59)
        
        logger.info(f"\nExecutando: {procedure_name}")
        logger.info(f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}")
        
        generated_files = executor.execute_procedure(
            procedure_name=procedure_name,
            start_date=start_date,
            end_date=end_date
        )
        
        logger.info(f"\nArquivos gerados: {len(generated_files)}")
        for file_path in generated_files:
            logger.info(f"  - {file_path}")
            
    except Exception as e:
        logger.error(f"Erro no teste via executor: {e}", exc_info=True)


def test_manual_sql():
    """
    Testa executando SQL manual para comparação.
    """
    logger.info("\n" + "=" * 80)
    logger.info("TESTE 3: Executando SQL SELECT manual para verificar dados")
    logger.info("=" * 80)
    
    try:
        db = DatabaseConnection()
        
        # Tenta uma query simples para verificar se há dados na tabela
        with db.connection() as conn:
            cursor = conn.cursor()
            
            # Verifica se a procedure existe
            logger.info("\n--- Verificando se a procedure existe ---")
            cursor.execute("""
                SELECT ROUTINE_NAME, ROUTINE_TYPE, CREATED, LAST_ALTERED
                FROM INFORMATION_SCHEMA.ROUTINES
                WHERE ROUTINE_NAME LIKE '%ciclo%'
                ORDER BY ROUTINE_NAME
            """)
            procedures = cursor.fetchall()
            logger.info(f"Procedures encontradas com 'ciclo' no nome: {len(procedures)}")
            for proc in procedures:
                logger.info(f"  - {proc[0]} ({proc[1]}) - Criada: {proc[2]}, Alterada: {proc[3]}")
            
            # Verifica parametros da procedure
            logger.info("\n--- Verificando parâmetros da procedure ---")
            cursor.execute("""
                SELECT 
                    PARAMETER_NAME,
                    DATA_TYPE,
                    PARAMETER_MODE,
                    ORDINAL_POSITION
                FROM INFORMATION_SCHEMA.PARAMETERS
                WHERE SPECIFIC_NAME = 'prQDataCicloDetalhado'
                ORDER BY ORDINAL_POSITION
            """)
            params = cursor.fetchall()
            logger.info(f"Parâmetros encontrados: {len(params)}")
            for param in params:
                logger.info(f"  - Posição {param[3]}: {param[0]} ({param[1]}) - Modo: {param[2]}")
                
    except Exception as e:
        logger.error(f"Erro no teste manual: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("Iniciando diagnóstico da procedure")
    logger.info("Data atual: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    # Executa os testes
    test_manual_sql()
    test_procedure_directly()
    test_procedure_via_executor()
    
    logger.info("\n" + "=" * 80)
    logger.info("Diagnóstico concluído")
    logger.info("=" * 80)
