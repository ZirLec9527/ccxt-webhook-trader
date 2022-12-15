import logging
import setting, testnet
import ccxt
import my_lib as myfc
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from mangum import Mangum

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

test = 0 # True or False
if test == True:
    pwd = testnet.WEBHOOK_TOKEN
    exid = testnet.EXCHANGE
    key = testnet.API_KEY
    secret = testnet.API_SECRET
else:
    pwd = setting.WEBHOOK_TOKEN
    exid = setting.EXCHANGE
    key = setting.API_KEY
    secret = setting.API_SECRET

exchange_class = getattr(ccxt, exid)
exchange = exchange_class({
    'apiKey': key,
    'secret': secret,
    'options': {
        'fetchCurrencies': False,
        'defaultType': 'future'
    }
})
exchange.set_sandbox_mode(test)

fast_app = FastAPI()

@fast_app.post("/webhook")
def read_webhook(signal: post_format, response: Response):
    if signal:
        if signal.TOKEN != pwd:
            logging.critical("TOKEN error")
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return response, {"msg": "check your webhook setting"}

        trade_symbol = myfc.symbolcheck(signal.SYMBOL)
        trade_price = signal.PRICE
        trade_quantity = signal.QUANTITY
        
        params = {
            # 'postOnly' : True,
            'reduceOnly': signal.REDUCEONLY,
        }        
        try:
            exchange.set_leverage(signal.LEVERAGE, trade_symbol)
        except Exception as e:
            logging.error('LEVERAGE:%d  SYMBOL:%s - %s', signal.LEVERAGE, trade_symbol, str(e))
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            return response,{"msg": "check your webhook SYMBOL and LEVERAGE"}

        try:
            star_order = exchange.create_order(
                trade_symbol,
                signal.ORDER_TYPE,
                signal.SIDE,
                trade_quantity,
                trade_price,
                params)
        except Exception as e:
            logging.error('SYMBOL:%s  TYPE:%s  SIDE/AMOUNT:%s/%d  PRICE:%d - %s', 
                trade_symbol, signal.ORDER_TYPE, signal.SIDE, trade_quantity, trade_price, str(e))
            response.status_code = status.HTTP_400_BAD_REQUEST
            return response,{"msg": "order fail"}

        # logging.info('SYMBOL:%s  TYPE:%s  ID:%s  SIDE/AMOUNT:%s/%d  PRICE:%d', 
        #     trade_symbol, signal.ORDER_TYPE, str(star_order['id']), str(star_order['side']), star_order['amount'], star_order['average'])
        response.status_code = status.HTTP_201_CREATED
        return response,{"msg": "order success"}
    else:
        logging.critical("POST error")
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response,{"msg": "check your webhook JSON"}

handler = Mangum(fast_app, lifespan="off")