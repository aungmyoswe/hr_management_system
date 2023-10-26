from openerp import models, fields, api

class HrDepartment(models.Model):
	_inherit = 'hr.job'

	section_id = fields.Many2one("hr.section", "Section", domain="[('department_id', '=', department_id)]", select=True)
	sub_section_id = fields.Many2one("hr.sub.section", "Sub Section", domain="[('section_id', '=', section_id)]", select=True)
	
	