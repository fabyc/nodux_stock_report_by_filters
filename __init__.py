# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .reports import *

def register():
    Pool.register(
        PrintReportStockStart,
        module='nodux_stock_report_by_filters', type_='model')
    Pool.register(
        PrintReportStock,
        module='nodux_stock_report_by_filters', type_='wizard')
    Pool.register(
        ReportStock,
        module='nodux_stock_report_by_filters', type_='report')
