from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import ctypes
from ctypes import wintypes, byref
import win32api
import win32con

from .costants import GENERAL_PATH
dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)

# DWM 常量
DWMWA_SYSTEMBACKDROP_TYPE = 38
DWMWA_WINDOW_CORNER_PREFERENCE = 33

DWMSBT_DISABLE = 1
DWMSBT_MAINWINDOW = 2          # Mica
DWMSBT_TRANSIENTWINDOW = 3     # Acrylic
DWMSBT_TABBEDWINDOW = 4        # MicaAlt

DWMWCP_DEFAULT = 0
DWMWCP_ROUND = 2
DWMWCP_ROUNDSMALL = 3


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

def apply_style(window:QMainWindow):
    if True:#check_win11_version()[0]:
        window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        qwidget_set_dwm_system_backdrop(window)
        window.setStyleSheet(open(GENERAL_PATH + 'style.qss','r',encoding='utf-8',errors='ignore').read())