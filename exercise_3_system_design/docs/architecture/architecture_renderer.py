from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import CloudFront, APIGateway
from diagrams.aws.compute import ECS
from diagrams.aws.database import Aurora, ElastiCache
from diagrams.aws.analytics import AmazonOpensearchService
from diagrams.aws.storage import S3
from diagrams.aws.security import WAF
from diagrams.aws.ml import Personalize, Sagemaker, Lex
from diagrams.onprem.client import User

# Define el nombre del archivo de salida y la ruta relativa
output_filename = "docs/architecture/images/arquitectura_hotelera"

with Diagram("Arquitectura Hotelera con IA", show=False, filename=output_filename, graph_attr={"bgcolor": "transparent"}):
    
    # Creamos un nodo User
    user = User("Huésped Web/Móvil")

    with Cluster("AWS Cloud"):
        # Capa de entrada y seguridad
        waf = WAF("WAF & Shield")
        cdn = CloudFront("CloudFront CDN")
        api_gw = APIGateway("API Gateway")
        
        # Conexión de entrada (Ahora funcionará)
        user >> waf >> cdn >> api_gw

        # Microservicios en ECS/Fargate
        with Cluster("Microservicios (ECS Fargate)"):
            svc_search = ECS("Servicio Búsqueda")
            svc_display = ECS("Servicio Visualización")
            svc_guest = ECS("Servicio Huéspedes")
            svc_payment = ECS("Servicio Pagos")
            
            api_gw >> Edge(label="/search") >> svc_search
            api_gw >> Edge(label="/hotels") >> svc_display
            api_gw >> Edge(label="/guest") >> svc_guest
            api_gw >> Edge(label="/payment") >> svc_payment

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
        svc_search >> db_opensearch
        svc_display >> db_aurora
        svc_display >> storage_s3
        svc_guest >> db_cache
        svc_guest >> db_aurora
        svc_payment >> db_aurora
        svc_display >> Edge(color="darkgreen") >> ai_personalize
        svc_display >> Edge(color="darkgreen") >> ai_sagemaker
        api_gw >> Edge(label="Chatbot", color="darkgreen") >> ai_lex
        svc_guest >> Edge(color="darkgreen", style="dashed") >> ai_personalize