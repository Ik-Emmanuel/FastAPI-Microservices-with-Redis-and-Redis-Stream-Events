from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()

### used for react front end which runs on a separate host 3000 
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'], 
    allow_methods=['*'],
    allow_headers=['*']

)

redis = get_redis_connection(
    host=REDIS_PUBLIC_HOST_URL,
    port=PORT_NUMBER,
    password=REDIS_PASSWORD,
    decode_responses = True
)

class Product(HashModel):
    name:str
    price:float
    quantity:int

    class Meta:
        database = redis

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Microservices"}

@app.get("/products")
def all():
    return [format(pk) for pk in Product.all_pks()]

#helper function
def format(pk: str):
    product = Product.get(pk)
    return {
        'id':product.pk,
        'name': product.name, 
        'price': product.price,
        'quantity': product.quantity
    }

@app.post('/products')
def create(product:Product):
    return product.save()

@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)


@app.delete('/products/{pk}')
def delete(pk: str):
    return Product.delete(pk)


