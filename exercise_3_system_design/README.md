# Propuesta de Arquitectura Cloud para Plataforma de Reservas Hoteleras

## 1. Resumen Ejecutivo

Este documento describe una arquitectura de microservicios nativa de la nube, utilizando **Amazon Web Services (AWS)**, para la migración y modernización del sitio web de gestión de reservas hoteleras. La arquitectura está diseñada para ser **globalmente rápida**, **segura**, **escalable**, **operativamente robusta** y estar enriquecida con capacidades de **Inteligencia Artificial** para ofrecer una experiencia de usuario superior y optimizar los ingresos del negocio.

## 2. Principios de Diseño

*   **Nube Nativa:** Uso de servicios gestionados de AWS para minimizar la carga operativa.
*   **Desacoplamiento:** Microservicios independientes que se pueden desarrollar, desplegar y escalar de forma autónoma.
*   **Escalabilidad y Elasticidad:** Infraestructura que se adapta automáticamente a la demanda, optimizando costos.
*   **Seguridad por Diseño:** Seguridad integrada en cada capa, desde la red hasta la aplicación.
*   **Observabilidad:** Monitoreo y trazabilidad centralizados para una operación proactiva del sistema.
*   **Inteligencia Integrada:** Uso proactivo de IA para mejorar la experiencia del cliente y las decisiones de negocio.

## 3. Diagrama de la Arquitectura Propuesta

El siguiente diagrama ilustra la interacción entre los diferentes componentes de la solución, desde la entrada del usuario hasta las capas de datos, monitoreo e inteligencia artificial.

![Arquitectura Propuesta](docs/architecture/images/arquitectura_hotelera.png)

*   **Nota**: Este diagrama fue generado utilizando la librería `diagrams` de Python, lo que permite versionar la arquitectura como código (`Diagrams as Code`).

## 4. Desglose de Componentes

### Capa de Presentación y Entrega (Frontend & Delivery)
*   **Amazon S3:** Aloja los activos estáticos del sitio web (HTML, CSS, JS).
    *   **Optimización de Costos:** Se utilizarán políticas de ciclo de vida para optimizar costos, moviendo automáticamente los activos menos accedidos (ej. fotos de hoteles antiguos o facturas pasadas) a clases de almacenamiento más económicas como `S3 Standard-IA` (Acceso Infrecuente) o `S3 Glacier` (Archivo).
*   **Amazon CloudFront (CDN):** Distribuye el contenido globalmente, almacenándolo en caché cerca de los usuarios para una latencia mínima.
*   **AWS WAF & Shield:** Protege la aplicación contra ataques web comunes (Inyección SQL, XSS) a nivel de borde.

### API y Lógica de Negocio (Backend)
*   **Amazon API Gateway:** Punto de entrada único y seguro para todas las peticiones. Gestiona la autenticación, autorización y enrutamiento a los microservicios.
*   **AWS Fargate (con ECS):** Motor de cómputo serverless para ejecutar nuestros microservicios en contenedores Docker sin gestionar servidores.
    *   **Servicio de Búsqueda:** Potenciado por OpenSearch, permite búsquedas complejas y semánticas.
    *   **Servicio de Visualización:** Entrega los datos de los hoteles (descripciones, precios) desde Aurora y las imágenes desde S3/CloudFront.
    *   **Servicio para Huéspedes:** Gestiona perfiles, favoritos e historial de navegación usando Aurora y ElastiCache para acceso rápido.
    *   **Servicio de Pagos:** Procesa transacciones de forma segura, integrándose con servicios de pago y registrando en Aurora.

### Capa de Datos (Data Layer)
*   **Amazon Aurora (Global Database):** Base de datos relacional principal para datos transaccionales (reservas, usuarios). Garantiza lecturas rápidas para usuarios internacionales.
*   **Amazon ElastiCache (Redis):** Caché en memoria para datos de acceso frecuente como sesiones y favoritos, reduciendo la carga en la base de datos principal.
*   **Amazon OpenSearch Service:** Motor de búsqueda para indexar los datos de los hoteles y habilitar búsquedas full-text, geolocalizadas y semánticas.
    *   **Flujo de Datos:** Nota importante: OpenSearch se alimenta de los datos de Aurora a través de un **proceso de sincronización en segundo plano** (ej. usando AWS Lambda gatillado por eventos de la base de datos). No se conecta directamente durante la petición del usuario, garantizando así un rendimiento óptimo en las búsquedas.

### Capa de Inteligencia Artificial
*   **Amazon Personalize:** Ofrece recomendaciones de hoteles personalizadas ("Usuarios como tú también vieron...") basadas en el comportamiento del usuario.
*   **Amazon SageMaker:** Despliega modelos de Machine Learning para implementar *Dynamic Pricing*, ajustando los precios en tiempo real según la demanda y otras variables.
*   **Amazon Lex + Bedrock:** Potencia un chatbot de asistencia 24/7 que responde preguntas frecuentes y ayuda en el proceso de reserva con un lenguaje natural y fluido.

## 5. Monitoreo, Alertas y Trazabilidad

Una arquitectura robusta requiere una visibilidad completa de su estado y rendimiento. **Amazon CloudWatch** será el pilar central de nuestra estrategia de observabilidad.
*   **Logs Centralizados (CloudWatch Logs):** Todos los microservicios ejecutándose en Fargate, así como otras funciones (Lambda) y servicios, enviarán sus logs a CloudWatch. Esto crea un repositorio centralizado para facilitar la depuración de errores y el análisis de comportamiento.
*   **Métricas de Rendimiento (CloudWatch Metrics):** Se monitorearán métricas clave de todos los servicios: uso de CPU/memoria de los contenedores, latencia del API Gateway, número de conexiones a la base de datos, tiempo de respuesta de los servicios de IA, etc.
*   **Alertas Proactivas (CloudWatch Alarms):** Se configurarán alarmas automáticas que notificarán al equipo de operaciones (vía email, Slack o PagerDuty) si alguna métrica cruza un umbral predefinido. Por ejemplo:
    *   Alerta si la tasa de errores 5xx del API Gateway supera el 1%.
    *   Alerta si el uso de CPU de un servicio se mantiene por encima del 80% durante más de 5 minutos.
    *   Alerta si la latencia de la base de datos aumenta significativamente.

## 6. Consideraciones de Costos

La arquitectura está diseñada para ser costo-eficiente, apalancándose en el modelo de pago por uso de la nube.
*   **Costos Variables (Pay-as-you-go):** La mayoría de los servicios de cómputo como **AWS Fargate**, **API Gateway** y **AWS Lambda** son serverless. Esto significa que solo se paga por el tiempo de cómputo que se utiliza, eliminando el costo de servidores inactivos y adaptándose perfectamente a la demanda variable del negocio.
*   **Costos Provisionados (Siempre Activos):** Componentes como **Amazon Aurora**, **ElastiCache** y **OpenSearch** requieren capacidad provisionada y representan el costo base de la infraestructura. Para optimizar estos costos, se pueden utilizar esquemas de compra como **AWS Savings Plans** o **Instancias Reservadas**, que ofrecen descuentos significativos a cambio de un compromiso de uso a 1 o 3 años.
*   **Almacenamiento y Transferencia:** El costo de **S3** y la transferencia de datos de **CloudFront** es bajo por GB, pero escala con el volumen. El uso inteligente de las clases de almacenamiento de S3 (como se mencionó anteriormente) es clave para mantener estos costos bajo control.
*   **Servicios de IA:** El costo de **Personalize** y **SageMaker** se basa en el uso (horas de entrenamiento, horas de hosting del endpoint, número de recomendaciones/predicciones). Su valor se mide por el retorno de inversión que generan, como el aumento en la tasa de conversión y la optimización de los ingresos por habitación.