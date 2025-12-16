#!/usr/bin/env python3
"""
Identifica qual versão da procedure usar
"""

import logging
from src.database import DatabaseConnection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def check_procedure_versions():
    """Lista todas as versões da procedure"""
    db = DatabaseConnection()
    
    with db.connection() as conn:
        cursor = conn.cursor()
        
        # Lista todas as procedures com nome similar
        sql = """
        SELECT 
            s.name AS schema_name,
            p.name AS procedure_name,
            p.create_date,
            p.modify_date,
            p.object_id
        FROM sys.procedures p
        JOIN sys.schemas s ON p.schema_id = s.schema_id
        WHERE p.name LIKE '%prQDataCicloDetalhado%'
        ORDER BY s.name, p.name
        """
        
        cursor.execute(sql)
        procedures = cursor.fetchall()
        
        logger.info(f"\nProcedures encontradas: {len(procedures)}")
        logger.info("=" * 100)
        
        for proc in procedures:
            schema = proc[0]
            name = proc[1]
            created = proc[2]
            modified = proc[3]
            obj_id = proc[4]
            
            logger.info(f"\n{schema}.{name}")
            logger.info(f"  Criada: {created}, Modificada: {modified}, ID: {obj_id}")
            
            # Obtém os parâmetros
            cursor.execute("""
                SELECT 
                    parameter_id,
                    name,
                    TYPE_NAME(user_type_id) AS type_name,
                    max_length
                FROM sys.parameters
                WHERE object_id = ?
                ORDER BY parameter_id
            """, obj_id)
            
            params = cursor.fetchall()
            logger.info(f"  Parâmetros ({len(params)}):")
            for param in params:
                param_id = param[0]
                param_name = param[1]
                param_type = param[2]
                param_len = param[3]
                logger.info(f"    {param_id}. {param_name} ({param_type})")

if __name__ == "__main__":
    check_procedure_versions()
