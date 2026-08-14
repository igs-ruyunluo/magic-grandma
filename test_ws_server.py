# test_ws_server.py(放在專案根目錄,純測試用)
import os
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from app import application

port = int(os.environ.get("PORT", 8000))
server = pywsgi.WSGIServer(("0.0.0.0", port), application, handler_class=WebSocketHandler)
print("8000port")
server.serve_forever()