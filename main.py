#!/usr/bin/env python3
"""
SQL Procedure Executor - Interface CLI

Uma ferramenta para executar procedures SQL Server dividindo períodos em meses
e exportando os resultados para arquivos Excel.
"""

import argparse
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from src.executor import ProcedureExecutor
from src.date_utils import parse_date_string

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def parse_extra_params(params_list: list) -> Dict[str, Any]:
    """
    Converte uma lista de strings formato key=value para um dicionário.

    Args:
        params_list: Lista de strings no formato key=value

    Returns:
        Dicionário com os parâmetros parseados
    """
    params = {}
    for param in params_list:
        if "=" not in param:
            raise ValueError(f"Parâmetro inválido: {param}. Use o formato key=value")
        key, value = param.split("=", 1)
        # Tenta converter para int se possível
        try:
            if value.isdigit():
                params[key] = int(value)
            else:
                params[key] = value
        except ValueError:
            params[key] = value
    return params


def list_procedures() -> None:
    """
    Lista todas as procedures configuradas.
    """
    try:
        executor = ProcedureExecutor()
        procedures = executor.list_procedures()

        logger.info("Procedures disponíveis:")
        for i, proc in enumerate(procedures, 1):
            logger.info(f"  {i}. {proc}")
    except Exception as e:
        logger.error(f"Erro ao listar procedures: {e}")
        sys.exit(1)


def test_connection() -> None:
    """
    Testa a conexão com o banco de dados.
    """
    try:
        executor = ProcedureExecutor()
        if executor.test_connection():
            logger.info("✓ Conexão com o banco de dados estabelecida com sucesso!")
        else:
            logger.error("✗ Falha ao conectar com o banco de dados.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"✗ Erro ao testar conexão: {e}")
        sys.exit(1)


def execute_procedure(
    procedure_name: str,
    start_date: datetime,
    end_date: datetime,
    extra_params: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Executa uma procedure com os parâmetros fornecidos.

    Args:
        procedure_name: Nome da procedure
        start_date: Data inicial
        end_date: Data final
        extra_params: Parâmetros adicionais
    """
    try:
        executor = ProcedureExecutor()

        # Valida se a procedure existe
        available_procedures = executor.list_procedures()
        if procedure_name not in available_procedures:
            logger.error(f"✗ Procedure '{procedure_name}' não encontrada.")
            logger.info("Procedures disponíveis:")
            for proc in available_procedures:
                logger.info(f"  - {proc}")
            sys.exit(1)

        # Executa a procedure
        generated_files = executor.execute_procedure(
            procedure_name=procedure_name,
            start_date=start_date,
            end_date=end_date,
            extra_params=extra_params,
        )

        if generated_files:
            logger.info("\nArquivos gerados:")
            for file_path in generated_files:
                logger.info(f"  - {file_path}")
        else:
            logger.info("\nNenhum arquivo foi gerado.")

    except Exception as e:
        logger.error(f"✗ Erro ao executar procedure: {e}")
        sys.exit(1)


def main():
    """
    Função principal da interface CLI.
    """
    parser = argparse.ArgumentParser(
        description="Executa procedures SQL Server dividindo períodos em meses e exportando para Excel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Listar procedures disponíveis
  python main.py --list

  # Testar conexão com o banco
  python main.py --test

  # Executar procedure sem parâmetros adicionais
  python main.py -p fato.ciclodetalhado -s 20250101 -e 20251031

  # Executar procedure com parâmetros adicionais
  python main.py -p fato.outra_procedure -s 20250101 -e 20251031 -P id_empresa=5

  # Executar com múltiplos parâmetros adicionais
  python main.py -p fato.outra_procedure -s 20250101 -e 20251031 -P id_empresa=5 tipo=ANALISE
        """
    )

    parser.add_argument(
        "-p", "--procedure",
        type=str,
        help="Nome da procedure a ser executada"
    )

    parser.add_argument(
        "-s", "--start",
        type=str,
        help="Data inicial no formato YYYYMMDD (ex: 20250101)"
    )

    parser.add_argument(
        "-e", "--end",
        type=str,
        help="Data final no formato YYYYMMDD (ex: 20251031)"
    )

    parser.add_argument(
        "-P", "--params",
        action="append",
        help="Parâmetros adicionais no formato key=value. Pode ser usado múltiplas vezes."
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="Lista todas as procedures configuradas"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Testa a conexão com o banco de dados"
    )

    args = parser.parse_args()

    # Ações que não requerem execução de procedure
    if args.list:
        list_procedures()
        return

    if args.test:
        test_connection()
        return

    # Validação dos argumentos para execução de procedure
    if not args.procedure:
        logger.error("✗ Nome da procedure é obrigatório para execução.")
        parser.print_help()
        sys.exit(1)

    if not args.start or not args.end:
        logger.error("✗ Data inicial e final são obrigatórias para execução.")
        parser.print_help()
        sys.exit(1)

    try:
        start_date = parse_date_string(args.start)
        # Treat CLI end date as inclusive end-of-day
        end_date = parse_date_string(args.end).replace(hour=23, minute=59, second=59, microsecond=999999)
    except ValueError as e:
        print(f"✗ {e}")
        sys.exit(1)

    if start_date > end_date:
        logger.error("✗ Data inicial não pode ser maior que a data final.")
        sys.exit(1)

    # Parse dos parâmetros adicionais
    extra_params = None
    if args.params:
        try:
            extra_params = parse_extra_params(args.params)
        except ValueError as e:
            logger.error(f"✗ {e}")
            sys.exit(1)

    # Executa a procedure
    execute_procedure(args.procedure, start_date, end_date, extra_params)


if __name__ == "__main__":
    main()