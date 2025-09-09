# project_etl/logic.py
import pandas as pd
from pandas import DataFrame # Usamos el import directo

def transform_relationships(df_matrix: DataFrame) -> DataFrame:
    """
    Transforma una matriz de adyacencia en una lista de aristas (edge list).
    NOTA: Se ha eliminado la validación con Pandera para simplificar la ejecución del entorno.
    Se asume que el formato de entrada es correcto.
    """
    # (Opcional) Una validación simple y nativa de pandas
    if not df_matrix.index.equals(df_matrix.columns):
        raise ValueError("El índice y las columnas del DataFrame de la matriz no coinciden.")

    relationships = []
    persons = df_matrix.columns.tolist()
    
    for person_a in persons:
        for person_b in persons:
            # Comprobar si hay relación (valor == 1) y no es una auto-relación
            if df_matrix.loc[person_a, person_b] == 1 and person_a != person_b:
                # Normalizar para evitar duplicados (A,C) y (C,A)
                sorted_pair = tuple(sorted((person_a, person_b)))
                if sorted_pair not in relationships:
                    relationships.append(sorted_pair)
    
    if not relationships:
        return pd.DataFrame(columns=["person_a", "person_b"])
        
    return pd.DataFrame(relationships, columns=["person_a", "person_b"])