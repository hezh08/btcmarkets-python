import base64
from collections import OrderedDict
import hashlib
import hmac
import json
import requests
import time


# Initial code is taken from https://github.com/BTCMarkets/api-v3-client-python/blob/master/main.py
# And has been modified to include all API v3 endpoints as at 30 Jan 2021.

class Client(object):
    def __init__(self, key, secret):
        self.key = str(key)
        self.secret = base64.b64decode(secret)
        self.url = "https://api.btcmarkets.net"

    # Private methods

    def _request(self, method, path, query_string=None, data=None):
        if data is not None:
            data = json.dumps(data)

        headers = self._build_headers(method, self.key, self.secret, path, data)
        fullPath = ""
        if query_string is None:
            fullPath = path
        else:
            fullPath = path + "?" + query_string

        try:
            if method == "POST":
                response = requests.post(self.url + fullPath, data=data, headers=headers)
            elif method == "PUT":
                response = requests.put(self.url + fullPath, data=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(self.url + fullPath, headers=headers)
            else:
                response = requests.get(self.url + fullPath, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            return e.response.json()["code"]
        except Exception as e:
            raise


    def _build_headers(self, method, api_key, api_secret, path, data):
        timestamp = str(int(time.time() * 1000))
        message = method + path + timestamp
        if data is not None:
            message += data
        
        signature = self._create_signature(api_secret, message)

        headers = {
            "Accept": "application/json",
            "Accept-Charset": "UTF-8",
            "Content-Type": "application/json",
            "BM-AUTH-APIKEY": api_key,
            "BM-AUTH-TIMESTAMP": timestamp,
            "BM-AUTH-SIGNATURE": signature
        }

        return headers

    def _create_signature(self, api_secret, message):
        presignature = base64.b64encode(hmac.new(
            api_secret, message.encode("utf-8"), digestmod=hashlib.sha512).digest())
        signature = presignature.decode("utf8")

        return signature

    # Public methods

    def list_active_markets(self):
        return self._request("GET", "/v3/markets")

    def get_market_ticker(self, market_id):
        return self._request("GET", "/v3/markets/{}/ticker".format(market_id))

    def get_market_trades(self, market_id, before=None, after=None, limit=None):
        data = []
        if before is not None:
            data.append("before={}".format(before))
        if after is not None:
            data.append("after={}".format(after))
        if limit is not None:
            data.append("limit={}".format(limit))

        if not data:
            return self._request("GET", "/v3/markets/{}/trades".format(market_id))
        else:
            return self._request("GET", "/v3/markets/{}/trades".format(market_id), "&".join(data))

    def get_market_orderbook(self, market_id, level=None):
        if level is not None:
            return self._request("GET", "/v3/markets/{}/orderbook".format(market_id), "level={}".format(level))
        else:
            return self._request("GET", "/v3/markets/{}/orderbook".format(market_id))
    
    def get_market_candles(self, market_id, time_window=None, from_=None,
                           to=None, before=None, after=None, limit=None):
        data = []
        if time_window is not None:
            data.append("timeWindow={}".format(time_window))
        if from_ is not None:
            data.append("from={}".format(from_))
        if to is not None:
            data.append("to={}".format(to))
        if before is not None:
            data.append("before={}".format(before))
        if after is not None:
            data.append("after={}".format(after))
        if limit is not None:
            data.append("limit={}".format(limit))

        if not data:
            return self._request("GET", "/v3/markets/{}/candles".format(market_id))
        else:
            return self._request("GET", "/v3/markets/{}/candles".format(market_id), "&".join(data))

    def get_multiple_tickers(self, *market_ids):
        data = []
        for m in market_ids:
            data.append("marketId={}".format(m))
        return self._request("GET", "/v3/markets/tickers", "&".join(data))

    def get_multiple_orderbooks(self, *market_ids):
        data = []
        for m in market_ids:
            data.append("marketId={}".format(m))
        return self._request("GET", "/v3/markets/orderbooks", "&".join(data))

    def place_new_order(self, market_id, price, amount, order_type, side, 
                        trigger_price=None, target_amount=None, time_in_force=None, 
                        post_only="False", self_trade=None, client_order_id=None):
        data = OrderedDict([
            ("marketId", str(market_id)),
            ("price", str(price)),
            ("amount", str(amount)),
            ("type", str(order_type)),
            ("side", str(side))
        ])
        if trigger_price is not None:
            data["triggerPrice"] = str(trigger_price)
        if target_amount is not None:
            data["targetAmount"] = str(target_amount)
        if time_in_force is not None:
            data["timeInForce"] = str(time_in_force)
        if post_only == "True":
            data["postOnly"] = True
        if self_trade is not None:
            data["selfTrade"] = str(self_trade)
        if client_order_id is not None:
            data["clientOrderId"] = str(client_order_id)
        
        return self._request("POST", "/v3/orders", data=data)

    def list_orders(self, market_id=None, before=None, after=None, limit=None, status=None):
        data = []
        if market_id is not None:
            data.append("marketId={}".format(market_id))
        if before is not None:
            data.append("before={}".format(before))
        if after is not None:
            data.append("after={}".format(after))
        if limit is not None:
            data.append("limit={}".format(limit))
        if status is not None:
            data.append("status={}".format(status))

        if not data:
            return self._request("GET", "/v3/orders")
        else:
            return self._request("GET", "/v3/orders", "&".join(data))

    def cancel_open_orders(self,  *market_ids):
        data = []
        for m in market_ids:
            data.append("marketId={}".format(m))

        if not data:
            return self._request("DELETE", "/v3/orders")
        else:
            return self._request("DELETE", "/v3/orders", "&".join(data))

    def get_an_order(self, id_):
        return self._request("GET", "/v3/orders/{}".format(id_))

    def cancel_an_order(self, id_):
        return self._request("DELETE", "/v3/orders/{}".format(id_))

    def replace_order(self, id_, price, amount, client_order_id=None):
        data = OrderedDict([
            ("price", str(price)),
            ("amount", str(amount))
        ])
        if client_order_id is not None:
            data["clientOrderId"] = str(client_order_id)

        return self._request("PUT", "/v3/orders/{}".format(id_), data=data)

    def place_and_cancel_order(self, place_order, cancel_order):
        data = OrderedDict([
            ("placeOrder", place_order),
            ("cancelOrder", cancel_order)
        ])

        return self._request("POST", "/v3/batchorders", data=data)

    def get_orders_by_id(self, ids):
        return self._request("GET", "/v3/batchorders/{}".format(",".join(ids)))

    def cancel_orders_by_id(self, ids):
        return self._request("DELETE", "/v3/batchorders/{}".format(",".join(ids)))

    def list_trades(self, market_id=None, order_id=None, before=None,
                    after=None, limit=None):
        data = []
        if market_id is not None:
            data.append("marketId={}".format(market_id))
        if order_id is not None:
            data.append("orderId={}".format(order_id))
        if before is not None:
            data.append("before={}".format(before))
        if after is not None:
            data.append("after={}".format(after))
        if limit is not None:
            data.append("limit={}".format(limit))

        if not data:
            return self._request("GET", "/v3/trades")
        else:
            return self._request("GET", "/v3/trades", "&".join(data))

    def get_trade_by_id(self, id_):
        return self._request("GET", "/v3/trades/{}".format(id_))

    def request_to_withdraw(self, asset_name, amount, to_address=None, account_name=None,
                            account_number=None, bsb_number=None, bank_name=None):
        data = OrderedDict([
            ("assetName", str(asset_name)),
            ("amount", str(amount))
        ])
        if to_address is not None:
            data["toAddress"] = str(to_address)
        if account_name is not None:
            data["accountName"] = str(account_name)
        if account_number is not None:
            data["accountNumber"] = str(account_number)
        if bsb_number is not None:
            data["bsbNumber"] = str(bsb_number)
        if bank_name is not None:
            data["bankName"] = str(bank_name)

        return self._request("POST", "/v3/withdrawals", data=data)

    def list_withdrawals(self, before=None, after=None, limit=None):
        data = []
        if before is not None:
            data.append("before={}".format(before))
        if after is not None:
            data.append("after={}".format(after))
        if limit is not None:
            data.append("limit={}".format(limit))

        if not data:
            return self._request("GET", "/v3/withdrawals")
        else:
            return self._request("GET", "/v3/withdrawals", "&".join(data))

    def get_withdraw_by_id(self, id_):
        return self._request("GET", "/v3/withdrawals/{}".format(id_))
    
    def list_deposits(self, before=None, after=None, limit=None):
        data = []
        if before is not None:
            data.append("before={}".format(before))
        if after is not None:
            data.append("after={}".format(after))
        if limit is not None:
            data.append("limit={}".format(limit))

        if not data:
            return self._request("GET", "/v3/deposits")
        else:
            return self._request("GET", "/v3/deposits", "&".join(data))

    def get_deposit_by_id(self, id_):
        return self._request("GET", "/v3/deposits/{}".format(id_))

    def list_deposits_withdrawals(self, before=None, after=None, limit=None):
        data = []
        if before is not None:
            data.append("before={}".format(before))
        if after is not None:
            data.append("after={}".format(after))
        if limit is not None:
            data.append("limit={}".format(limit))

        if not data:
            return self._request("GET", "/v3/transfers")
        else:
            return self._request("GET", "/v3/transfers", "&".join(data))

    def get_deposits_withdrawals_by_id(self, id_):
        return self._request("GET", "/v3/transfers/{}".format(id_))

    def get_deposit_address(self, asset_name):
        return self._request("GET", "/v3/addresses", "assetName={}".format(asset_name))

    def get_withdrawal_fees(self):
        return self._request("GET", "/v3/withdrawal-fees")
    
    def list_assets(self):
        return self._request("GET", "/v3/assets")

    def get_trading_fees(self):
        return self._request("GET", "/v3/accounts/me/trading-fees")

    def get_withdrawal_limits(self):
        return self._request("GET", "/v3/accounts/me/withdrawal-limits")

    def get_balances(self):
        return self._request("GET", "/v3/accounts/me/balances")

    def get_transactions(self, asset_name=None, before=None, after=None, limit=None):
        data = []
        if asset_name is not None:
            data.append("assetName={}".format(asset_name))
        if before is not None:
            data.append("before={}".format(before))
        if after is not None:
            data.append("after={}".format(after))
        if limit is not None:
            data.append("limit={}".format(limit))

        if not data:
            return self._request("GET", "/v3/accounts/me/transactions")
        else:
            return self._request("GET", "/v3/accounts/me/transactions", "&".join(data))

    def create_new_report(self, type_, format_):
        data = OrderedDict([
            ("type", str(type_)),
            ("format", str(format_))
        ])

        return self._request("POST", "/v3/reports", data=data)

    def get_report_by_id(self, id_):
        return self._request("GET", "/v3/reports/{}".format(id_))

    def get_server_time(self):
        return self._request("GET", "/v3/time")