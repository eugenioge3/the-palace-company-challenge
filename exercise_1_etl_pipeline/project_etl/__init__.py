from dagster import Definitions
from .assets import (
    user_relationships_table, 
    actors_table, 
    actor_relationships_view,
)
from .schedules import daily_relationships_update_schedule
from .resources import mysql_etl_resource

defs = Definitions(
    assets=[
        user_relationships_table, 
        actors_table, 
        actor_relationships_view
    ],
    schedules=[daily_relationships_update_schedule],
    resources={
        "mysql_conn": mysql_etl_resource
    }
)