# webhook-fastapi-ccxt-lambda
Trade cryptocurrencies using the CCXT library via webhooks. Can also be deployed to AWS Lambda Functions.

---
## Requirements
* Python 3.7+
* <a href="https://github.com/tiangolo/fastapi" target="_blank">FastAPI</a> : handle http requests.
* <a href="https://github.com/ccxt/ccxt" target="_blank">CCXT Library</a> : connect and trade with cryptocurrency exchanges.
* <a href="https://github.com/jordaneremieff/mangum" target="_blank">Mangum</a> : an adapter for running ASGI applications in AWS Lambda to handle Function URL.

Not necessary to deploy. Just for local testing.
* <a href="https://github.com/encode/uvicorn" target="_blank">Uvicorn</a> : an ASGI web server.
---

## Quickstart

Recommand create a <a href="https://docs.python.org/3/tutorial/venv.html" target="_blank">virtual environment</a>.

Install using `pip`:
```shell
$ pip install -r requirments.txt
```
Edit `setting.py` ( `testnet.py` for testing ) to connect exchange. Setting OS environ `IP_ALLOW` for whitelist IP and `TESTMODE` for switch loading from setting or testnet.

For all IP allow can set to `["*"]`

Turn off testnet `False`

Runing `uvicorn` server:
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
Using HTTP request methods `POST` to `http://localhost:8000/webhook` with JSON:
```json
{
    "TOKEN": "test1234qwer",
    "SYMBOL": "BTCUSDT",
    "SIDE": "buy",
    "ORDER_TYPE": "limit",
    "PRICE": 24680,
    "QUANTITY": 0.5,
    "REDUCEONLY": false,
    "LEVERAGE": 5,
    "COMMENT": "test"
}
```
Now only test WORKING for Binance USD-M future.
