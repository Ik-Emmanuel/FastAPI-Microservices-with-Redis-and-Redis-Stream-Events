from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests, time

from fastapi.background import BackgroundTasks


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



class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str #pending, completed, refunded

    class Meta:
        database = redis


@app.get("/orders")
def get_orders():
    return [format(pk) for pk in Order.all_pks()]

#helper function
def format(pk: str):
    order = Order.get(pk)
    return {
        'id':order.pk,
        'price': order.price, 
        'total': order.total,
        'quantity': order.quantity,
        'status':order.status
    }


@app.get('/orders/{pk}')
def get(pk: str):
    #to create and start listening for events
    order = Order.get(pk)
    redis.xadd('refund_order', order.dict(), '*')
    return order



def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    #add event to redis stream with an auto generated id indicated by '*' else you add your own redis streams event ID
    # redis.xadd('KEY', A Dict,  'Event ID') 
    redis.xadd('order_completed', order.dict(), '*')

@app.post('/orders')
async def create(request: Request, background_tasks:BackgroundTasks): #id, quantity
    body = await request.json()
    req = requests.get('http://localhost:8000/products/%s' %body['id'])
    product = req.json()
    order = Order(
        product_id = body['id'],
        price = product['price'],
        fee = 0.2 * product['price'],
        total = 1.2 * product['price'], #price + fee
        quantity = body['quantity'], 
        status='pending'
    )
    order.save()

    # background_tasks.add_task(<function name>, <parameters>)
    background_tasks.add_task(order_completed, order)
    return order




