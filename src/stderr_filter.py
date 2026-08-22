# src/stderr_filter.py
import sys
import re

class StderrFilter:
    """全局stderr过滤器"""
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, filter_strings=None, enabled=True):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        self.filter_strings = filter_strings or []
        self.enabled = enabled
        self.original_stderr = sys.stderr
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.filter_strings
        ]
    
    def write(self, text):
        if self.enabled and text:
            for pattern in self.compiled_patterns:
                if pattern.search(text):
                    return  # 过滤掉
        self.original_stderr.write(text)
        self.original_stderr.flush()
    
    def flush(self):
        if hasattr(self.original_stderr, 'flush'):
            self.original_stderr.flush()
    
    def install(self):
        """安装过滤器到全局"""
        sys.stderr = self
        return self
    
    def uninstall(self):
        """卸载过滤器"""
        sys.stderr = self.original_stderr

# 创建全局单例
global_filter = StderrFilter([
    r'QThread: Destroyed while thread .* is still running',
    r'libpng warning: iCCP: known incorrect sRGB profile',
], True).install()