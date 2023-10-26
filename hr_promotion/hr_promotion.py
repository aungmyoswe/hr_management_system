from openerp import api, models, fields
from openerp.exceptions import ValidationError

class HrPromotion(models.Model):    
	_name = 'hr.promotion'
	_rec_name = 'employee'

	employee = fields.Many2one('hr.employee', string='Employee')
	emp_id = fields.Char('Employee ID')
	doa = fields.Date('D.O.A')
	department = fields.Many2one('hr.department', string='Department')
	old_position = fields.Many2one('hr.job', 'Current Position')
	old_salary = fields.Float('Current Salary')
	new_department = fields.Many2one('hr.department', string="New Department")
	new_position = fields.Many2one('hr.job', 'Promoted Position')
	new_salary = fields.Float('New Salary')
	eff_date = fields.Date('Effective Date')
	remark = fields.Text('Remark')
	state = fields.Selection([('draft', 'Draft'),
                ('error', 'Error'),('finished', 'Finished'),], 'States')
	section_id = fields.Many2one('hr.section', string='Section')
	sub_section_id = fields.Many2one('hr.sub.section', string='Sub Section')

	_defaults = {'state':'draft'}

	@api.one
	@api.onchange('employee')
	def _onchange_employee(self):
		self.emp_id = self.employee.emp_id
		self.doa = self.employee.contract_id.trial_date_start
		self.department = self.new_department = self.employee.department_id
		self.old_position = self.employee.contract_id.job_id
		self.old_salary = self.employee.contract_id.wage
		self.section_id = self.employee.section_id
		self.sub_section_id = self.employee.sub_section_id


	def validate_promotion(self, cr, uid, ids, context=None):
		contract_obj = self.pool.get('hr.contract')
		employee_obj = self.pool.get('hr.employee')
		for prom in self.browse(cr, uid , ids):
			emp_value = {'job_id':prom.new_position.id,'department_id':prom.new_department.id}
			employee_obj.write(cr, uid, prom.employee.id, emp_value)
			contract_value = {'job_id':prom.new_position.id,'department_id':prom.new_department.id,'wage':prom.new_salary}
			contract_obj.write(cr, uid, prom.employee.contract_id.id, contract_value)
			self.write(cr, uid, ids, {'state':'finished'})

	def reverse_promotion(self, cr, uid, ids, context=None):
		contract_obj = self.pool.get('hr.contract')
		employee_obj = self.pool.get('hr.employee')
		for prom in self.browse(cr, uid , ids):
			emp_value = {'job_id':prom.old_position.id,'department_id':prom.department.id}
			employee_obj.write(cr, uid, prom.employee.id, emp_value)
			contract_value = {'job_id':prom.old_position.id,'wage':prom.old_salary,'department_id':prom.department.id}
			contract_obj.write(cr, uid, prom.employee.contract_id.id, contract_value)
			self.write(cr, uid, ids, {'state':'draft'})



