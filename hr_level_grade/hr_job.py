from openerp import models, fields, api

class HrDepartment(models.Model):
	_inherit = 'hr.job'

	job_level = fields.Many2one("hr.management.level", "Job Level")
	
	
	