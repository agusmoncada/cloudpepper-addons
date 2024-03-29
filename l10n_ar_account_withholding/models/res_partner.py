# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
# from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    # TODO renombrar campo
    arba_alicuot_ids = fields.One2many(
        'res.partner.arba_alicuot',
        'partner_id',
        'Alícuotas PERC-RET',
    )
    drei = fields.Selection([
        ('activo', 'Activo'),
        ('no_activo', 'No Activo'),
    ],
        string='DREI',
    )
    # TODO agregarlo en mig a v10 ya que fix dbs no es capaz de arreglarlo
    # porque da el error antes de empezar a arreglar
    # drei_number = fields.Char(
    # )
    default_regimen_ganancias_id = fields.Many2one(
        'afip.tabla_ganancias.alicuotasymontos',
        'Regimen Ganancias por Defecto',
    )

    def get_arba_alicuota_percepcion(self):
        company = self._context.get('invoice_company')
        date_invoice = self._context.get('date_invoice')
        if date_invoice and company:
            date = fields.Date.from_string(date_invoice)
            arba = self.get_arba_data(company, date)
            return arba.alicuota_percepcion / 100.0
        return 0

    def get_arba_alicuota_retencion(self, company, date):
        arba = self.get_arba_data(company, date)
        return arba.alicuota_retencion / 100.0

    def get_arba_data(self, company, date):
        self.ensure_one()
        from_date = (date + relativedelta(day=1)).strftime('%Y%m%d')
        to_date = (date + relativedelta(
            day=1, days=-1, months=+1)).strftime('%Y%m%d')
        commercial_partner = self.commercial_partner_id
        arba = self.arba_alicuot_ids.search([
            ('from_date', '=', from_date),
            ('to_date', '=', to_date),
            ('company_id', '=', company.id),
            ('partner_id', '=', commercial_partner.id)], limit=1)
        if not arba:
            arba_data = company.get_arba_data(
                commercial_partner,
                from_date, to_date,
            )
            arba_data['partner_id'] = commercial_partner.id
            arba_data['company_id'] = company.id
            arba = self.arba_alicuot_ids.sudo().create(arba_data)
        return arba

    def get_retencion(self, tax_code = ''):
        res = 0
        if tax_code:
            tax_id = self.env['account.tax'].search([('padron_prefix','=',tax_code)],limit=1)
            if tax_id:
                retention_id = self.env['res.partner.perception'].search(
                        [('partner_id','=',self.id),('tax_id','=',tax_id.id)],
                        order='date_from desc',
                        limit=1)
                if retention_id:
                    res = retention_id.percent / 100
        return res


class ResPartnerArbaAlicuot(models.Model):
    # TODO rename model to res.partner.tax or similar
    _name = "res.partner.arba_alicuot"
    _order = "to_date desc, from_date desc, tag_id, company_id"

    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        ondelete='cascade',
    )
    tax_id = fields.Many2one(
        'account.tax',
        'Impuesto',
        domain=[('type_tax_use', '=', 'supplier')],
    )
    percent = fields.Float('Porcentaje',digits=(6,4))
    tag_id = fields.Many2one(
        'account.account.tag',
        domain=[('applicability', '=', 'taxes')],
        change_default=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        ondelete='cascade',
        default=lambda self: self.env.user.company_id,
    )
    from_date = fields.Date(
    )
    to_date = fields.Date(
    )
    numero_comprobante = fields.Char(
    )
    codigo_hash = fields.Char(
    )
    alicuota_percepcion = fields.Float(
    )
    alicuota_retencion = fields.Float(
    )
    grupo_percepcion = fields.Char(
    )
    grupo_retencion = fields.Char(
    )
    withholding_amount_type = fields.Selection([
        ('untaxed_amount', 'Untaxed Amount'),
        ('total_amount', 'Total Amount'),
    ],
        'Base para retenciones',
        help='Base amount used to get withholding amount',
    )
    regimen_percepcion = fields.Char(
        size=3,
        help="Utilizado para la generación del TXT para SIRCAR.\n"
        "Tipo de Régimen de Percepción (código correspondiente según "
        "tabla definida por la jurisdicción)"
    )
    regimen_retencion = fields.Char(
        size=3,
        help="Utilizado para la generación del TXT para SIRCAR.\n"
        "Tipo de Régimen de Retención (código correspondiente según "
        "tabla definida por la jurisdicción)"
    )
    api_codigo_articulo_retencion = fields.Selection([
        ('001', '001: Art.1 - inciso A - (Res. Gral. 15/97 y Modif.)'),
        ('002', '002: Art.1 - inciso B - (Res. Gral. 15/97 y Modif.)'),
        ('003', '003: Art.1 - inciso C - (Res. Gral. 15/97 y Modif.)'),
        ('004', '004: Art.1 - inciso D pto.1 - (Res. Gral. 15/97 y Modif.)'),
        ('005', '005: Art.1 - inciso D pto.2 - (Res. Gral. 15/97 y Modif.)'),
        ('006', '006: Art.1 - inciso D pto.3 - (Res. Gral. 15/97 y Modif.)'),
        ('007', '007: Art.1 - inciso E - (Res. Gral. 15/97 y Modif.)'),
        ('008', '008: Art.1 - inciso F - (Res. Gral. 15/97 y Modif.)'),
        ('009', '009: Art.1 - inciso H - (Res. Gral. 15/97 y Modif.)'),
        ('010', '010: Art.1 - inciso I - (Res. Gral. 15/97 y Modif.)'),
        ('011', '011: Art.1 - inciso J - (Res. Gral. 15/97 y Modif.)'),
        ('012', '012: Art.1 - inciso K - (Res. Gral. 15/97 y Modif.)'),
        ('013', '013: Art.1 - inciso L - (Res. Gral. 15/97 y Modif.)'),
        ('014', '014: Art.1 - inciso LL pto.1 - (Res. Gral. 15/97 y Modif.)'),
        ('015', '015: Art.1 - inciso LL pto.2 - (Res. Gral. 15/97 y Modif.)'),
        ('016', '016: Art.1 - inciso LL pto.3 - (Res. Gral. 15/97 y Modif.)'),
        ('017', '017: Art.1 - inciso LL pto.4 - (Res. Gral. 15/97 y Modif.)'),
        ('018', '018: Art.1 - inciso LL pto.5 - (Res. Gral. 15/97 y Modif.)'),
        ('019', '019: Art.1 - inciso M - (Res. Gral. 15/97 y Modif.)'),
        ('020', '020: Art.2 - (Res. Gral. 15/97 y Modif.)'),
    ],
        string='Código de Artículo/Inciso por el que retiene',
    )
    api_codigo_articulo_percepcion = fields.Selection([
        ('021', '021: Art.10 - inciso A - (Res. Gral. 15/97 y Modif.)'),
        ('022', '022: Art.10 - inciso B - (Res. Gral. 15/97 y Modif.)'),
        ('023', '023: Art.10 - inciso D - (Res. Gral. 15/97 y Modif.)'),
        ('024', '024: Art.10 - inciso E - (Res. Gral. 15/97 y Modif.)'),
        ('025', '025: Art.10 - inciso F - (Res. Gral. 15/97 y Modif.)'),
        ('026', '026: Art.10 - inciso G - (Res. Gral. 15/97 y Modif.)'),
        ('027', '027: Art.10 - inciso H - (Res. Gral. 15/97 y Modif.)'),
        ('028', '028: Art.10 - inciso I - (Res. Gral. 15/97 y Modif.)'),
        ('029', '029: Art.10 - inciso J - (Res. Gral. 15/97 y Modif.)'),
        ('030', '030: Art.11 - (Res. Gral. 15/97 y Modif.)'),
    ],
        string='Código de artículo Inciso por el que percibe',
    )
    api_articulo_inciso_calculo_selection = [
        ('001', '001: Art. 5º 1er. párrafo (Res. Gral. 15/97 y Modif.)'),
        ('002', '002: Art. 5º inciso 1)(Res. Gral. 15/97 y Modif.)'),
        ('003', '003: Art. 5° inciso 2)(Res. Gral. 15/97 y Modif.)'),
        ('004', '004: Art. 5º inciso 4)(Res. Gral. 15/97 y Modif.)'),
        ('005', '005: Art. 5° inciso 5)(Res. Gral. 15/97 y Modif.)'),
        ('006', '006: Art. 6º inciso a)(Res. Gral. 15/97 y Modif.)'),
        ('007', '007: Art. 6º inciso b)(Res. Gral. 15/97 y Modif.)'),
        ('008', '008: Art. 6º inciso c)(Res. Gral. 15/97 y Modif.)'),
        ('009', '009: Art. 12º)(Res. Gral. 15/97 y Modif.)'),
        ('010', '010: Art. 6º inciso d)(Res. Gral. 15/97 y Modif.)'),
        ('011', '011: Art. 5° inciso 6)(Res. Gral. 15/97 y Modif.)'),
        ('012', '012: Art. 5° inciso 3)(Res. Gral. 15/97 y Modif.)'),
        ('013', '013: Art. 5° inciso 7)(Res. Gral. 15/97 y Modif.)'),
        ('014', '014: Art. 5° inciso 8)(Res. Gral. 15/97 y Modif.)'),
    ]
    api_articulo_inciso_calculo_percepcion = fields.Selection(
        api_articulo_inciso_calculo_selection,
        string='Artículo/Inciso para el cálculo percepción',
    )
    api_articulo_inciso_calculo_retencion = fields.Selection(
        api_articulo_inciso_calculo_selection,
        string='Artículo/Inciso para el cálculo retención',
    )
