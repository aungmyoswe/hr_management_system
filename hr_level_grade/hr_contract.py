from openerp import fields, models, api
from datetime import datetime, timedelta

class contract_init(models.Model):

    _name = 'hr.contract'
    _inherit = 'hr.contract'

    job_level = fields.Many2one('hr.management.level',string='Job Level',related='job_id.job_level',readonly=True,store=True,copy=True)
    wage = fields.Float('Wage',related='job_level.salary_amount',store=True,copy=True)
    specail_allowance = fields.Float('Special Allowance',related='job_level.allowance_amount',store=True,copy=True)
    

