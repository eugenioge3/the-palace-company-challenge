from dagster import schedule, define_asset_job

# Creamos un "job" que tiene como objetivo materializar nuestro asset
relationships_job = define_asset_job(name="update_relationships_job", selection="user_relationships_table")

# Creamos el schedule que ejecutará este job
@schedule(
    job=relationships_job,
    cron_schedule="0 0 * * *", # Cada día a las 00:00
    execution_timezone="UTC",
)
def daily_relationships_update_schedule(context):
    """
    Ejecuta el job de actualización de relaciones diariamente.
    """
    return {}