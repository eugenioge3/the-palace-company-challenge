import pandas as pd
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
    context.log.info(f"Leyendo la matriz desde {excel_path}")

    try:
        excel_file = pd.ExcelFile(excel_path)
        sheet_names = excel_file.sheet_names
        preferred_sheet_name = "Matriz de adyacencia"
        sheet_to_load = sheet_names[0] if preferred_sheet_name not in sheet_names else preferred_sheet_name

        if sheet_to_load != preferred_sheet_name:
            context.log.warning(f"Hoja '{preferred_sheet_name}' no encontrada. Usando la primera: '{sheet_to_load}'.")
        else:
            context.log.info(f"Cargando desde la hoja: '{sheet_to_load}'.")

        df_matrix_raw = pd.read_excel(excel_path, sheet_name=sheet_to_load, header=1, index_col=0)
    except Exception as e:
        raise DagsterInvariantViolationError(f"Error al leer la hoja de la matriz. Error: {e}")

    df_matrix = df_matrix_raw.drop(columns=df_matrix_raw.columns[0])
    df_matrix.columns = df_matrix.index

    if not df_matrix.index.equals(df_matrix.columns):
        raise DagsterInvariantViolationError("Error de consistencia: Índices de filas y columnas no son idénticos.")
    
    context.log.info(f"Matriz procesada. Forma: {df_matrix.shape}")

    relationships = []
    persons = df_matrix.index.tolist()
    
    for person_a in persons:
        for person_b in persons:
            if df_matrix.loc[person_a, person_b] == 1 and person_a != person_b:
                sorted_pair = tuple(sorted((person_a, person_b)))
                if sorted_pair not in relationships:
                    relationships.append(sorted_pair)
    
    final_df = pd.DataFrame(relationships, columns=["person_a", "person_b"])
    context.log.info(f"Se encontraron {len(final_df)} relaciones únicas.")

    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text(f"TRUNCATE TABLE {table_name}"))
            if not final_df.empty:
                final_df.to_sql(table_name, con=conn, if_exists="append", index=False)
            context.log.info(f"Tabla '{table_name}' actualizada con {len(final_df)} registros.")
    
    return table_name # Devolvemos el nombre de la tabla para que otros assets puedan usarlo

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


