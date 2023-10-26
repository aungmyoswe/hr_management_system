from openerp import models, fields, api

class permanent(models.Model):
    _name = 'permanent'
    
    order_no = fields.Char('Order No',required = True)
    order_date = fields.Date('Order Date',required = True)
    title_id = fields.Many2one('permanent.title', 'Title',required = True)
    permanent_line = fields.One2many('permanent.line','permanent_id','Permanent Lines')
    distribute_line = fields.One2many('permanent.distribute','permanent_id','Permanent Distributes')
    
class permanentLine(models.Model):
    _name = 'permanent.line'
    
    permanent_id = fields.Many2one('permanent', 'permanent',required = True)
    employee = fields.Many2one('hr.employee','Employee', required = True)
    job = fields.Many2one('hr.job','Job Title', required = True)
    department = fields.Many2one('hr.department','Department',required = True)
    section = fields.Many2one('hr.section','Section')
    reason = fields.Char('Reason',required = True)
    permanent_date = fields.Date('permanent Date',required = True)
    description = fields.Char('Description')
    deactive = fields.Boolean("Active", related="employee.active", store=True)
    
class permanentDistribute(models.Model):
    _name = 'permanent.distribute'
    
    permanent_id = fields.Many2one('permanent', 'permanent',required = True)
    #employee = fields.Many2one('hr.employee','Employee', required = True)
    #job = fields.Many2one('hr.job','Job Title',)
    #department = fields.Many2one('hr.department','Department',)
    
    #title = fields.Char('Title')
    title_id = fields.Many2one('permanent.distribute.title','Title')
    
class permanentDistributeTitle(models.Model):
    _name = 'permanent.distribute.title'
    
    name = fields.Char('Title', required =True)
    
class permanentTitle(models.Model):
    _name = 'permanent.title'
    
    name = fields.Char('Name', required =True)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    permanent_id = fields.One2many('permanent.line','employee','permanent', copy = True)
     
