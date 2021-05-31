import json
import pprint
import traceback

from api.saxo import Session
import sched, time

CONFIG_PATH = 'config.json'

config = json.loads(open(CONFIG_PATH, 'r').read())
APP_KEY = config.get('app_key')
AUTH_ENDPOINT = config.get('auth_endpoint')
TOKEN_ENDPOINT = config.get('token_endpoint')
SECRET = config.get('secret')
STRATEGY = config.get('strategy')


s = sched.scheduler(time.time, time.sleep)

def getOrders(sc):
    print("Doing stuff...")
    orders = access.get("port/v1/orders/me",
                        FieldGroups="DisplayAndFormat")

    pp.pprint(orders)
    s.enter(5, 1, getOrders, (sc,))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    a = 1
    access = Session(APP_KEY, AUTH_ENDPOINT, TOKEN_ENDPOINT, SECRET)
    print("[Authorised SAXO]")

    pp = pprint.PrettyPrinter(indent=2)

    try:
        out = access.get("ref/v1/instruments", KeyWords=STRATEGY['ticker'], AssetTypes='FxSpot')

        pp.pprint(out)

        identifier = out["Data"][0]["Identifier"]

        out = access.get("trade/v1/infoprices/list", Uics=identifier, AssetType='FxSpot', Amount=STRATEGY["amount"],
                         FieldGroups="DisplayAndFormat,Quote")

        pp.pprint(out)

        if STRATEGY["type"] == "priceLimit":

            #s.enter(5, 1, getOrders, (s,))
            #s.run()

            order = access.post("trade/v2/orders", post={
                "Uic": identifier,
                "BuySell": "Buy",
                "AssetType": "FxSpot",
                "Amount": STRATEGY["amount"],
                "OrderPrice": STRATEGY["buyPrice"],
                "OrderType": "Limit",
                "OrderRelation": "StandAlone",
                "ManualOrder": "true",
                "OrderDuration": {
                    "DurationType": "GoodTillCancel"
                }
            })

            pp.pprint(order)

    except:
        print("\n** EXCEPTION **\n", traceback.format_exc(), "\n")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
