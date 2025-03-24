from fastapi import FastAPI
from controller.tourist_controller import router as tourist_router
from db.database import engine, Base

# Inicializar a aplicação FastAPI
app = FastAPI()

# Criar automaticamente as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Incluir o controller com um prefixo e tags
app.include_router(tourist_router, prefix="/api", tags=["Tourists"])

# Rota raiz para verificar se a API está funcionando
@app.get("/")
async def root():
    return {"message": "API está funcionando com Controller!"}
