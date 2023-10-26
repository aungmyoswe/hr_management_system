from openerp import models, fields

class HrSection(models.Model):
    _name = 'hr.section'
    _description = 'Section in Human Resource Management'
    
    name = fields.Char("Name", required=True)
    department_id = fields.Many2one("hr.department", "Department", required=True)
    #sequence = fields.Integer("Sequence", required=True)
    