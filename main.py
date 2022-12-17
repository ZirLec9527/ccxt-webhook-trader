import ccxt
import logging
import os
import my_lib as myfc
import setting, testnet
from ast import literal_eval
from fastapi import FastAPI, Response, Request, status
from mangum import Mangum
from pydantic import BaseModel

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%c')
class post_format(BaseModel):
    TOKEN : str
    SYMBOL : str
    SIDE : str
    ORDER_TYPE : str
    PRICE : float
    QUANTITY : float
    REDUCEONLY : bool
    LEVERAGE : int
    COMMENT : str

allowip = literal_eval(os.environ.get('IP_TV'))
test = literal_eval(os.environ.get('TESTMODE'))
if test == True:
    tkn = testnet.WEBHOOK_TOKEN
    exid = testnet.EXCHANGE
    key = testnet.API_KEY
    secret = testnet.API_SECRET
    pwd = testnet.PASSWORD
else:
    tkn = setting.WEBHOOK_TOKEN
    exid = setting.EXCHANGE
    key = setting.API_KEY
    secret = setting.API_SECRET
    pwd = setting.PASSWORD

exchange_class = getattr(ccxt, exid)
exchange = exchange_class({
    'apiKey': key,
    'secret': secret,
    'password': pwd,
    'options': {
        'fetchCurrencies': False,
        'defaultType': 'future'
    }
})
exchange.set_sandbox_mode(test)
fast_app = FastAPI()

@fast_app.middleware("http")
async def test(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    hostip = request.client.host
    if hostip in allowip:
        response = await call_next(request)
        return response
    else:
        logging.critical('IP error: %s', hostip)
        return response

@fast_app.post("/webhook")
def read_webhook(
    signal: post_format,
    response: Response,
):
    if signal:
        if signal.TOKEN != tkn:
            logging.critical('TOKEN error: %s', signal.TOKEN)
            response.status_code = 401
            return {"msg": "check your webhook setting"}

        trade_symbol = myfc.symbolcheck(signal.SYMBOL)
        trade_price = signal.PRICE
        trade_quantity = signal.QUANTITY
        
        if signal.LEVERAGE > 0:
            try:
                exchange.set_leverage(signal.LEVERAGE, trade_symbol)
            except Exception as e:
                logging.error('LEVERAGE:%d  SYMBOL:%s - %s', signal.LEVERAGE, trade_symbol, str(e))
                response.status_code = 422
                return {"msg": "check your webhook SYMBOL and LEVERAGE"}

        params = {
            # 'postOnly' : True,
            'reduceOnly': signal.REDUCEONLY,
        }
        try:
            star_order = exchange.create_order(
                trade_symbol,
                signal.ORDER_TYPE,
                signal.SIDE,
                trade_quantity,
                trade_price,
                params)
            response.status_code = 201
            return {"msg": "order success"}
        except Exception as e:
            logging.error('SYMBOL:%s  TYPE:%s  SIDE/AMOUNT:%s/%d  PRICE:%.3f - %s', 
                trade_symbol, signal.ORDER_TYPE, signal.SIDE, trade_quantity, trade_price, str(e))
            response.status_code = 400
            return {"msg": "order fail"}
    else:
        logging.critical("POST error")
        response.status_code = 400
        return {"msg": "check your webhook JSON"}

handler = Mangum(fast_app, lifespan="off")