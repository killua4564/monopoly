from .lands import BaseLand, Land, Ocean
from .stocks import BaseStock, ETF, Stock

Land.update_forward_refs(Stock=Stock)
Stock.update_forward_refs(Land=Land)
