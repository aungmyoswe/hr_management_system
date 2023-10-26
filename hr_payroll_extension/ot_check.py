from openerp import models, fields, api
from openerp.exceptions import ValidationError

class hr_payslip(models.Model):
    _inherit = "hr.payslip"

    parent_department_id = fields.Many2one(related='employee_id.parent_department_id',string='Parent Department',store=True)
    is_above_supervisor = fields.Boolean(compute="_is_above_supervisor")

    # False Invisible
    # True  Visible
    @api.one
    def _is_above_supervisor(self):
        print '_is_above_supervisor call'
        self.is_above_supervisor = False
        is_finance_user = self.env['res.users'].search([('id', '=', self.env.uid)]).is_finance_user
        is_finance_manager = self.env['res.users'].search([('id', '=', self.env.uid)]).is_finance_manager
        
        if is_finance_manager:
            self.is_above_supervisor = True
        elif is_finance_manager and is_finance_user:
            self.is_above_supervisor = True
        elif is_finance_user:
            if not self.contract_id.job_id.is_above_supervisor:
                self.is_above_supervisor = True

        print self.is_above_supervisor

class payslip_checking(models.Model):
    _name = "hr.payslip.checking"

    employee_id = fields.Many2one('hr.employee','Employee')
    parent_department_id = fields.Many2one('hr.department','Parent Department')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    wd = fields.Float('WD')
    leave = fields.Float('Leave')
    late_leave = fields.Float('Late Leave')
    late_big = fields.Float('Late > 25')
    late_small = fields.Float('Late < 25')
    late_half = fields.Float('Late Half')
    absent = fields.Float('Absent')
    df_ot = fields.Float('DayOff OT')
    n_ot = fields.Float('Normal OT')
    od = fields.Float('OnDuty')
    # late_leave_exception = fields.Boolean('Leave Leave Exception')
    # absent_exception = fields.Boolean('Absent Exception')
    
class Ot_Check(models.Model):
    _name = "hr.ot_check"
    
    slip_id = fields.Many2one('hr.payslip')
    employee_id = fields.Many2one('hr.employee')
    parent_department_id = fields.Many2one(related='employee_id.parent_department_id',string='Parent Department',store=True)
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    work_day = fields.Char('Work Day')
    shift = fields.Char('Shift')
    in_out = fields.Char('Attendance')
    ot = fields.Char('OT')
    od = fields.Char('On Duty')
    wp = fields.Char('WP')
    wd = fields.Char('WD')
    l = fields.Char('Leave')
    lh = fields.Boolean('Leave Have')
    late = fields.Char('Late')
    late_have = fields.Boolean('Late Have')

# class OT_Request(models.Model):    
#     _name = 'hr.ot.request'

#     employee_id = fields.Many2one('hr.employee',string="Employee")
#     department_id = fields.Many2one('hr.department',related='employee_id.department_id',string="Department",readonly=True)
#     job_id = fields.Many2one('hr.job',related='employee_id.job_id',string="Job",readonly=True)
    
#     date = fields.Date('Date', required=True)
#     start_time = fields.Char('Start Time') #, required=True
#     end_time = fields.Char('End Time') #, required=True
#     total_hours = fields.Float('Total Hours', required=True)
#     reason = fields.Text('Reason')

#     manager = fields.Many2one('hr.employee', string='Manager', readonly=True)

# class OD_Request(models.Model):    
#     _name = 'hr.od.request'

#     employee_id = fields.Many2one('hr.employee',string="Employee")
#     department_id = fields.Many2one('hr.department',related='employee_id.department_id',string="Department",readonly=True)
#     job_id = fields.Many2one('hr.job',related='employee_id.job_id',string="Job",readonly=True)
    
#     date = fields.Date('Date', required=True)
#     start_time = fields.Char('Start Time') #, required=True
#     end_time = fields.Char('End Time') #, required=True
#     total_hours = fields.Char('Total Hours', required=True)
#     reason = fields.Text('Reason')

class hr_payroll_structure(models.Model):
    _inherit = 'hr.payroll.structure'

    department_id = fields.Many2one('hr.department', string='Department')
    parent_department_id = fields.Many2many('hr.department','hr_payroll_structure_department_rel',
              'structure_id', 'parent_department_id', string='Parent Department',required=True)

class hr_payroll_approve(models.Model):
    _name = 'hr.payroll.approve'

    name = fields.Many2one('hr.employee', string='Employee')
    date = fields.Date(string='Date')
    confirm = fields.Selection([('draft','Draft'),('approve','Approve')],'Status')
    run_id = fields.Many2one('hr.payslip.run', string='Payslip Run')

class hr_payroll_approve(models.Model): 
    _inherit = 'hr.payslip.run'

    approve_ids = fields.One2many('hr.payroll.approve','run_id','Payslip Approve', copy = True) 
    is_already_approve = fields.Boolean(compute="_is_already_approve")
    state = fields.Selection([
            ('draft', 'Draft'),
            ('check', 'Check'),
            ('generate', 'Generate'),
            ('close', 'Close'),
        ], 'Status', select=True, readonly=True, copy=False)

    def check_payslip_run(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'check'}, context=context)

    def generate_payslip_run(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'generate'}, context=context)

    @api.one
    def _is_already_approve(self):
      print '_is_already_approve'
      hr_payroll_approve_obj = self.pool.get('hr.payroll.approve')
      
      self.is_already_approve = False
      print self.id
      for a in hr_payroll_approve_obj.search(self.env.cr,self.env.uid,[('run_id', '=', self.id)]):
        if hr_payroll_approve_obj.browse(self.env.cr,self.env.uid,a).confirm == 'approve':
            self.is_already_approve = True

      print self.is_already_approve

class res_user(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    is_finance_user = fields.Boolean('is_finance_user')
    is_finance_manager = fields.Boolean('is_finance_manager')
      