# ccxt-webhook-trader

Trade cryptocurrencies using the CCXT library via webhooks. </br>
Now only test WORKING for Binance USD-M future.

---
## Requirements
* Python 3.7+
* <a href="https://github.com/tiangolo/fastapi" target="_blank">FastAPI</a> : a framework handles http requests.
* <a href="https://github.com/ccxt/ccxt" target="_blank">CCXT Library</a> : connect and trade with cryptocurrency exchanges.

If you need to deploy in AWS Lambda functions.

* <a href="https://github.com/jordaneremieff/mangum" target="_blank">Mangum</a> : an adapter for running ASGI applications in AWS Lambda to handle Function URL.

Not necessary to deploy. Just for local testing.
* <a href="https://github.com/encode/uvicorn" target="_blank">Uvicorn</a> : an ASGI web server.
---

## Quickstart

Recommand create a <a href="https://docs.python.org/3/tutorial/venv.html" target="_blank">virtual environment</a>.

### 1. Install using `pip`:
```shell
$ pip install -r requirments.txt
```

### 2. Setting parameters
#### method 1 (maybe more security):
Setting all parameters in OS environment variables.
* `TESTMODE`: switch to testnet. if not set the default value is `False`.
* `IP_ALLOW`: for whitelist IP.
* `WEBHOOK_TOKEN`: some random key you generate.
* `EXCHANGE`: see ccxt library <a href="https://docs.ccxt.com/en/latest/exchange-markets.html" target="_blank">support list</a>.
* `API_KEY`: your exchange api key.
* `API_SECRET`: your exchange api secret.
* `API_PASSWORD`: some exchange need.

#### method 2:
* Edit `account` and `iplist` in the `setting.py` file. ( `testnet` for testing ) </br>
Setting `TESTMODE` in OS environment variables to switch to testnet. if not set the default value is `False`.

method 1 has higher priority than method 2. </br>
For all IP allow can set to `['*']` ( If `TESTMODE` is `True` that `IP_ALLOW` always set to `['*']`)

### 3. Runing `uvicorn` server:
```shell
$ uvicorn --host localhost main:fast_app
```
Like this on your terminal:
```shell
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```
### 4. Using HTTP request methods `POST` to `http://localhost:8000/webhook` with JSON:

Below is an order to buy 0.5 BTC at market price. `PRICE` has no effect.
```json
{
    "TOKEN": "test1234qwer",
    "SYMBOL": "BTCUSDT",
    "SIDE": "buy",
    "PRICE": 12345,
    "QUANTITY": 0.5,
}
```

Additional parameters are as follows.</br>
* `ORDER_TYPE`: Change order type.  By default order type is `market`
* `REDUCEONLY`: The order is reduce position only or not. By default is `False`
* `LEVERAGE` : Change leverage ratio. Default will not change.
* `COMMENT` : Any comment you wanna.

Here is an order to buy 0.8 BTC with a limit price of 24680. And change leverage ratio to 5x.
```json
{
    "TOKEN": "test1234qwer",
    "SYMBOL": "BTCUSDT",
    "SIDE": "buy",
    "PRICE": 24680,
    "QUANTITY": 0.8,
    "ORDER_TYPE": "limit",
    "REDUCEONLY": False,
    "LEVERAGE": 5,
    "COMMENT": "test"
}
```
