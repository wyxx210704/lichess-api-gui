from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import ctypes
from ctypes import wintypes, byref
import win32api
import win32con
import base64
import hashlib
import secrets
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

from .costants import GENERAL_PATH
dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)

DWMWA_SYSTEMBACKDROP_TYPE = 38
DWMWA_WINDOW_CORNER_PREFERENCE = 33

DWMSBT_DISABLE = 1
DWMSBT_MAINWINDOW = 2          # Mica
DWMSBT_TRANSIENTWINDOW = 3     # Acrylic
DWMSBT_TABBEDWINDOW = 4        # MicaAlt

DWMWCP_DEFAULT = 0
DWMWCP_ROUND = 2
DWMWCP_ROUNDSMALL = 3

AUTH_URL = "https://lichess.org/oauth"
TOKEN_URL = "https://lichess.org/api/token"

class MARGINS(ctypes.Structure):
    _fields_ = [
        ("cxLeftWidth", ctypes.c_int),
        ("cxRightWidth", ctypes.c_int),
        ("cyTopHeight", ctypes.c_int),
        ("cyBottomHeight", ctypes.c_int),
    ]

def check_win11_version():
    try:
        # 打开注册表
        key = win32api.RegOpenKeyEx(
            win32con.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
            0,
            win32con.KEY_READ
        )
        
        product_name = win32api.RegQueryValueEx(key, "ProductName")[0]
        build = int(win32api.RegQueryValueEx(key, "CurrentBuild")[0])
        display_ver = win32api.RegQueryValueEx(key, "DisplayVersion")[0]
        
        win32api.RegCloseKey(key)
        
        if "Windows 11" in product_name and build >= 22621:
            return True, f"{product_name} {display_ver}"
        return False, product_name
        
    except Exception as e:
        return False, str(e)

def qwidget_set_dwm_system_backdrop(widget: QWidget, backdrop_type: int = DWMSBT_TRANSIENTWINDOW) -> int:
    if not widget.isWindow():
        raise RuntimeError("传入必须是顶层窗口(isWindow()==True)，子控件没有顶层HWND，无法使用DWM SystemBackdrop")

    # 确保窗口已经创建原生Win32句柄，最好在 show() 之后调用
    hwnd_val = widget.winId()
    hwnd = wintypes.HWND(int(hwnd_val))

    # 1. 扩展Frame到整个客户区 (-1,-1,-1,-1)，这一步必不可少，否则只有标题栏生效
    margins = MARGINS(-1, -1, -1, -1)
    hr = dwmapi.DwmExtendFrameIntoClientArea(hwnd, byref(margins))
    if hr != 0:
        return hr

    # 2. 设置 SystemBackdropType
    val_backdrop = ctypes.c_int(backdrop_type)
    hr = dwmapi.DwmSetWindowAttribute(
        hwnd,
        DWMWA_SYSTEMBACKDROP_TYPE,
        byref(val_backdrop),
        ctypes.sizeof(val_backdrop)
    )
    if hr != 0:
        return hr

    return hr

#-------------------------------------------以下为公开函数--------------------------------------------------

def apply_style(window:QWidget):
    if True:#check_win11_version()[0]:
        window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        qwidget_set_dwm_system_backdrop(window)
        window.setStyleSheet(open(GENERAL_PATH + 'style.qss','r',encoding='utf-8',errors='ignore').read())

def login_with_lichess(
    scope: str = "",
    client_id: str = "my-local-app",
    port: int = 8080,
    timeout: float = 300,
) -> dict:
    """
    阻塞直到用户在浏览器中完成 Lichess 授权，返回 token 字典：
    {"access_token": ..., "token_type": ..., "expires_in": ...}
    """

    # ---------- 1. 生成 PKCE 参数 ----------
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b"=").decode()
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    state = secrets.token_urlsafe(16)
    redirect_uri = f"http://localhost:{port}/callback"

    # ---------- 2. 用容器在线程间传递结果 ----------
    result_box: dict = {}
    done_event = threading.Event()

    # ---------- 3. 定义回调 HTTP handler ----------
    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return

            qs = urllib.parse.parse_qs(parsed.query)
            returned_state = qs.get("state", [""])[0]
            code = qs.get("code", [""])[0]
            error = qs.get("error", [""])[0]

            # CSRF 校验
            if returned_state != state:
                result_box["error"] = "state mismatch (CSRF?)"
            elif error:
                result_box["error"] = f"authorization denied: {error}"
            elif not code:
                result_box["error"] = "no code returned"
            else:
                result_box["code"] = code

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(open(
                GENERAL_PATH + 'login_success.html',
                'r',
                encoding='utf-8',
            ).read().encode(
                encoding='utf-8',
            ))
            done_event.set()

        def log_message(self, *args):  # 静音
            pass

    # ---------- 4. 启动临时服务器 ----------
    server = HTTPServer(("127.0.0.1", port), CallbackHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    # ---------- 5. 打开浏览器 ----------
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
        "state": state,
    }
    if scope:
        params["scope"] = scope

    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    webbrowser.open(url)

    # ---------- 6. 阻塞等待回调 ----------
    try:
        if not done_event.wait(timeout=timeout):
            raise TimeoutError("等待用户授权超时")
    finally:
        server.shutdown()

    if "error" in result_box:
        raise RuntimeError(result_box["error"])

    # ---------- 7. 用 code 换 token ----------
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": result_box["code"],
            "code_verifier": code_verifier,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()