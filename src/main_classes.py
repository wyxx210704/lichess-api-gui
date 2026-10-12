from PyQt6.QtCore import QtMsgType,qInstallMessageHandler
import sys
from typing import *

P = ParamSpec('P')

class QtMessageFilter:
    def __init__(self, filter_patterns):
        """
        filter_patterns: 要过滤的字符串列表
        """
        self.filter_patterns = filter_patterns
        self.original_handler = None
    
    def handler(self, msg_type, context, message):
        """
        自定义消息处理器
        msg_type: QtMsgType 枚举值
        context: QMessageLogContext 对象
        message: 消息字符串
        """
        # 检查是否包含要过滤的字符串
        if any(pattern in message for pattern in self.filter_patterns):
            return  # 直接忽略，不输出
        
        # 对于不需要过滤的消息，可以重定向到原始处理器或直接输出
        if self.original_handler:
            self.original_handler(msg_type, context, message)
        else:
            # 默认处理方式
            msg_type_map = {
                QtMsgType.QtDebugMsg: "Debug",
                QtMsgType.QtInfoMsg: "Info",
                QtMsgType.QtWarningMsg: "Warning",
                QtMsgType.QtCriticalMsg: "Critical",
                QtMsgType.QtFatalMsg: "Fatal",
            }
            print(f"[{msg_type_map.get(msg_type, 'Unknown')}] {message}", file=sys.stderr)
    
    def install(self):
        """安装过滤器"""
        # 保存原始处理器
        self.original_handler = qInstallMessageHandler(None)
        # 安装自定义处理器
        qInstallMessageHandler(self.handler)
    
    def uninstall(self):
        """卸载过滤器，恢复原始处理器"""
        qInstallMessageHandler(self.original_handler)