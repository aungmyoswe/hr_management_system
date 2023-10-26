from openerp import models, fields, api

class Termination(models.Model):
    _name = 'termination'
    
    order_no = fields.Char('Order No',required = True)
    order_date = fields.Date('Order Date',required = True)
    title_id = fields.Many2one('termination.title', 'Title',required = True)
    termination_line = fields.One2many('termination.line','termination_id','Termination Lines')
    distribute_line = fields.One2many('termination.distribute','termination_id','Termination Distributes')
    
    @api.multi
    def print_receipt(self):
        print self.id
        if self.id:
            url = 'http://localhost:8080/birt-viewer/frameset?__report=termination_list.rptdesign&id=' + str(self.id) 
        if url :
            return {
            'type' : 'ir.actions.act_url',
            'url' : url,
            'target': 'new',
            }
        else:
            raise ValidationError('Not Found')
            
        return True

    @api.multi
    def unlink(self):
        record = self.pool.get('termination').browse(self.env.cr,self.env.uid,self.ids)
        termination_line_obj = self.pool.get('termination.line')
        print record         
    
        for rec in record:
          records = termination_line_obj.search(self.env.cr,self.env.uid,[('termination_id', '=', rec.id)])
          records = termination_line_obj.browse(self.env.cr,self.env.uid,records)
          print records
        
          for record_line_ids in records:
              print record_line_ids
              record_line_id = termination_line_obj.unlink(self.env.cr,self.env.uid, record_line_ids.id)   
              print 'unlink termination lines ...'
              print record_line_id

        return models.Model.unlink(self)

class TerminationLine(models.Model):
    _name = 'termination.line'
    
    termination_id = fields.Many2one('termination', 'Termination',required = True)
    employee = fields.Many2one('hr.employee','Employee', required = True)
    job = fields.Many2one('hr.job','Job Title', required = True)
    department = fields.Many2one('hr.department','Department',required = True)
    section = fields.Many2one('hr.section','Section')
    reason = fields.Char('Reason',required = True)
    termination_date = fields.Date('Termination Date',required = True)
    description = fields.Char('Description')
    deactive = fields.Boolean("Active", related="employee.active", store=True)
    
class TerminationDistribute(models.Model):
    _name = 'termination.distribute'
    
    termination_id = fields.Many2one('termination', 'Termination',required = True)
    #employee = fields.Many2one('hr.employee','Employee', required = True)
    #job = fields.Many2one('hr.job','Job Title',)
    #department = fields.Many2one('hr.department','Department',)
    
    #title = fields.Char('Title')
    title_id = fields.Many2one('termination.distribute.title','Title')
    
class TerminationDistributeTitle(models.Model):
    _name = 'termination.distribute.title'
    
    name = fields.Char('Title', required =True)
    
class TerminationTitle(models.Model):
    _name = 'termination.title'
    
    name = fields.Char('Name', required =True)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    termination_id = fields.One2many('termination.line','employee','Termination', copy = True)
     
