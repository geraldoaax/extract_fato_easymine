#!/usr/bin/env python3
"""
Testa a procedure com todos os parâmetros (NULL para os opcionais)
"""

import logging
from datetime import datetime
from src.database import DatabaseConnection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def test_with_all_params():
    """
    Testa passando todos os 19 parâmetros, com NULL para os opcionais.
    """
    db = DatabaseConnection()
    
    # Testa com período antigo (provavelmente tem dados)
    data_inicial = datetime(2024, 11, 1)
    data_final = datetime(2024, 11, 30, 23, 59, 59)
    
    logger.info("Testando com TODOS os parâmetros (-1 para opcionais)")
    
    with db.connection() as conn:
        cursor = conn.cursor()
        
        # SQL com parâmetros nomeados e valores -1 para opcionais
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
            @cicloID = '-1'
        """
        
        logger.info(f"Data Inicial: {data_inicial.strftime('%Y-%m-%d')}")
        logger.info(f"Data Final: {data_final.strftime('%Y-%m-%d')}")
        logger.info("Executando com -1 para todos os parâmetros opcionais...")
        
        try:
            cursor.execute(sql, data_inicial, data_final)
            
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                logger.info(f"✓ Sucesso! {len(rows)} linhas retornadas")
                logger.info(f"Colunas: {columns[:5]}..." if len(columns) > 5 else f"Colunas: {columns}")
                
                if rows:
                    logger.info(f"Primeira linha (sample): {rows[0][:3]}...")
            else:
                logger.warning("Nenhum result set retornado")
                
        except Exception as e:
            logger.error(f"Erro: {e}")


def test_check_defaults():
    """
    Verifica os valores DEFAULT dos parâmetros na definição da procedure
    """
    db = DatabaseConnection()
    
    logger.info("\n" + "="*80)
    logger.info("Verificando valores DEFAULT dos parâmetros")
    logger.info("="*80)
    
    with db.connection() as conn:
        cursor = conn.cursor()
        
        # Query para obter defaults
        sql_defaults = """
        SELECT 
            p.PARAMETER_NAME,
            p.DATA_TYPE,
            p.ORDINAL_POSITION,
            p.PARAMETER_MODE
        FROM INFORMATION_SCHEMA.PARAMETERS p
        WHERE p.SPECIFIC_SCHEMA = 'fato'
            AND p.SPECIFIC_NAME = 'prQDataCicloDetalhado'
        ORDER BY p.ORDINAL_POSITION
        """
        
        cursor.execute(sql_defaults)
        rows = cursor.fetchall()
        
        logger.info(f"\nParâmetros da procedure fato.prQDataCicloDetalhado:")
        for row in rows:
            param_name = row[0]
            data_type = row[1]
            position = row[2]
            logger.info(f"  {position}. {param_name} ({data_type})")


if __name__ == "__main__":
    test_check_defaults()
    print()
    test_with_all_params()
