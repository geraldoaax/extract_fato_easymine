#!/usr/bin/env python3
"""
Testa a procedure com UsuarioID = 2115
"""

import logging
from datetime import datetime
from src.database import DatabaseConnection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def test_with_usuario_id():
    """
    Testa passando UsuarioID = 2115
    """
    db = DatabaseConnection()
    
    # Testa com período recente
    data_inicial = datetime(2024, 11, 1)
    data_final = datetime(2024, 11, 30, 23, 59, 59)
    usuario_id = 2115
    
    logger.info("=" * 80)
    logger.info("Testando procedure com UsuarioID = 2115")
    logger.info("=" * 80)
    
    with db.connection() as conn:
        cursor = conn.cursor()
        
        # SQL com parâmetros nomeados (SEM UsuarioID)
        sql = """
        EXEC fato.prQDataCicloDetalhado 
            @dataInicial = ?,
            @dataFinal = ?,
            @equipamentoSetorID = '-1',
            @equipamentoClassificacaoID = '-1',
            @equipamentoID = '-1',
            @tipoAtividadeID = '-1',
            @especMaterialID = '-1',
            @materialID = '-1',
            @origemID = '-1',
            @destinoID = '-1',
            @dmtCheioInicial = '-1',
            @dmtCheioFinal = '-1',
            @proprietarioID = '-1',
            @turnoID = '-1',
            @turmaID = '-1',
            @equipamentoCargaID = '-1',
            @operadorID = '-1',
            @frotaTransporteID = '-1',
            @cicloID = ''
        """
        
        logger.info(f"Data Inicial: {data_inicial.strftime('%Y-%m-%d')}")
        logger.info(f"Data Final: {data_final.strftime('%Y-%m-%d')}")
        logger.info("Executando...")
        
        try:
            cursor.execute(sql, data_inicial, data_final)
            
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                logger.info(f"\n✓✓✓ SUCESSO! {len(rows)} linhas retornadas ✓✓✓")
                logger.info(f"Colunas ({len(columns)}): {columns[:5]}..." if len(columns) > 5 else f"Colunas: {columns}")
                
                if rows:
                    logger.info(f"\nPrimeira linha (amostra dos primeiros 5 campos):")
                    for i, (col, val) in enumerate(zip(columns[:5], rows[0][:5])):
                        logger.info(f"  {col}: {val}")
                    
                    # Mostra mais algumas estatísticas
                    logger.info(f"\nTotal de registros: {len(rows)}")
                    logger.info(f"Total de colunas: {len(columns)}")
            else:
                logger.warning("Nenhum result set retornado")
                
        except Exception as e:
            logger.error(f"Erro: {e}", exc_info=True)


if __name__ == "__main__":
    test_with_usuario_id()
