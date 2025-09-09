import pandas as pd
import numpy as np
from dagster import asset, DagsterInvariantViolationError, AssetIn
from sqlalchemy import text

# --- ASSET 1: Tabla de Relaciones (user_relationships) ---
@asset(
    group_name="relationships",
    description="Lee la matriz de relaciones, la transforma y la carga en MySQL.",
    required_resource_keys={"mysql_conn"},
    compute_kind="python"
)
def user_relationships_table(context):
    engine = context.resources.mysql_conn
    table_name = "user_relationships"

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        person_a INT NOT NULL,
        person_b INT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (person_a, person_b)
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_table_query))

    excel_path = "/opt/dagster/app/data/relaciones.xlsx"
    sheet_name = "Matriz de adyacencia"
    context.log.info(f"Leyendo la matriz desde la hoja: '{sheet_name}'")

    try:

        # 1. Lee la hoja entera sin asumir estructura.
        df_raw = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
        
        # 2. Extrae la lista de todos los IDs numéricos válidos de la primera columna (columna A).
        all_ids = pd.to_numeric(df_raw.iloc[2:, 0], errors='coerce').dropna().astype(int)

        # 3. Extrae solo el bloque de datos numéricos (desde la celda C3 en adelante).
        data_block = df_raw.iloc[2:, 2:].copy()
        
        # 4. Crea una matriz cuadrada vacía, usando all_ids para el índice y las columnas.
        df_matrix = pd.DataFrame(index=all_ids, columns=all_ids)
        
        # 5. Rellena la matriz cuadrada con los datos del Excel.
        # Recorta los datos y los índices para que coincidan en tamaño
        valid_rows = all_ids[:len(data_block)]
        valid_cols = all_ids[:len(data_block.columns)]
        
        # Asigna los datos a la subsección correspondiente de la matriz cuadrada.
        df_matrix.loc[valid_rows, valid_cols] = data_block.values

        # 6. Convierte toda la matriz a tipo numérico para estandarizarla.
        df_matrix = df_matrix.apply(pd.to_numeric, errors='coerce')

    except Exception as e:
        raise DagsterInvariantViolationError(
            f"Error al leer o procesar la hoja '{sheet_name}'. "
            f"Revisa la estructura del archivo. Error: {e}"
        )

    context.log.info(f"Matriz procesada. Forma final: {df_matrix.shape}")
    
    context.log.info("Transformando matriz a lista de relaciones...")
    
    stacked = df_matrix.stack()
    relationships_series = stacked[stacked == 1]
    
    relationships_df = relationships_series.index.to_frame(index=False, name=["person_a", "person_b"])
    relationships_df = relationships_df[relationships_df['person_a'] != relationships_df['person_b']]
    
    sorted_pairs = np.sort(relationships_df.values, axis=1)
    final_df = pd.DataFrame(sorted_pairs, columns=["person_a", "person_b"]).drop_duplicates()

    context.log.info(f"Se encontraron {len(final_df)} relaciones únicas.")

    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text(f"TRUNCATE TABLE {table_name}"))
            if not final_df.empty:
                final_df.to_sql(table_name, con=conn, if_exists="append", index=False)
            context.log.info(f"Tabla '{table_name}' actualizada con {len(final_df)} registros.")
    
    return table_name

# --- ASSET 2: Tabla de Actores (actors) ---
@asset(
    group_name="relationships",
    description="Lee la lista de actores y la carga en la tabla 'actors'.",
    required_resource_keys={"mysql_conn"},
    compute_kind="python"
)
def actors_table(context):
    engine = context.resources.mysql_conn
    table_name = "actors"

    # Definimos el esquema de la nueva tabla
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        numeric_id INT PRIMARY KEY NOT NULL,
        letter_code VARCHAR(5) NOT NULL,
        actor_name VARCHAR(255) NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_table_query))

    excel_path = "/opt/dagster/app/data/relaciones.xlsx"
    sheet_name = "Lista de actores"
    context.log.info(f"Leyendo la lista de actores desde la hoja '{sheet_name}'")

    try:
        # Leemos los datos, saltando las primeras 4 filas y usando solo las columnas A, B, C
        df = pd.read_excel(
            excel_path,
            sheet_name=sheet_name,
            header=None,       
            skiprows=4,        
            usecols="A:C"      
        )
        # Nombramos las columnas
        df.columns = ["letter_code", "numeric_id", "actor_name"]
        
        # Limpieza de datos
        df.dropna(how="all", inplace=True) # Eliminar filas completamente vacías
        df['numeric_id'] = df['numeric_id'].astype(int) # Asegurar que el ID es un número entero

        # Convierte todos los códigos a mayúsculas para asegurar consistencia
        df['letter_code'] = df['letter_code'].str.upper()
        context.log.info("Se estandarizaron los 'letter_code' a mayúsculas.")

    except Exception as e:
        raise DagsterInvariantViolationError(f"Error al leer la hoja '{sheet_name}'. Asegúrate de que exista. Error: {e}")

    context.log.info(f"Se encontraron {len(df)} actores.")

    # Cargamos los datos en la base de datos
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text(f"TRUNCATE TABLE {table_name}"))
            if not df.empty:
                df.to_sql(table_name, con=conn, if_exists="append", index=False)
            context.log.info(f"Tabla '{table_name}' actualizada con {len(df)} registros.")
    
    return table_name

# --- ASSET 3: Vista Combinada (v_actor_relationships) ---
@asset(
    group_name="relationships",
    description="Crea una vista en MySQL para unir las relaciones con los nombres de los actores.",
    required_resource_keys={"mysql_conn"},
    # Definimos las dependencias: este asset se ejecuta DESPUÉS de los otros dos.
    ins={"user_relationships": AssetIn(key="user_relationships_table"),
         "actors": AssetIn(key="actors_table")},
    compute_kind="mysql"
)
def actor_relationships_view(context, user_relationships, actors):
    engine = context.resources.mysql_conn
    view_name = "v_actor_relationships"

    # La consulta SQL para crear la vista
    # Hacemos un doble JOIN a la tabla de actores para obtener el nombre de person_a y person_b
    create_view_query = f"""
    CREATE OR REPLACE VIEW {view_name} AS
    SELECT
        ur.person_a AS person_a_id,
        act_a.letter_code AS person_a_letter,
        act_a.actor_name AS person_a_name,
        ur.person_b AS person_b_id,
        act_b.letter_code AS person_b_letter,
        act_b.actor_name AS person_b_name
    FROM
        {user_relationships} ur
    JOIN
        {actors} act_a ON ur.person_a = act_a.numeric_id
    JOIN
        {actors} act_b ON ur.person_b = act_b.numeric_id;
    """
    
    context.log.info(f"Creando o reemplazando la vista '{view_name}'...")
    with engine.connect() as conn:
        conn.execute(text(create_view_query))
    context.log.info("Vista creada exitosamente.")


