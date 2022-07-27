from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(root_path="/fastapi", docs_url='/docs', openapi_url='/openapi.json')

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
def get_root():
  return {'message': 'Bike Prediction API'}


# @app.get(f'{subpath}/detect_lang/')
# async def detect_language(text: str):
# 	return detector.detect_language(text)
