"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from .base import *

DEBUG = False


try:
    from .local import *
except ImportError:
    pass

