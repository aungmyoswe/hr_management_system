from openerp import models, fields
#from setuptools.depends import Require

class Treatment(models.Model):
    _name = 'treatment.treatment'
    
    name = fields.Text('Treatment Description', require=True)
    drug_id = fields.One2many('treatment.drug.line','drug_line','Drugs')
    drug_line_name = fields.Char(related="drug_id.drug.name", string="Drugs", store=True)
    drug_line_qty = fields.Integer(related="drug_id.qty", string="Quantity", store=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    treatment_date = fields.Date('Date', require=True)
    doctor_id = fields.Many2one('treatment.doctor', string="Doctor")
    

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    treatment_id = fields.One2many('treatment.treatment','employee_id','Treatment', copy = True)

class TreatmentDoctor(models.Model):
    _name = 'treatment.doctor'
    name = fields.Char('Doctor Name',require=True)
    doctor = fields.One2many('treatment.treatment', 'doctor_id', 'doctor', copy=True)

class TreatmentDrug(models.Model):
    _name = 'treatment.drug'
    name = fields.Char('Drug Name',require=True)
    drug = fields.One2many('treatment.treatment', 'drug_id', 'drug', copy=True)
    
class TreatmentDrugLine(models.Model):
    _name = 'treatment.drug.line'
    name = fields.Char('Drug Name',require=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    drug = fields.Many2one('treatment.drug',string="Drug", require=True)
    qty = fields.Integer('Quantity', require=True)
    drug_line = fields.Many2one('treatment.treatment','Drugs')