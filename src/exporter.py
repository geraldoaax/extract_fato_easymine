import pandas as pd
import os
from datetime import datetime
from typing import Optional


class ExcelExporter:
    """
    Classe responsável por exportar DataFrames para arquivos Excel.
    """

    def __init__(self, base_output_path: str = "output"):
        """
        Inicializa o exportador com o caminho base de saída.

        Args:
            base_output_path: Caminho base onde os arquivos serão salvos
        """
        self.base_output_path = base_output_path

    def _ensure_directory_exists(self, directory: str) -> None:
        """
        Garante que o diretório existe, criando-o se necessário.

        Args:
            directory: Caminho do diretório
        """
        os.makedirs(directory, exist_ok=True)

    def export_to_excel(
        self,
        df: pd.DataFrame,
        procedure_name: str,
        output_folder: str,
        period_start: datetime,
        filename: Optional[str] = None,
    ) -> str:
        """
        Exporta um DataFrame para um arquivo Excel.

        Args:
            df: DataFrame a ser exportado
            procedure_name: Nome da procedure
            output_folder: Nome da pasta de saída
            period_start: Início do período para nomeação do arquivo
            filename: Nome personalizado do arquivo (opcional)

        Returns:
            Caminho completo do arquivo gerado
        """
        if df.empty:
            raise ValueError("DataFrame está vazio. Nenhum dado para exportar.")

        # Monta o caminho completo
        full_output_path = os.path.join(self.base_output_path, output_folder)
        self._ensure_directory_exists(full_output_path)

        # Gera o nome do arquivo se não fornecido
        if not filename:
            date_suffix = period_start.strftime("%Y%m")
            filename = f"{procedure_name}_{date_suffix}.xlsx"

        # Garante que o arquivo tenha a extensão correta
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"

        file_path = os.path.join(full_output_path, filename)

        # Exporta para Excel
        try:
            df.to_excel(file_path, index=False, engine="openpyxl")
            print(f"Arquivo gerado com sucesso: {file_path}")
            return file_path
        except Exception as e:
            raise Exception(f"Erro ao exportar para Excel: {e}")

    def export_multiple_sheets(
        self,
        dataframes: dict,
        procedure_name: str,
        output_folder: str,
        period_start: datetime,
        filename: Optional[str] = None,
    ) -> str:
        """
        Exporta múltiplos DataFrames para um único arquivo Excel com múltiplas abas.

        Args:
            dataframes: Dicionário com {nome_aba: DataFrame}
            procedure_name: Nome da procedure
            output_folder: Nome da pasta de saída
            period_start: Início do período para nomeação do arquivo
            filename: Nome personalizado do arquivo (opcional)

        Returns:
            Caminho completo do arquivo gerado
        """
        if not dataframes:
            raise ValueError("Nenhum DataFrame fornecido para exportação.")

        # Filtra apenas DataFrames não vazios
        valid_dfs = {name: df for name, df in dataframes.items() if not df.empty}

        if not valid_dfs:
            raise ValueError("Todos os DataFrames estão vazios. Nenhum dado para exportar.")

        # Monta o caminho completo
        full_output_path = os.path.join(self.base_output_path, output_folder)
        self._ensure_directory_exists(full_output_path)

        # Gera o nome do arquivo se não fornecido
        if not filename:
            date_suffix = period_start.strftime("%Y%m")
            filename = f"{procedure_name}_{date_suffix}.xlsx"

        # Garante que o arquivo tenha a extensão correta
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"

        file_path = os.path.join(full_output_path, filename)

        # Exporta para Excel com múltiplas abas
        try:
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                for sheet_name, df in valid_dfs.items():
                    # Limita o nome da aba para 31 caracteres (limite do Excel)
                    safe_sheet_name = sheet_name[:31]
                    df.to_excel(writer, sheet_name=safe_sheet_name, index=False)

            print(f"Arquivo com múltiplas abas gerado com sucesso: {file_path}")
            return file_path
        except Exception as e:
            raise Exception(f"Erro ao exportar para Excel com múltiplas abas: {e}")