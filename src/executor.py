import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .database import DatabaseConnection
from .date_utils import split_date_range_monthly
from .exporter import ExcelExporter

logger = logging.getLogger(__name__)


class ProcedureExecutor:
    """
    Classe responsável por carregar configurações de procedures e executá-las
    dividindo automaticamente períodos em meses.
    """

    def __init__(self, config_path: str = "config/procedures.yaml"):
        """
        Inicializa o executor de procedures.

        Args:
            config_path: Caminho para o arquivo de configuração YAML
        """
        self.config_path = config_path
        self.procedures_config = self._load_config()
        self.db_connection = DatabaseConnection()
        self.exporter = ExcelExporter()

    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega as configurações do arquivo YAML.

        Returns:
            Dicionário com as configurações das procedures
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")

        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                return config
        except yaml.YAMLError as e:
            raise Exception(f"Erro ao ler arquivo YAML: {e}")
        except Exception as e:
            raise Exception(f"Erro ao carregar configurações: {e}")

    def get_procedure_config(self, procedure_name: str) -> Dict[str, Any]:
        """
        Obtém a configuração de uma procedure específica.

        Args:
            procedure_name: Nome da procedure

        Returns:
            Dicionário com a configuração da procedure
        """
        for procedure in self.procedures_config.get("procedures", []):
            if procedure["name"] == procedure_name:
                return procedure

        raise ValueError(f"Procedure '{procedure_name}' não encontrada na configuração")

    def list_procedures(self) -> List[str]:
        """
        Lista todas as procedures configuradas.

        Returns:
            Lista com os nomes das procedures
        """
        return [proc["name"] for proc in self.procedures_config.get("procedures", [])]

    def _prepare_params(
        self,
        procedure_config: Dict[str, Any],
        date_start: datetime,
        date_end: datetime,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        Prepara os parâmetros para execução da procedure.
    
        Esta implementação é mais tolerante a diferenças de nome de parâmetro
        (ex.: DataInicial / data_inicial / DataInicial) e tenta mapear
        automaticamente os parâmetros do tipo datetime para `date_start` e
        `date_end` com heurísticas simples. Se houver dois parâmetros datetime
        sem nomes indicativos, o primeiro datetime será tratado como início e
        o segundo como fim.
    
        Args:
            procedure_config: Configuração da procedure
            date_start: Data inicial
            date_end: Data final
            extra_params: Parâmetros adicionais (opcional)
    
        Returns:
            Lista de parâmetros na ordem correta
        """
        params_config = procedure_config.get("params", [])
        params_list = [None] * len(params_config)
    
        # Contadores/flags para fallback quando nomes não forem explícitos
        assigned_start = False
        assigned_end = False
    
        # Primeiro passe: tenta mapear datetime por nome (case-insensitive, diferentes formas)
        for param_config in params_config:
            param_name = param_config["name"]
            param_type = param_config["type"]
            position = param_config["position"] - 1  # Converter para índice base 0
            lname = str(param_name).lower()
    
            if param_type == "datetime":
                # Heurísticas por nome
                if any(k in lname for k in ("inicial", "inicio", "start")):
                    params_list[position] = date_start
                    assigned_start = True
                elif any(k in lname for k in ("final", "fim", "end")):
                    params_list[position] = date_end
                    assigned_end = True
    
        # Segunda passe: preenche restantes (datetimes sem nome indicativo)
        for param_config in params_config:
            param_name = param_config["name"]
            param_type = param_config["type"]
            position = param_config["position"] - 1
            lname = str(param_name).lower()
    
            if param_type == "datetime" and params_list[position] is None:
                # Se nenhum dos dois já foi atribuído, atribui start ao primeiro encontrado
                if not assigned_start:
                    params_list[position] = date_start
                    assigned_start = True
                elif not assigned_end:
                    params_list[position] = date_end
                    assigned_end = True
                else:
                    # Se já atribuídos ambos, por segurança atribui date_end
                    params_list[position] = date_end
    
            elif param_type == "int":
                # Verifica se há um valor default
                default_value = param_config.get("default")
                pname = param_config["name"]
                if extra_params and pname in extra_params:
                    try:
                        params_list[position] = int(extra_params[pname])
                    except Exception:
                        raise ValueError(f"Parâmetro '{pname}' do tipo int inválido")
                elif default_value is not None:
                    params_list[position] = default_value
                else:
                    raise ValueError(f"Parâmetro '{pname}' do tipo int não fornecido")
    
            else:
                pname = param_config["name"]
                if extra_params and pname in extra_params:
                    params_list[position] = extra_params[pname]
                elif param_config.get("default") is not None:
                    params_list[position] = param_config["default"]
    
        # Valida se todos os parâmetros foram preenchidos
        if any(param is None for param in params_list):
            raise ValueError("Não foi possível preencher todos os parâmetros necessários")
    
        return params_list

    def execute_procedure(
        self,
        procedure_name: str,
        start_date: datetime,
        end_date: datetime,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Executa uma procedure dividindo o período em meses e exportando os resultados.

        Args:
            procedure_name: Nome da procedure a ser executada
            start_date: Data inicial do período
            end_date: Data final do período
            extra_params: Parâmetros adicionais (opcional)

        Returns:
            Lista com os caminhos dos arquivos gerados
        """
        # Obtém a configuração da procedure
        procedure_config = self.get_procedure_config(procedure_name)
        output_folder = procedure_config.get("output_folder", procedure_name)

        # Divide o período em meses
        monthly_periods = split_date_range_monthly(start_date, end_date)
        
        logger.info(f"Executando procedure '{procedure_name}' para {len(monthly_periods)} período(s) mensal(is)")

        generated_files = []

        for i, (period_start, period_end) in enumerate(monthly_periods, 1):
            logger.info(f"Executando período {i}/{len(monthly_periods)}: {period_start.strftime('%d/%m/%Y')} a {period_end.strftime('%d/%m/%Y')}")

            # Prepara os parâmetros para este período
            params = self._prepare_params(procedure_config, period_start, period_end, extra_params)

            # Ajusta horário inicial/final conforme padrão: 00:00:00 e 23:59:59
            period_start_dt = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end_dt = period_end.replace(hour=23, minute=59, second=59, microsecond=0)

            try:
                # Se for um objeto no schema 'fato', trocar execução de procedure por SELECT
                schema = procedure_name.split(".")[0] if "." in procedure_name else ""
                if schema.lower() == "fato":
                    # Permite configurar nome da tabela ou coluna de data na configuração
                    table_name = procedure_config.get("table", procedure_name)
                    date_column = procedure_config.get("date_column", "Data")

                    df = self.db_connection.execute_select(
                        table_name, period_start_dt, period_end_dt, date_column=date_column
                    )
                else:
                    # Executa a procedure (comportamento legado)
                    df = self.db_connection.execute_procedure(procedure_name, params)

                if df.empty:
                    logger.info(f"  Nenhum dado retornado para este período")
                    continue

                # Exporta para Excel
                file_path = self.exporter.export_to_excel(
                    df=df,
                    procedure_name=procedure_name,
                    output_folder=output_folder,
                    period_start=period_start,
                )

                generated_files.append(file_path)
                logger.info(f"  {len(df)} registros exportados")

            except Exception as e:
                logger.error(f"  Erro ao execututar período: {e}")
                continue

        logger.info(f"\nExecução concluída. {len(generated_files)} arquivo(s) gerado(s)")
        return generated_files

    def test_connection(self) -> bool:
        """
        Testa a conexão com o banco de dados.

        Returns:
            True se a conexão for bem-sucedida, False caso contrário
        """
        try:
            return self.db_connection.test_connection()
        except Exception as e:
            logger.error(f"Erro ao testar conexão: {e}")
            return False