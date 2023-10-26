from openerp import api, models, fields
from openerp.exceptions import ValidationError

class HrContract(models.Model):
    _name = 'hr.contract'
    _inherit = "hr.contract"
    
    is_cycle_using = fields.Boolean('Include Cycle Using')
    is_outbound = fields.Boolean('Include Outbound')
    is_travel_allowance = fields.Boolean('Include Travel')
    cold_room_allowance = fields.Float('Cold Room Amount')
    month_allowance = fields.Float('Month Allowance')
    year_allowance = fields.Float('Year Allowance')

    ot_rate = fields.Float('OT Rate')
    is_ssb = fields.Boolean('Include SSB')
    



