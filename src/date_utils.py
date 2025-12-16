from datetime import datetime, timedelta
from typing import List, Tuple


def split_date_range_monthly(start_date: datetime, end_date: datetime) -> List[Tuple[datetime, datetime]]:
    """
    Divide um período de datas em intervalos mensais.

    Args:
        start_date: Data inicial do período
        end_date: Data final do período

    Returns:
        Lista de tuplas (data_inicial, data_final) para cada mês,
        onde data_inicial é o primeiro dia do mês às 00:00:00
        e data_final é o último dia do mês às 23:59:59
    """
    if start_date > end_date:
        raise ValueError("Data inicial não pode ser maior que a data final")

    monthly_ranges = []
    current_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    while current_date <= end_date:
        # Calcula o último dia do mês atual
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1, day=1)

        last_day_of_month = next_month - timedelta(days=1)

        # Define o período do mês
        month_start = max(current_date, start_date.replace(hour=0, minute=0, second=0, microsecond=0))
        month_end = min(last_day_of_month.replace(hour=23, minute=59, second=59, microsecond=0),
                       end_date.replace(hour=23, minute=59, second=59, microsecond=0))

        monthly_ranges.append((month_start, month_end))

        # Avança para o próximo mês
        current_date = next_month

    return monthly_ranges


def parse_date_string(date_str: str) -> datetime:
    """
    Converte uma string no formato YYYYMMDD para datetime.

    Args:
        date_str: String no formato YYYYMMDD

    Returns:
        Objeto datetime
    """
    try:
        return datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        raise ValueError(f"Formato de data inválido: {date_str}. Use o formato YYYYMMDD (ex: 20250101)")