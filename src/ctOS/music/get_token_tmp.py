import os
import json
import base64
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs
from requests import post
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("TOKEN_PUBLIC")
CLIENT_SECRET = os.getenv("TOKEN_PRIVATE")
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "user-read-playback-state user-modify-playback-state"
TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".spotify_token.json")


def _basic_auth_header():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")
    return "Basic " + base64.b64encode(auth_string).decode("utf-8")


class _CallbackHandler(BaseHTTPRequestHandler):
    code = None

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        _CallbackHandler.code = query.get("code", [None])[0]
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>You can close this.</h1>")

    def log_message(self, format, *args):
        pass 


def _request_authorization_code():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode(params)
    webbrowser.open(auth_url)

    server = HTTPServer(("127.0.0.1", 8888), _CallbackHandler)
    server.handle_request()
    return _CallbackHandler.code


def _exchange_code_for_tokens(code):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": _basic_auth_header(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    result = post(url, headers=headers, data=data)
    result.raise_for_status()
    return result.json()


def _refresh_access_token(refresh_token):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": _basic_auth_header(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    result = post(url, headers=headers, data=data)
    result.raise_for_status()
    return result.json()


def _save_tokens(tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)


def _load_tokens():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE) as f:
        return json.load(f)


def get_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("TOKEN_PUBLIC et TOKEN_PRIVATE doivent etre definis dans l'environnement")

    tokens = _load_tokens()

    if tokens and "refresh_token" in tokens:
        new_tokens = _refresh_access_token(tokens["refresh_token"])
        new_tokens.setdefault("refresh_token", tokens["refresh_token"])
        _save_tokens(new_tokens)
        return new_tokens["access_token"]

    code = _request_authorization_code()
    if not code:
        raise RuntimeError("Aucun code recu, autorisation echouee")

    tokens = _exchange_code_for_tokens(code)
    _save_tokens(tokens)
    return tokens["access_token"]