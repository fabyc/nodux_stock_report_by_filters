#This file is part of Tryton. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms
from trytond.model import ModelView, fields, ModelSQL
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.report import Report
from decimal import Decimal
import datetime
from trytond.wizard import Wizard, StateView, StateAction, StateTransition, Button

__all__ = ['PrintReportStockStart', 'PrintReportStock', 'ReportStock']
__metaclass__ = PoolMeta

_NOBODEGAS = [
    ('no_1', '1 Bodega'),
    ('no_2', '2 Bodegas'),
    ('no_3', '3 Bodegas'),
    ('no_4', '4 Bodegas'),
    ('no_5', '5 Bodegas'),
    ('no_6', '6 Bodegas'),
]

class PrintReportStockStart(ModelView):
    'Print Report Stock Start'
    __name__ = 'nodux_stock_report_by_filters.print_report_stock.start'

    todas_bodegas = fields.Boolean('Todas')

    no_bodegas = fields.Selection(_NOBODEGAS, 'No. de Bodegas', help="Numero de bodegas para reporte inventario")

    bodega = fields.Many2One('stock.location', 'Location', domain=[('type', '=', 'storage')], states={
        'required': Eval('no_bodegas').in_(['no_1','no_2','no_3', 'no_4', 'no_5', 'no_6']),
    })

    bodega2 = fields.Many2One('stock.location', 'Location 2', domain=[('type', '=', 'storage')], states={
        'invisible': Eval('no_bodegas').in_(['no_1']),
        'required': Eval('no_bodegas').in_(['no_2', 'no_3', 'no_4', 'no_5', 'no_6']),
    })
    bodega3 = fields.Many2One('stock.location', 'Location 3', domain=[('type', '=', 'storage')], states={
        'invisible': Eval('no_bodegas').in_(['no_1', 'no_2']),
        'required': Eval('no_bodegas').in_(['no_3', 'no_4', 'no_5', 'no_6']),
    })
    bodega4 = fields.Many2One('stock.location', 'Location 4', domain=[('type', '=', 'storage')], states={
        'invisible': Eval('no_bodegas').in_(['no_1', 'no_2', 'no_3']),
        'required' : Eval('no_bodegas').in_(['no_4', 'no_5', 'no_6']),
    })
    bodega5 = fields.Many2One('stock.location', 'Location 5', domain=[('type', '=', 'storage')], states={
        'invisible': Eval('no_bodegas').in_(['no_1', 'no_2', 'no_3', 'no_4']),
        'required' : Eval('no_bodegas').in_(['no_5', 'no_6']),
    })
    bodega6 = fields.Many2One('stock.location', 'Location 6', domain=[('type', '=', 'storage')], states={
        'invisible': Eval('no_bodegas').in_(['no_1', 'no_2', 'no_3', 'no_4', 'no_5']),
        'required' : Eval('no_bodegas').in_(['no_6']),
    })

    todos_stock = fields.Boolean('Todos', states={
        'readonly': (Eval('mayor', True)) | (Eval('menor', True)) | (Eval('igual', True)) | (Eval('mayor_igual', True)),
    })

    mayor = fields.Boolean('> 0', help="Stock mayor a cero", states={
        'readonly':(Eval('todos_stock', True)) | (Eval('menor', True)) | (Eval('igual', True)) | (Eval('mayor_igual', True)),
    })

    menor = fields.Boolean('< 0', help="Stock menor a cero", states={
        'readonly':(Eval('todos_stock', True)) | (Eval('mayor', True)) |  (Eval('igual', True)) | (Eval('mayor_igual', True)),
    })

    igual = fields.Boolean('= 0', help="Stock igual a cero", states={
        'readonly':(Eval('todos_stock', True)) | (Eval('menor', True)) |  (Eval('mayor', True)) | (Eval('mayor_igual', True)),
    })

    mayor_igual = fields.Boolean('> = 0', help="Stock mayor o igual a cero", states={
        'readonly':(Eval('todos_stock', True)) | (Eval('menor', True)) |  (Eval('igual', True)) | (Eval('mayor', True)),
    })

    todos_precio = fields.Boolean('Todos', states={
        'readonly': (Eval('mayor_precio', True)) | (Eval('menor_precio', True)),
    })

    mayor_precio = fields.Boolean('Precio > 0', help="Precio mayor a cero", states={
        'readonly':(Eval('todos_precio', True)) | (Eval('menor_precio', True)),
    })

    menor_precio = fields.Boolean('Precio =< 0', help="Precio menor-igual a cero",  states={
        'readonly':(Eval('todos_precio', True)) | (Eval('mayor_precio', True)),
    })

    todos_iva = fields.Boolean ('Todos', states={
        'readonly':(Eval('sin_iva', True)) | (Eval('con_iva', True)),
    })

    sin_iva = fields.Boolean('Sin IVA', states={
        'readonly':(Eval('todos_iva', True)) | (Eval('con_iva', True)),
    })

    con_iva = fields.Boolean('Con IVA',  states={
        'readonly':(Eval('todos_iva', True)) | (Eval('sin_iva', True)),
    })

    todos_activo = fields.Boolean('Todos', states={
        'readonly':(Eval('activo', True)) | (Eval('baja', True))
    })

    activo = fields.Boolean('Activos', states={
        'readonly':(Eval('todos_activo', True)) | (Eval('baja', True)),
    })

    baja = fields.Boolean('Baja', states={
        'readonly':(Eval('todos_activo', True)) | (Eval('activo', True)),
    })

    date = fields.Date('Date', required=True)

    company = fields.Many2One('company.company', 'Company', required=True)

    @staticmethod
    def default_no_bodegas():
        return "no_1"

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_mayor():
        return True

    @staticmethod
    def default_mayor_precio():
        return True

    @staticmethod
    def default_todos_iva():
        return True

    @staticmethod
    def default_activo():
        return True

    def on_change_todos_stock(self):
        res= {}
        if self.todos_stock:
            if self.todos_stock == True:
                res['mayor'] = False
                res['menor'] = False
                res['igual'] = False
                res['mayor_igual'] = False
        return res

    def on_change_mayor(self):
        res= {}
        if self.mayor:
            if self.mayor == True:
                res['todos_stock'] = False
                res['menor'] = False
                res['igual'] = False
                res['mayor_igual'] = False
        return res

    def on_change_menor(self):
        res= {}
        if self.menor:
            if self.menor == True:
                res['todos_stock'] = False
                res['mayor'] = False
                res['igual'] = False
                res['mayor_igual'] = False
        return res

    def on_change_igual(self):
        res= {}
        if self.igual:
            if self.igual == True:
                res['todos_stock'] = False
                res['mayor'] = False
                res['menor'] = False
                res['mayor_igual'] = False
        return res

    def on_change_mayor_igual(self):
        res= {}
        if self.mayor_igual:
            if self.mayor_igual == True:
                res['todos_stock'] = False
                res['mayor'] = False
                res['menor'] = False
                res['igual'] = False
        return res

    def on_change_todos_precio(self):
        res= {}
        if self.todos_precio:
            if self.todos_precio == True:
                res['mayor_precio'] = False
                res['menor_precio'] = False
        return res

    def on_change_mayor_precio(self):
        res= {}
        if self.mayor_precio:
            if self.mayor_precio == True:
                res['todos_precio'] = False
                res['menor_precio'] = False
        return res

    def on_change_menor_precio(self):
        res= {}
        if self.menor_precio:
            if self.menor_precio == True:
                res['todos_precio'] = False
                res['mayor_precio'] = False
        return res

    def on_change_todos_iva(self):
        res= {}
        if self.todos_iva:
            if self.todos_iva == True:
                res['con_iva'] = False
                res['sin_iva'] = False
        return res

    def on_change_con_iva(self):
        res= {}
        if self.con_iva:
            if self.con_iva == True:
                res['todos_iva'] = False
                res['sin_iva'] = False
        return res

    def on_change_sin_iva(self):
        res= {}
        if self.sin_iva:
            if self.sin_iva == True:
                res['todos_iva'] = False
                res['con_iva'] = False
        return res

    def on_change_todos_activo(self):
        res= {}
        if self.todos_activo:
            if self.todos_activo == True:
                res['activo'] = False
                res['baja'] = False
        return res

    def on_change_activo(self):
        res= {}
        if self.activo:
            if self.activo == True:
                res['todos_activo'] = False
                res['baja'] = False
        return res

    def on_change_baja(self):
        res={}
        if self.baja:
            if self.baja == True:
                res['todos_activo'] = False
                res['activo'] = False
        return res

class PrintReportStock(Wizard):
    'Print Report Stock'
    __name__ = 'nodux_stock_report_by_filters.print_report_stock'
    start = StateView('nodux_stock_report_by_filters.print_report_stock.start',
        'nodux_stock_report_by_filters.print_report_stock_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Print', 'print_', 'tryton-print', default=True),
            ])
    print_ = StateAction('nodux_stock_report_by_filters.report_stock')

    def do_print_(self, action):
        if self.start.no_bodegas:
            no_bodegas = self.start.no_bodegas
        else:
            no_bodegas = None

        if self.start.bodega:
            bodega = self.start.bodega.id
        else:
            bodega = None

        if self.start.bodega2:
            bodega2 = self.start.bodega2.id
        else:
            bodega2 = None

        if self.start.bodega3:
            bodega3 = self.start.bodega3.id
        else:
            bodega3 = None

        if self.start.bodega4:
            bodega4 = self.start.bodega4.id
        else:
            bodega4 = None

        if self.start.bodega5:
            bodega5 = self.start.bodega5.id
        else:
            bodega5 = None

        if self.start.bodega6:
            bodega6 = self.start.bodega6.id
        else:
            bodega6 = None

        if self.start.todos_stock:
            todos_stock = self.start.todos_stock
        else:
            todos_stock = False
        if self.start.mayor:
            mayor = self.start.mayor
        else:
            mayor = False
        if self.start.menor:
            menor = self.start.menor
        else:
            menor = False
        if self.start.igual:
            igual = self.start.igual
        else:
            igual = False
        if self.start.mayor_igual:
            mayor_igual = self.start.mayor_igual
        else:
            mayor_igual = False
        if self.start.todos_precio:
            todos_precio = self.start.todos_precio
        else:
            todos_precio = False
        if self.start.mayor_precio:
            mayor_precio = self.start.mayor_precio
        else:
            mayor_precio = False
        if self.start.menor_precio:
            menor_precio = self.start.menor_precio
        else:
            menor_precio = False
        if self.start.todos_iva:
            todos_iva = self.start.todos_iva
        else:
            todos_iva = False
        if self.start.sin_iva:
            sin_iva = self.start.sin_iva
        else:
            sin_iva = False
        if self.start.con_iva:
            con_iva = self.start.con_iva
        else:
            con_iva = False
        if self.start.todos_activo:
            todos_activo = self.start.todos_activo
        else:
            todos_activo = False
        if self.start.activo:
            activo = self.start.activo
        else:
            activo = False
        if self.start.baja:
            baja = self.start.baja
        else:
            baja = False

        data = {
            'no_bodegas': no_bodegas,
            'bodega': bodega,
            'bodega2':bodega2,
            'bodega3':bodega3,
            'bodega4':bodega4,
            'bodega5':bodega5,
            'bodega6':bodega6,
            'todos_stock': todos_stock,
            'mayor': mayor,
            'menor': menor,
            'igual': igual,
            'mayor_igual': mayor_igual,
            'todos_precio': todos_precio,
            'mayor_precio': mayor_precio,
            'menor_precio': menor_precio,
            'todos_iva': todos_iva,
            'sin_iva': sin_iva,
            'con_iva': con_iva,
            'todos_activo': todos_activo,
            'activo': activo,
            'baja': baja,
            'company': self.start.company.id,
            'date': self.start.date,
            }
        return action, data

    def transition_print_(self):
        return 'end'


class ReportStock(Report):
    __name__ = 'nodux_stock_report_by_filters.report_stock'

    @classmethod
    def parse(cls, report, records, data, localcontext):
        pool = Pool()
        Location = pool.get('stock.location')
        Product = pool.get('product.product')
        PriceList = pool.get('product.price_list')

        Company = pool.get('company.company')
        ProductUom = pool.get('product.uom')

        locations = Location.search([('type', '=', 'storage')])
        product_lines = []

        priceList = PriceList.search([('incluir_lista', '=', True)])

        if len(priceList) == 1:
            tam_price = 1
        elif len(priceList) == 2:
            tam_price = 2
        elif len(priceList) == 3:
            tam_price = 3
        elif len(priceList) == 4:
            tam_price = 4
        elif len(priceList) == 5:
            tam_price = 5
        elif len(priceList) == 6:
            tam_price = 6


        if data['no_bodegas'] == 'no_6':
            no_bodegas = 'no_6'
            for l in locations:
                with Transaction().set_context(stock_date_end=(data['date'])):
                    pbl = Product.products_by_location([l])

                    product2uom = {}
                    product2type = {}
                    product2consumable = {}
                    product_qty = {}

                    for product in Product.browse([line[1] for line in pbl]):
                        product2uom[product.id] = product.default_uom.id
                        product2type[product.id] = product.type
                        product2consumable[product.id] = product.consumable


                    for (location, product), quantity in pbl.iteritems():
                        product_qty[product] = (quantity, product2uom[product])


                    for product_id in product_qty:
                        lineas = {}
                        listas_precios = []
                        for l_p in Product(product_id).listas_precios:
                            listas_precios.append(l_p)

                        if (product2type[product_id] != 'goods'
                                or product2consumable[product_id]):
                            continue
                        quantity, uom_id = product_qty[product_id]


                        if data['todos_stock'] == True:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        if lineas:
                            product_lines.append(lineas)
        elif data['no_bodegas'] == 'no_1':
            no_bodegas = 'no_1'
            with Transaction().set_context(stock_date_end=(data['date'])):
                pbl = Product.products_by_location([data['bodega']])

            product2uom = {}
            product2type = {}
            product2consumable = {}
            product_qty = {}

            for product in Product.browse([line[1] for line in pbl]):
                product2uom[product.id] = product.default_uom.id
                product2type[product.id] = product.type
                product2consumable[product.id] = product.consumable


            for (location, product), quantity in pbl.iteritems():
                product_qty[product] = (quantity, product2uom[product])


            for product_id in product_qty:
                listas_precios = []
                lineas = {}
                if (product2type[product_id] != 'goods'
                        or product2consumable[product_id]):
                    continue
                quantity, uom_id = product_qty[product_id]

                for l_p in Product(product_id).listas_precios:
                    listas_precios.append(l_p)

                if data['todos_activo'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                elif data['baja'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                elif data['activo'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios
                if lineas:
                    product_lines.append(lineas)

        elif data['no_bodegas'] == 'no_2':
            no_bodegas = 'no_2'

            with Transaction().set_context(stock_date_end=(data['date'])):
                pbl = Product.products_by_location([data['bodega']])
                pbl2 = Product.products_by_location([data['bodega2']])

            product2uom = {}
            product2type = {}
            product2consumable = {}
            product_qty = {}
            product_qty2 = {}

            for product in Product.browse([line[1] for line in pbl]):
                product2uom[product.id] = product.default_uom.id
                product2type[product.id] = product.type
                product2consumable[product.id] = product.consumable

            if pbl:
                for (location, product), quantity in pbl.iteritems():
                    product_qty[product] = (quantity, product2uom[product])

            if pbl2:
                for (location, product), quantity in pbl2.iteritems():
                    product_qty2[product] = (quantity, product2uom[product])


            for product_id in product_qty:
                lineas = {}
                quantity2 = 0
                listas_precios = []

                for l_p in Product(product_id).listas_precios:
                    listas_precios.append(l_p)

                if (product2type[product_id] != 'goods'
                        or product2consumable[product_id]):
                    continue
                quantity, uom_id = product_qty[product_id]

                for product_id2 in product_qty2:
                    if product_id2 == product_id:
                        quantity2, uom_id2 = product_qty2[product_id]

                if data['todos_activo'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                elif data['baja'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                elif data['activo'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                if lineas:
                    product_lines.append(lineas)

        elif data['no_bodegas'] == 'no_3':
            no_bodegas = 'no_3'
            with Transaction().set_context(stock_date_end=(data['date'])):
                pbl = Product.products_by_location([data['bodega']])
                pbl2 = Product.products_by_location([data['bodega2']])
                pbl3 = Product.products_by_location([data['bodega3']])

            product2uom = {}
            product2type = {}
            product2consumable = {}
            product_qty = {}
            product_qty2 = {}
            product_qty3 = {}

            for product in Product.browse([line[1] for line in pbl]):
                product2uom[product.id] = product.default_uom.id
                product2type[product.id] = product.type
                product2consumable[product.id] = product.consumable


            for (location, product), quantity in pbl.iteritems():
                product_qty[product] = (quantity, product2uom[product])

            for (location, product), quantity in pbl2.iteritems():
                product_qty2[product] = (quantity, product2uom[product])

            for (location, product), quantity in pbl3.iteritems():
                product_qty3[product] = (quantity, product2uom[product])


            for product_id in product_qty:
                lineas = {}
                quantity2 = 0
                quantity3 = 0
                listas_precios = []

                for l_p in Product(product_id).listas_precios:
                    listas_precios.append(l_p)

                if (product2type[product_id] != 'goods'
                        or product2consumable[product_id]):
                    continue
                quantity, uom_id = product_qty[product_id]

                for product_id2 in product_qty2:
                    if product_id2 == product_id:
                        quantity2, uom_id2 = product_qty2[product_id]

                for product_id3 in product_qty3:
                    if product_id3 == product_id:
                        quantity3, uom_id3 = product_qty3[product_id]

                if data['todos_activo'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                elif data['baja'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                elif data['activo'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                if lineas:
                    product_lines.append(lineas)

        elif data['no_bodegas'] == 'no_4':
            no_bodegas = 'no_4'
            with Transaction().set_context(stock_date_end=(data['date'])):
                pbl = Product.products_by_location([data['bodega']])
                pbl2 = Product.products_by_location([data['bodega2']])
                pbl3 = Product.products_by_location([data['bodega3']])
                pbl4 = Product.products_by_location([data['bodega4']])

            product2uom = {}
            product2type = {}
            product2consumable = {}
            product_qty = {}
            product_qty2 = {}
            product_qty3 = {}
            product_qty4 = {}

            for product in Product.browse([line[1] for line in pbl]):
                product2uom[product.id] = product.default_uom.id
                product2type[product.id] = product.type
                product2consumable[product.id] = product.consumable


            for (location, product), quantity in pbl.iteritems():
                product_qty[product] = (quantity, product2uom[product])

            for (location, product), quantity in pbl2.iteritems():
                product_qty2[product] = (quantity, product2uom[product])

            for (location, product), quantity in pbl3.iteritems():
                product_qty3[product] = (quantity, product2uom[product])

            for (location, product), quantity in pbl4.iteritems():
                product_qty4[product] = (quantity, product2uom[product])


            for product_id in product_qty:
                lineas = {}
                quantity2 = 0
                quantity3 = 0
                quantity4 = 0
                listas_precios = []

                for l_p in Product(product_id).listas_precios:
                    listas_precios.append(l_p)

                if (product2type[product_id] != 'goods'
                        or product2consumable[product_id]):
                    continue
                quantity, uom_id = product_qty[product_id]

                for product_id2 in product_qty2:
                    if product_id2 == product_id:
                        quantity2, uom_id2 = product_qty2[product_id]

                for product_id3 in product_qty3:
                    if product_id3 == product_id:
                        quantity3, uom_id3 = product_qty3[product_id]

                for product_id4 in product_qty4:
                    if product_id4 == product_id:
                        quantity4, uom_id4 = product_qty4[product_id]

                if data['todos_activo'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                elif data['baja'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                elif data['activo'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                if lineas:
                    product_lines.append(lineas)

        elif data['no_bodegas'] == 'no_5':
            no_bodegas = 'no_5'
            with Transaction().set_context(stock_date_end=(data['date'])):
                pbl = Product.products_by_location([data['bodega']])
                pbl2 = Product.products_by_location([data['bodega2']])
                pbl3 = Product.products_by_location([data['bodega3']])
                pbl4 = Product.products_by_location([data['bodega4']])
                pbl5 = Product.products_by_location([data['bodega5']])

            product2uom = {}
            product2type = {}
            product2consumable = {}
            product_qty = {}
            product_qty2 = {}
            product_qty3 = {}
            product_qty4 = {}
            product_qty5 = {}

            for product in Product.browse([line[1] for line in pbl]):
                product2uom[product.id] = product.default_uom.id
                product2type[product.id] = product.type
                product2consumable[product.id] = product.consumable

            for (location, product), quantity in pbl.iteritems():
                product_qty[product] = (quantity, product2uom[product])

            for (location, product), quantity in pbl2.iteritems():
                product_qty2[product] = (quantity, product2uom[product])

            for (location, product), quantity in pbl3.iteritems():
                product_qty3[product] = (quantity, product2uom[product])

            for (location, product), quantity in pbl4.iteritems():
                product_qty4[product] = (quantity, product2uom[product])

            for (location, product), quantity in pbl5.iteritems():
                product_qty5[product] = (quantity, product2uom[product])

            for product_id in product_qty:
                lineas = {}
                quantity2 = 0
                quantity3 = 0
                quantity4 = 0
                quantity5 = 0

                listas_precios = []

                for l_p in Product(product_id).listas_precios:
                    listas_precios.append(l_p)

                if (product2type[product_id] != 'goods'
                        or product2consumable[product_id]):
                    continue
                quantity, uom_id = product_qty[product_id]

                for product_id2 in product_qty2:
                    if product_id2 == product_id:
                        quantity2, uom_id2 = product_qty2[product_id]

                for product_id3 in product_qty3:
                    if product_id3 == product_id:
                        quantity3, uom_id3 = product_qty3[product_id]

                for product_id4 in product_qty4:
                    if product_id4 == product_id:
                        quantity4, uom_id4 = product_qty4[product_id]

                for product_id5 in product_qty5:
                    if product_id5 == product_id:
                        quantity5, uom_id5 = product_qty5[product_id]

                if data['todos_activo'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0:
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0)):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                elif data['baja'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == False):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                elif data['activo'] == True:
                    if data['todos_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['mayor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price > Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                    elif data['menor_precio'] == True:
                        if data['todos_stock'] == True and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor'] == True and quantity > 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['menor'] == True and quantity < 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['igual'] == True and quantity == 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                        elif data['mayor_igual'] == True and quantity >= 0 and (Product(product_id).template.list_price < Decimal(0.0))  and (Product(product_id).active == True):
                            lineas['product'] = Product(product_id)
                            lineas['quantity'] = quantity
                            lineas['quantity2'] = quantity2
                            lineas['quantity3'] = quantity3
                            lineas['quantity4'] = quantity4
                            lineas['quantity5'] = quantity5
                            lineas['uom'] = ProductUom(uom_id)
                            lineas['pricelist'] = listas_precios

                if lineas:
                    product_lines.append(lineas)

        company = Company(data['company'])
        if data['bodega']:
            bodega = Location(data['bodega'])
        else:
            bodega = None
        if data['bodega2']:
            bodega2 = Location(data['bodega2'])
        else:
            bodega2 = None
        if data['bodega3']:
            bodega3 = Location(data['bodega3'])
        else:
            bodega3 = None
        if data['bodega4']:
            bodega4 = Location(data['bodega4'])
        else:
            bodega4 = None
        if data['bodega5']:
            bodega5 = Location(data['bodega5'])
        else:
            bodega5 = None
        if data['bodega6']:
            bodega6 = Location(data['bodega6'])
        else:
            bodega6 = None

        date = data['date']
        localcontext['lines'] = product_lines
        localcontext['company'] = company
        localcontext['date'] = date
        localcontext['location'] = bodega
        localcontext['location2'] = bodega2
        localcontext['location3'] = bodega3
        localcontext['location4'] = bodega4
        localcontext['location5'] = bodega5
        localcontext['location6'] = bodega6
        localcontext['no_bodegas'] = no_bodegas

        return super(ReportStock, cls).parse(report, records, data,
                localcontext=localcontext)
