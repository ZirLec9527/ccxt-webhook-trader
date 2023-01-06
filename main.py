import ccxt.async_support as ccxt
import logging
import os
from fastapi import FastAPI, Response, Request, HTTPException
from mangum import Mangum
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO,  format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%c')
logger = logging.getLogger('trader')

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

test = os.environ.get('TESTMODE', False)
if test == True:
    from setting import testnet as apiconf
    allowip = ['*']
else:
    from setting import account as apiconf
    from setting import iplist
    allowip = os.environ.get('IP_ALLOW', iplist)

apitoken = os.environ.get('WEBHOOK_TOKEN', apiconf['WEBHOOK_TOKEN'])
apiexchange = os.environ.get('EXCHANGE', apiconf['EXCHANGE'])
apikey = os.environ.get('API_KEY', apiconf['API_KEY'])
apisecret = os.environ.get('API_SECRET', apiconf['API_SECRET'])
apipwd = os.environ.get('API_PASSWORD', apiconf['API_PASSWORD'])

exchange_class = getattr(ccxt, apiexchange)
exchange = exchange_class({
    'apiKey': apikey,
    'secret': apisecret,
    'password': apipwd,
    'options': {
        'enableRateLimit': True,
        'fetchCurrencies': False,
        'defaultType': 'future' # spot, margin, future, or swap
    }
})
exchange.set_sandbox_mode(test)
fast_app = FastAPI()

def symbolfilter(symbol):
    syidx = 0
    try:
        syidx = symbol.index('USDT')
    except:
        try:
            logger.warning('USDT not found. Try to use BUSD.')
            syidx = symbol.index('BUSD')
        except:
            logger.error(f'USDT BUSD both not found. {symbol}')
            raise NameError(symbol)
    symbol = symbol[:syidx+4]
    return symbol

@fast_app.middleware('http') # before request
async def pre_process(request: Request, call_next):    
    hostip = request.client.host
    '''
    ms azure method
    hostip = request.headers.get('client-ip')
    hostip = hostip[:hostip.index(':')]
    '''
    if (hostip in allowip) or (allowip == ['*']):
        response = await call_next(request)
    else:
        logger.critical(f'IP error: {hostip}')
        response = Response(status_code=403)
    return response

@fast_app.post("/webhook", status_code=201)
async def read_webhook(signal: post_format):
    if signal.TOKEN != apitoken:
        logger.critical(f'mismatch {signal.TOKEN=}')
        raise HTTPException(status_code=401, detail='check your webhook setting')
    
    # logger.info(f'webhook signal: {signal}')
    trade_symbol = symbolfilter(signal.SYMBOL)
    trade_price = signal.PRICE
    trade_quantity = signal.QUANTITY
    
    if signal.LEVERAGE > 0:
        try:
            setlever = await exchange.set_leverage(signal.LEVERAGE, trade_symbol)
        except Exception as e:
            logger.error(f'LEVERAGE:{signal.LEVERAGE} SYMBOL:{trade_symbol} - {e}')
            raise HTTPException(status_code=422, detail='leverage error')
        else:
            logger.info(setlever)

    order_params = {'reduceOnly': signal.REDUCEONLY}
    try:
        star_order = await exchange.create_order(
            trade_symbol,
            signal.ORDER_TYPE,
            signal.SIDE,
            trade_quantity,
            trade_price,
            order_params
            )
    except Exception as e:
        logger.error('SYMBOL:%s  TYPE:%s  SIDE/AMOUNT:%s/%d  PRICE:%.3f - %s', 
            trade_symbol, signal.ORDER_TYPE, signal.SIDE, trade_quantity, trade_price, str(e))
        raise HTTPException(status_code=422, detail='order failed')
    else:
        logging.info('SYMBOL:%s  TYPE:%s  ID:%s  SIDE/AMOUNT:%s/%d  PRICE:%.3f', 
            star_order['symbol'], star_order['type'], star_order['id'], star_order['side'], star_order['amount'], star_order['price'])
        return {"order success"}

handler = Mangum(fast_app, lifespan="off")
