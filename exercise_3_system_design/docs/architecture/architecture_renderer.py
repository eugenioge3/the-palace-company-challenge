from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import CloudFront, APIGateway
from diagrams.aws.compute import ECS
from diagrams.aws.database import Aurora, ElastiCache
from diagrams.aws.analytics import AmazonOpensearchService
from diagrams.aws.storage import S3
from diagrams.aws.security import WAF
from diagrams.aws.ml import Personalize, Sagemaker, Lex
from diagrams.aws.management import Cloudwatch 
from diagrams.onprem.client import User

# Define el nombre del archivo de salida y la ruta relativa
output_filename = "docs/architecture/images/arquitectura_hotelera"

with Diagram("Arquitectura Hotelera con IA", show=False, filename=output_filename, graph_attr={"bgcolor": "transparent"}):
    
    user = User("Huésped Web/Móvil")

    with Cluster("AWS Cloud"):
        # Capa de entrada y seguridad
        waf = WAF("WAF & Shield")
        cdn = CloudFront("CloudFront CDN")
        api_gw = APIGateway("API Gateway")
        
        user >> waf >> cdn >> api_gw

        # Microservicios en ECS/Fargate
        with Cluster("Microservicios (ECS Fargate)"):
            services_group = [
                ECS("Servicio Búsqueda"),
                ECS("Servicio Visualización"),
                ECS("Servicio Huéspedes"),
                ECS("Servicio Pagos")
            ]
        
        # Capa de Monitoreo
        with Cluster("Monitoreo y Operaciones"): 
            cw = Cloudwatch("CloudWatch\n(Logs, Métricas, Alertas)")

        # Conexiones principales
        api_gw >> Edge(label="/search") >> services_group[0]
        api_gw >> Edge(label="/hotels") >> services_group[1]
        api_gw >> Edge(label="/guest") >> services_group[2]
        api_gw >> Edge(label="/payment") >> services_group[3]
        
        # Conexión conceptual de monitoreo a los servicios
        cw >> Edge(style="dotted", color="firebrick") >> services_group 

        # Capa de Datos
        with Cluster("Capa de Datos"):
            db_aurora = Aurora("Aurora DB (Global)\nReservas, Usuarios")
            db_opensearch = AmazonOpensearchService("OpenSearch\nBúsqueda semántica")
            db_cache = ElastiCache("ElastiCache (Redis)\nSesiones, Favoritos")
            storage_s3 = S3("S3\nImágenes, Activos")

        # Capa de Inteligencia Artificial
        with Cluster("Capa de IA (Servicios Gestionados)"):
            ai_personalize = Personalize("Amazon Personalize\nRecomendaciones")
            ai_lex = Lex("Amazon Lex + Bedrock\nChatbot Asistente")
            ai_sagemaker = Sagemaker("SageMaker Endpoint\nDynamic Pricing")

        # Conexiones de los servicios
        services_group[0] >> db_opensearch
        services_group[1] >> db_aurora
        services_group[1] >> storage_s3
        services_group[2] >> db_cache
        services_group[2] >> db_aurora
        services_group[3] >> db_aurora
        
        services_group[1] >> Edge(color="darkgreen") >> ai_personalize
        services_group[1] >> Edge(color="darkgreen") >> ai_sagemaker
        api_gw >> Edge(label="Chatbot", color="darkgreen") >> ai_lex
        services_group[2] >> Edge(color="darkgreen", style="dashed") >> ai_personalize