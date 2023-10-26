from openerp import fields, models

class hr_payslip_wizard(models.TransientModel):
    _name = 'hr.duty_roster.wizard'
    slip_ids = fields.Many2many('hr.employee.duty.roster', string="Pay slips")
    
    _defaults = {
        'slip_ids' : lambda self, cr, uid, context: context.get('slip_ids',False),
        }
    
    def compute_all_slips(self, cr, uid, ids, context=None):
        payslip_obj = self.pool.get('hr.employee.duty.roster')
        for rec in self.browse(cr,uid,ids):
            s_ids = []
            for slip in rec.slip_ids:
                s_ids.append(slip.id)
            print s_ids
            if s_ids:
                payslip_obj.compute(cr, uid, s_ids, context=context)
              
    
