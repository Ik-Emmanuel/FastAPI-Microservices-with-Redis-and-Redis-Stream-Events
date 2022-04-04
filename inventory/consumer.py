from main import redis, Product
import time

key = 'order_completed'
group = 'inventory-group'

try:
    redis.xgroup_create(key, group)
except:
    print("Group already exists")


while True:
    try:
        results = redis.xreadgroup(group, key, {key: '>'}, None)
        # key: > means get all events
        # print(results) #prints an event if fired else prints empty array
        # sample result event
        # [['order_completed', [('1649109991261-0', {'pk': '01FZV9TQSEM85CZQCQMGVS9YW3', 'product_id': '01FZV2G29E2T9S3G7N2QMMYPN3', 'price': '15.0', 'fee': '3.0', 'total': '18.0', 'quantity': '2', 'status': 'completed'})]]]
        if results != []:
            for result in results:
                obj = result[1][0][1]           
                try:
                    product = Product.get(obj['product_id'])
                    print(product)
                    product.quantity = product.quantity - int(obj['quantity'])
                    product.save()

                except:
                    redis.xadd('refund_order', obj, '*')
    except Exception as e:
        print(str(e))
    time.sleep(1)
    