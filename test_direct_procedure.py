"""
Script para testar execução direta da procedure
"""
import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

# Configurações
server = os.getenv("DB_SERVER")
database = os.getenv("DB_DATABASE")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
driver = os.getenv("DB_DRIVER")
encrypt = os.getenv("DB_ENCRYPT", "no")

# String de conexão
conn_str = (
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"TrustServerCertificate=yes;"
    f"Encrypt={encrypt}"
)

print("Conectando ao banco...")
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Testar a procedure
print("\nTestando procedure fato.prQDataCicloDetalhado")
print("Parâmetros: '20250101 00:00:00', '20250131 23:59:59'")

try:
    # Opção 1: Com SET NOCOUNT ON
    cursor.execute("SET NOCOUNT ON")
    cursor.execute("EXEC fato.prQDataCicloDetalhado '20250101 00:00:00', '20250131 23:59:59'")
    
    # Verificar se há resultado
    if cursor.description:
        print("\nColunas retornadas:")
        for col in cursor.description:
            print(f"  - {col[0]}")
        
        rows = cursor.fetchall()
        print(f"\nNúmero de registros: {len(rows)}")
        
        if len(rows) > 0:
            print("\nPrimeiras 3 linhas:")
            for i, row in enumerate(rows[:3]):
                print(f"  {i+1}: {row}")
    else:
        print("\n⚠️  Nenhum result set retornado (cursor.description is None)")
        print("Isso pode significar que:")
        print("  1. A procedure não tem SELECT")
        print("  2. A procedure tem RETURN mas não SELECT")
        print("  3. Há um erro na procedure")
        
        # Tentar verificar se há mensagens
        cursor.nextset()
        if cursor.description:
            print("\nEncontrado result set adicional!")
            rows = cursor.fetchall()
            print(f"Registros: {len(rows)}")

except Exception as e:
    print(f"\n❌ Erro: {e}")

finally:
    cursor.close()
    conn.close()
    print("\nConexão fechada.")
