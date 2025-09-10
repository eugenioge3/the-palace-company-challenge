# The Palace Company - Data Engineering Challenge

Este repositorio contiene las soluciones para la prueba técnica de Data Engineer Manager. El desafío se ha dividido en tres ejercicios distintos, cada uno ubicado en su respectiva carpeta.

## Estructura del Repositorio

- **[Exercise 1: ETL Pipeline](https://github.com/eugenioge3/the-palace-company-challenge/tree/main/exercise_1_etl_pipeline)**: Contiene un pipeline de ETL robusto y reproducible construido con Dagster para procesar datos de relaciones de usuarios.
- **[Exercise 2: REST API](https://github.com/eugenioge3/the-palace-company-challenge/tree/main/exercise_2_rest_api)**:  Contiene la solución propuesta para el desarrollo de una API REST para la ingesta y consulta de datos.
- **[Exercise 3: System Design](https://github.com/eugenioge3/the-palace-company-challenge/tree/main/exercise_3_system_design)**: Contiene el diagrama de arquitectura y la documentación para la propuesta de diseño de sistemas en la nube.

## Filosofía de Diseño

Las soluciones presentadas siguen principios de ingeniería de software moderna aplicados a datos:

- **Reproducibilidad:** Los entornos son containerizados con Docker para garantizar ejecuciones consistentes.
- **Fiabilidad:** Se implementan validaciones de datos y pruebas unitarias para asegurar la calidad y el correcto funcionamiento. 
- **Mantenibilidad:** El código está organizado de forma modular, separando la lógica de negocio, la orquestación y la configuración.
- **Documentación:** Cada ejercicio está auto-documentado con un `README.md` que detalla su propósito, funcionamiento y decisiones de diseño.

### Otras Consideraciones

Aunque este repositorio es un challenge y no contempla la implementación completa de ciertas prácticas de producción, es importante tener en cuenta:

- **Escalabilidad:** En un entorno real, las soluciones deberían diseñarse para manejar volúmenes crecientes de datos y usuarios sin degradar el rendimiento.
- **Costos:** La eficiencia en el uso de recursos y servicios en la nube es clave para optimizar costos operativos.
- **Compatibilidad con servicios y tecnologías existentes:** Considerar la integración con otros sistemas y la facilidad de mantenimiento a largo plazo.
- **Seguridad y cumplimiento:** Aunque no se implementa en este desafío, es fundamental pensar en la protección de datos y cumplimiento de regulaciones en producción.
