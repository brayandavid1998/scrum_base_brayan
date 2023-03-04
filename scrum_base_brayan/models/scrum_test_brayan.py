import models,fields


class ScrumTestMolina(models.Model):
    _CantidadProductos = 'Test.Molina'

    Amount_Product = fields.one2many(string="Cantidad")

class ScrumTestBryan(models.Model):
    _Nombre = 'Test Bryan'
    _FechaVencimiento = 'Test.Bryan'
    _TipoProducto = 'Test.Bryan'

    name = fields.Char(string="Nombre")
    expires = fields.date("Fecha")
    typeproduct = fields.many2One(string="TipoDeProducto", default="cantidad")


