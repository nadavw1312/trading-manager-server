from common.middlewares.exception_middleware import ExceptionMiddleware
from common.middlewares.response_middleware import ensure_success_response_middleware
from server.src.features.big_data.conditions.orch.conditions_embedding_orch import ConditionsEmbeddingOrch
from server.src.routes import register_routes_v1
from server.src.common.services.proxy.init_proxy_locator_cs import init_proxy_locator_cs
from fastapi.middleware.cors import CORSMiddleware

from server.src.features.big_data.calculations.calculations_bl import CalculationsBl
from server.src.features.big_data.calculations.calculations_orch import CalculationsOrch
from server.src.features.big_data.conditions.conditions_bl import ConditionsBl
from server.src.features.big_data.conditions.conditions_orch import ConditionsOrch


def init_app(app):
    init_proxy_locator_cs()
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173/"],  # Update with your client URL
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )
    # Add the Exception Middleware to handle exceptions globally
    app.add_middleware(ExceptionMiddleware)

    # Add the Success Response Middleware to format successful responses
    app.middleware("http")(ensure_success_response_middleware)

    register_routes_v1(app)
    
    # CalculationsBl().load_and_insert_calculations()
    # ConditionsBl().load_and_insert_conditions()
    # ConditionsBl().update_conditions_embeddings()
    # CalculationsOrch().document_calculations()
    # ConditionsEmbeddingOrch().insert_conditions_embeddings()

    # Health check route
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
