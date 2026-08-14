import os
import falcon
from resources.game_ws import handle_game_round

falcon_app = falcon.App()
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
falcon_app.add_static_route('/', static_path)

class IndexResource:
    def on_get(self, req, resp):
        resp.content_type = 'text/html'
        index_path = os.path.join(static_path, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            resp.text = f.read()

falcon_app.add_route('/', IndexResource())

def application(environ, start_response):
    ws = environ.get("wsgi.websocket")
    if ws:
        handle_game_round(ws)
        return
    else:
        
        return falcon_app(environ, start_response)