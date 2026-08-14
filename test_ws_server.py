# test_ws_server.py(放在專案根目錄,純測試用)
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from app import application

server = pywsgi.WSGIServer(("0.0.0.0", 8000), application, handler_class=WebSocketHandler)
print("8000port")
server.serve_forever()