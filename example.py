import btcmarkets

# Example

api_key = "<add-your-own>"
api_secret = "<add-your-own>"

client = btcmarkets.Client(api_key, api_secret)

print(client.list_orders(status="open"))
order = client.place_new_order("BTC-AUD", "100.12", "0.0024", "Limit", "Bid")
print(order)
print(client.cancel_an_order(order["orderId"]))
print(client.list_orders(status="open"))
