from dagster import schedule, define_asset_job

all_assets_job = define_asset_job(name="update_all_assets_job", selection="*")

@schedule(
    job=all_assets_job,
    cron_schedule="0 0 * * *", # Cada día a las 00:00
    execution_timezone="UTC",
)
def daily_update_schedule(context):
    """
    Ejecuta el job que actualiza TODOS los assets diariamente.
    """
    return {}