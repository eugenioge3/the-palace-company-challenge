import pandas as pd
from sqlalchemy import create_engine, text
import sys

print("Iniciando el proceso de ingesta de datos (modelo Muchos-a-Muchos)...")

DATABASE_URL = "postgresql://user:password@db:5432/techtest_db"
try:
    engine = create_engine(DATABASE_URL)
    # Usamos engine.begin() para asegurar que la transacción se guarde (COMMIT) al final
    with engine.begin() as connection:
        print("Conexión a la base de datos establecida exitosamente.")

        df = pd.read_csv('sample.csv')
        df.columns = df.columns.str.strip()

        df['state'] = df['state'].str.strip().str.upper()
        valid_states_mask = df['state'].str.match(r'^[A-Z]{2}$', na=False)
        df.loc[~valid_states_mask, 'state'] = None
        
        df.dropna(subset=['state', 'email', 'first_name', 'last_name'], inplace=True)
        print(f"Archivo CSV leído y validado. {len(df)} filas válidas.")

        unique_departments = df['department'].dropna().unique()
        departments_df = pd.DataFrame(unique_departments, columns=['name'])
        if not departments_df.empty:
            departments_df.to_sql('temp_departments', connection, if_exists='replace', index=False)
            connection.execute(text("INSERT INTO departments (name) SELECT name FROM temp_departments ON CONFLICT (name) DO NOTHING;"))
        print(f"{len(departments_df)} departamentos únicos procesados.")

        contacts_df = df.drop_duplicates(subset=['email'], keep='first').drop(columns=['department'])
        contacts_df.to_sql('temp_contacts', connection, if_exists='replace', index=False)
        connection.execute(text("""
            INSERT INTO contacts (first_name, last_name, company_name, email, address, city, state, zip, phone1, phone2)
            SELECT first_name, last_name, company_name, email, address, city, state, zip, phone1, phone2 FROM temp_contacts
            ON CONFLICT (email) DO UPDATE SET
                first_name = EXCLUDED.first_name, last_name = EXCLUDED.last_name, company_name = EXCLUDED.company_name,
                address = EXCLUDED.address, city = EXCLUDED.city, state = EXCLUDED.state, zip = EXCLUDED.zip,
                phone1 = EXCLUDED.phone1, phone2 = EXCLUDED.phone2;
        """))
        print(f"{len(contacts_df)} contactos únicos insertados/actualizados.")

        contacts_map = pd.read_sql(text("SELECT id, email FROM contacts"), connection).set_index('email')['id'].to_dict()
        departments_map = pd.read_sql(text("SELECT id, name FROM departments"), connection).set_index('name')['id'].to_dict()

        associations = []
        for _, row in df.dropna(subset=['department']).iterrows():
            if row['email'] in contacts_map and row['department'] in departments_map:
                associations.append({
                    'contact_id': contacts_map.get(row['email']),
                    'department_id': departments_map.get(row['department'])
                })
        
        if associations:
            assoc_df = pd.DataFrame(associations).drop_duplicates()
            assoc_df.to_sql('temp_assoc', connection, if_exists='replace', index=False)
            connection.execute(text("""
                INSERT INTO contact_department_association (contact_id, department_id)
                SELECT contact_id, department_id FROM temp_assoc
                ON CONFLICT (contact_id, department_id) DO NOTHING;
            """))
        print(f"{len(associations)} asociaciones contacto-departamento procesadas.")

except Exception as e:
    print(f"Ocurrió un error: {e}")
    sys.exit(1)

print("¡Proceso de ingesta completado exitosamente!")