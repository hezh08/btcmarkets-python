import btcmarkets
import random
import string


# Test

api_key = "<add-your-own>"
api_secret = "<add-your-own>"

client = btcmarkets.Client(api_key, api_secret)

client_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)) # client order id

print(client.list_orders(status="open"))
print("client order #" + client_id)
print(client.place_new_order("BTC-AUD", "100.12", "0.0024", "Limit", "Bid", client_order_id=client_id))
print(client.cancel_an_order(client_id))
print(client.list_orders(status="open"))