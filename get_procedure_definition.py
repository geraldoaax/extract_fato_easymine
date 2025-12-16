#!/usr/bin/env python3
"""
Verifica o código da procedure para entender por que não retorna dados
"""

import logging
from src.database import DatabaseConnection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def get_procedure_definition():
    """Obtém a definição da procedure"""
    db = DatabaseConnection()
    
    with db.connection() as conn:
        cursor = conn.cursor()
        
        # Tenta obter a definição da procedure
        sql = """
        SELECT 
            OBJECT_DEFINITION(OBJECT_ID('fato.prQDataCicloDetalhado'))
        """
        
        cursor.execute(sql)
        result = cursor.fetchone()
        
        if result and result[0]:
            proc_def = result[0]
            logger.info("Definição da procedure:")
            logger.info("=" * 80)
            
            # Mostra apenas as primeiras e últimas 50 linhas
            lines = proc_def.split('\n')
            logger.info(f"Total de linhas: {len(lines)}")
            logger.info("\nPrimeiras 30 linhas:")
            for i, line in enumerate(lines[:30], 1):
                print(f"{i:3}: {line}")
            
            logger.info("\n... (linhas intermediárias omitidas) ...\n")
            
            logger.info("Últimas 30 linhas:")
            start_line = len(lines) - 30
            for i, line in enumerate(lines[-30:], start_line + 1):
                print(f"{i:3}: {line}")
        else:
            logger.error("Não foi possível obter a definição da procedure")

if __name__ == "__main__":
    get_procedure_definition()
