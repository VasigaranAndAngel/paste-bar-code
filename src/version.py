from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("paste-bar-code")
except PackageNotFoundError:
    __version__ = "0.0.0"
