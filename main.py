from fastapi import FastAPI
from controller.tourist_controller import router as tourist_router
from controller.recommendation_controller import router as recommendation_router
from db.database import engine, Base

# Inicializar a aplicação FastAPI
app = FastAPI()

# Criar automaticamente as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Incluir o controller com um prefixo e tags
app.include_router(tourist_router, prefix="/api", tags=["Tourists"])
app.include_router(recommendation_router, prefix="/api/recommendations", tags=["Recommendations"])  # Incluir o router de recomendações


# Rota raiz para verificar se a API está funcionando
@app.get("/")
async def root():
    return {"message": "API está funcionando com Controller!"}
