from fastapi import FastAPI
#from database import engine
#from usuario import modelo

#modelo.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}