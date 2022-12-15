import json, logging

def symbolcheck(symbol):
    syidx = 0
    try:
        syidx = symbol.index('USDT')
    except:
        try:
            print("USDT not found. Try to use BUSD.")
            syidx = symbol.index('BUSD')
        except:
            logging.error("USDT BUSD both not found.")
            return Exception
    symbol = symbol[:syidx]+'/'+symbol[syidx:syidx+4]
    return symbol

def fetchpos(ex, symbol):
    if ex.has['fetchPositions']:
        openorder = ex.fetchPositions([symbol])
        od = json.dumps(openorder[0])
        od = json.loads(od)
        currentPos = float(od['info']['positionAmt'])
        print('new '+symbol+' position:'+od['info']['positionAmt'])
    else:
        print('exchange not support "fetchPositions" function')