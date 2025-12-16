#!/usr/bin/env python3
"""
Testa a procedure dbo.prQDataCicloDetalhado com UsuarioID
"""

import logging
from datetime import datetime
from src.database import DatabaseConnection
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def test_dbo_procedure():
    """
    Testa a procedure dbo.prQDataCicloDetalhado com UsuarioID = 2115
    """
    db = DatabaseConnection()
    
    data_inicial = datetime(2024, 11, 1)
    data_final = datetime(2024, 11, 30, 23, 59, 59)
    usuario_id = 2115
    
    logger.info("=" * 80)
    logger.info("Testando dbo.prQDataCicloDetalhado com UsuarioID = 2115")
    logger.info("=" * 80)
    
    with db.connection() as conn:
        cursor = conn.cursor()
        
        sql = """
        EXEC dbo.prQDataCicloDetalhado 
            @dataInicial = ?,
            @dataFinal = ?,
            @UsuarioID = ?
        """
        
        logger.info(f"Data Inicial: {data_inicial.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Data Final: {data_final.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"UsuarioID: {usuario_id}")
        logger.info("\nExecutando...")
        
        try:
            cursor.execute(sql, data_inicial, data_final, usuario_id)
            
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                
                logger.info(f"\n{'='*80}")
                logger.info(f"✓✓✓ SUCESSO! {len(rows)} linhas retornadas ✓✓✓")
                logger.info(f"{'='*80}")
                logger.info(f"\nTotal de colunas: {len(columns)}")
                logger.info(f"Colunas: {', '.join(columns[:10])}...")
                
                if rows and len(rows) > 0:
                    logger.info(f"\nPrimeira linha (primeiros 5 campos):")
                    for i, (col, val) in enumerate(zip(columns[:5], rows[0][:5])):
                        logger.info(f"  {col}: {val}")
                    
                    # Salva um arquivo Excel de teste
                    df = pd.DataFrame.from_records(rows, columns=columns)
                    test_file = "output/teste_dbo_procedure.xlsx"
                    df.to_excel(test_file, index=False, engine='openpyxl')
                    logger.info(f"\n✓ Arquivo de teste salvo: {test_file}")
                    
                return True
            else:
                logger.warning("Nenhum result set retornado")
                return False
                
        except Exception as e:
            logger.error(f"Erro: {e}", exc_info=True)
            return False


if __name__ == "__main__":
    success = test_dbo_procedure()
    if success:
        logger.info("\n" + "="*80)
        logger.info("DIAGNÓSTICO: A procedure dbo.prQDataCicloDetalhado FUNCIONA!")
        logger.info("O problema é que o código está usando fato.prQDataCicloDetalhado")
        logger.info("que tem 19 parâmetros e não retorna dados.")
        logger.info("="*80)
