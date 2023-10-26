from openerp import fields, models

class hr_payslip_wizard(models.TransientModel):
    _name = 'hr.payslip.wizard'
    slip_ids = fields.Many2many('hr.payslip', string="Pay slips")
    
    _defaults = {
        'slip_ids' : lambda self, cr, uid, context: context.get('slip_ids',False),
        }
    
    def compute_all_slips(self, cr, uid, ids, context=None):
        # all payslip import must have success

        payslip_obj = self.pool.get('hr.payslip')
        for rec in self.browse(cr,uid,ids):
            s_ids = []
            for slip in rec.slip_ids:
                s_ids.append(slip.id)
            print s_ids
            if s_ids:
                payslip_obj.compute_sheet(cr, uid, s_ids, context=context)

class hr_payslip_input_wizard(models.TransientModel):
    _name = 'hr.payslip.input.wizard'
    import_ids = fields.Many2many('data_import.payroll', string="Amount Import")
    
    _defaults = {
        'import_ids' : lambda self, cr, uid, context: context.get('import_ids',False),
        }
    
    def import_all_amount(self, cr, uid, ids, context=None):
        import_obj = self.pool.get('data_import.payroll')
        for rec in self.browse(cr,uid,ids):
            s_ids = []
            for slip in rec.import_ids:
                s_ids.append(slip.id)
            print s_ids
            if s_ids:
                import_obj.import_data_by_amount(cr, uid, s_ids, context=context)
              
    