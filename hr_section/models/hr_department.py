from openerp import models, fields, api

class HrDepartment(models.Model):
	_inherit = 'hr.department'

	#sequence = fields.Integer("Sequence", required=True)
