# The Palace Company - Data Engineer Challenge

Este repositorio contiene las soluciones para la prueba técnica de Data Engineer Manager. El desafío se ha dividido en tres ejercicios distintos, cada uno ubicado en su respectiva carpeta.

## Estructura del Repositorio

- **/exercise_1_etl_pipeline**: Contiene un pipeline de ETL robusto y reproducible construido con Dagster, Docker, Pandera y Pytest para procesar datos de relaciones de usuarios.
- **/exercise_2_rest_api**: (Placeholder) Contiene la solución propuesta para el desarrollo de una API REST para la ingesta y consulta de datos.
- **/exercise_3_system_design**: (Placeholder) Contiene el diagrama de arquitectura y la documentación para la propuesta de diseño de sistemas en la nube.

## Filosofía de Diseño

Las soluciones presentadas siguen principios de ingeniería de software moderna aplicados a datos:

- **Reproducibilidad:** Todos los entornos son containerizados con Docker para garantizar ejecuciones consistentes.
- **Fiabilidad:** Se implementan validaciones de datos (Pandera) y pruebas unitarias (Pytest) para asegurar la calidad y el correcto funcionamiento.
- **Mantenibilidad:** El código está organizado de forma modular, separando la lógica de negocio, la orquestación y la configuración.
- **Documentación:** Cada ejercicio está auto-documentado con un `README.md` que detalla su propósito, funcionamiento y decisiones de diseño.