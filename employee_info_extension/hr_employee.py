from openerp import fields, models, api
from datetime import datetime, timedelta
from datetime import date
from openerp.exceptions import ValidationError

SELECTION_RANK = [
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('15', '15')
    ]

class Hr_Employee(models.Model):

    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    # Change label Manager to Management by thurein soe 9/19/2017
    parent_id = fields.Many2one('hr.employee', string='Management')
    # -----------------------------------------------------
    # change work phone to mobile phone
    work_phone = fields.Char(' Mobile Phone', readonly=False)
    otherid = fields.Char('Fingerprint Id')
    fingerprint_name = fields.Char('Fingerprint Name')
    burmese_name = fields.Char('Burmese Name',requried=True)
    working_experience = fields.Text('Working Experience')
    show_in_report = fields.Boolean('Show In Report')
    manager = fields.Boolean('HOD')
    blood_group = fields.Char('Blood Type')
    mobile = fields.Char('Mobile', size=30)
    emp_id = fields.Char('Employee ID')
    education = fields.Char('Education')
    # Create education format by thurein soe 9/19/2017
    other_qualis = fields.Text('Other Qualifications')
    subject = fields.Many2one('hr.employee.subject', string='Subject')
    degree = fields.Many2one('hr.recruitment.degree', string='Degree')
    license_no = fields.Char('License No')
    promotion_order_no = fields.Char('Promotion Order No')
    
    office_order_no = fields.Char('Office Order No.')
    religion = fields.Char('Religion')
    nrc_image = fields.Binary(string="NRC")
    house_hold_image = fields.Binary(string="House Hold")            
    attachment_ids = fields.Many2many('ir.attachment','hr_employee_ir_attachments_rel',
            'employee_id', 'attachment_id', string='Attachments')
    
    section_id = fields.Many2one("hr.section",string="Section",domain="[('department_id', '=', department_id)]",readonly=False,store=True,)
    sub_section_id = fields.Many2one("hr.sub.section", "Sub Section", domain="[('section_id', '=', section_id),('department_id', '=', department_id)]",readonly=False,store=True,)
    job_id = fields.Many2one('hr.job', 'Job Title', domain="[('section_id', '=', section_id),('sub_section_id', '=', sub_section_id),('department_id', '=', department_id)]")
    age = fields.Integer('Age', compute='_compute_age') 
    employment = fields.Char('Employment', compute='_compute_employment')
    trial_date_start = fields.Date(string='Joining Date',require=True)
    trial_date_end = fields.Date(string='End of Probation' ,compute='_compute_trial_date_end',store=True)
    
    parent_department_id = fields.Many2one('hr.department', string='Parent Department',domain="[('parent_id', '=', False)]",required=True)

    # def create(self, cr, uid, data, context=None):
    #     context = dict(context or {})
    #     print 'Hr_Employee Create ----------'
        
    #     print 'Hr_Employee Data ' + str(data)
    #     #raise ValidationError('Record !')
    #     record_id = super(Hr_Employee, self).create(cr, uid, data, context=context)
    #     print record_id
        
	   #    # assessment auto create
    #     assessment_obj = self.pool.get('assessment.record')
    #     record_value = {
    #                   'employee': record_id,
    #     }
    #     assessment_obj.create(cr, uid, record_value, context=context)
        
	   #    # contract auto create
    #     contract_obj = self.pool.get('hr.contract')
    #     contract_value={}
    #     contract_value['name'] = data['name'] + ' Contract'        
    #     contract_value['employee_id'] = record_id
    #     contract_value['job_id'] = data['job_id']
    #     #contract_value['date_start'] = data['trial_date_start']
    #     #contract_value['trial_date_start'] = data['trial_date_start']
    #     contract_value['wage'] = 0
    #     contract_value['struct_id'] = 1
    #     contract_obj.create(cr, uid, contract_value, context=context)
        
    #     return record_id
    
    # @api.one
    # @api.depends('trial_date_start')
    # def _compute_trial_date_end(self):
    #   print '_compute_trial_date_end'
    #   if self.trial_date_start:
    #     trial_date_start=datetime.strptime(str(self.trial_date_start),"%Y-%m-%d")
    #     self.trial_date_end= trial_date_start + timedelta(days=90)
    #     print self.trial_date_end

    @api.one
    @api.depends('trial_date_start')
    def _compute_trial_date_end(self):
      print '_compute_trial_date_end'
      if self.trial_date_start:
        trial_date_start=datetime.strptime(str(self.trial_date_start),"%Y-%m-%d")
        year=trial_date_start.year
        day=trial_date_start.day 
        month=trial_date_start.month+3
        if month > 12:
          month=month-12
          year=year+1
        else:
          month=month 
        end_date=str(int(year))+'-'+str(int(month))+'-'+str(int(day))
        date_end=datetime.strptime(str(end_date),'%Y-%m-%d')
        d_day=abs(date_end-trial_date_start).days
        self.trial_date_end= trial_date_start + timedelta(days=d_day)
        print self.trial_date_end

    @api.depends('employment','trial_date_start')
    def _compute_employment(self):
        print '_compute_employment'
        print self.trial_date_start
        if self.trial_date_start:
          self.env.cr.execute("SELECT to_char(age(CURRENT_TIMESTAMP,'" + self.trial_date_start + "'), 'YY') || ' Years and ', to_char(age(CURRENT_TIMESTAMP,'" + self.trial_date_start + "'), 'MM') || ' Months' FROM hr_employee");
          s = str(self.env.cr.fetchone())
          print s
          start = s.find("(")
          end = s.find(")")
          employment = s[start+1:end-1].replace("u","").replace("'","")
          self.employment = employment

    @api.depends('age','birthday')
    def _compute_age(self):
        for r in self:
            if r.birthday:  
                today = date.today()
                month = datetime.strptime(r.birthday, '%Y-%m-%d').strftime('%m')
                year = datetime.strptime(r.birthday, '%Y-%m-%d').strftime('%Y')
                day = datetime.strptime(r.birthday, '%Y-%m-%d').strftime('%d')
                r.age = today.year - int(year) - ((today.month, today.day) < (int(month), int(day)))

    _defaults = {
 	               'country_id': lambda self, cr, uid, context: self.pool.get('res.country').browse(cr, uid, self.pool.get('res.country').search(cr,uid, [('code','=','MM')]))[0].id,  
    }
    
# class Hr_Contract(models.Model):
#   _inherit = 'hr.contract'
  
#   specail_allowance = fields.Float('Special Allowance')
#   trial_date_start = fields.Date(related='employee_id.trial_date_start',string="Date Start")
#   trial_date_end = fields.Date(related='employee_id.trial_date_end', string="Trial Date End")
#   department_id = fields.Many2one(related='employee_id.department_id',string="Department",store=True)
#   section_id = fields.Many2one(related='employee_id.section_id',string="Section",store=True)
#   sub_section_id = fields.Many2one(related='employee_id.sub_section_id', string="Sub Section",store=True)
#   active = fields.Boolean(related='employee_id.active', string='Active', store=True, copy=True)

#   insurance_amount = fields.Float('Insurance')
#   payment_type = fields.Selection([('cash', 'Cash'),
#                              ('mpu', 'MPU'),
#                              ('saving', 'Saving')],string="Payment Type")
#   shift_type = fields.Many2one('dutyroster.shift.group',string = "Shift Group")
#   sub_shift_type = fields.Many2one('dutyroster.shift.group',string = "Sub Group")
#   office_time = fields.Many2one('hr.employee.office.time',string = "Office Time")

#   _defaults = {'payment_type' : 'mpu'}

class Hr_Job(models.Model):

  _name = 'hr.job'
  _inherit = 'hr.job'

  name = fields.Char('Job Position (English)')
  burmese_name = fields.Char('Job Position (Burmese)')
  rank = fields.Selection(SELECTION_RANK,'Rank')
  is_above_supervisor = fields.Boolean('Is Above Supervisor')          

class Hr_Department(models.Model):

  _name = 'hr.department'
  _inherit = 'hr.department'
  
  name = fields.Char('Department Name (English)')
  burmese_name = fields.Char('Department Name (Burmese)')  
  
class Hr_Employee_Subject(models.Model):
    
    _name = 'hr.employee.subject'
    name = fields.Char('Subject', required=True)
    
class Hr_Employee_Degree(models.Model):
    
    _name = 'hr.employee.degree'
    name = fields.Char('Degree', required=True)

class Hr_Contract(models.Model):

  _inherit = 'hr.contract'

  is_permanent = fields.Boolean('Is Permanent',readonly=True) 
  permanent_date = fields.Date('Permanent Date')       
  
#Start 17/01/2018 KKW Add section and sub section field 
  
class Hr_LeaveRequest(models.Model):

  _inherit = 'hr.holidays'

  section_id = fields.Many2one("hr.section",string="Section",domain="[('department_id','=',department_id)]",readonly=False,store=True,)
  sub_section_id = fields.Many2one("hr.sub.section", string="Sub Section", domain="[('section_id', '=', section_id),('department_id','=',department_id)]",readonly=False,store=True,)

  def onchange_employee(self, cr, uid, ids, employee_id):
    result = {'value': {'department_id': False, 'section_id': False, 'sub_section_id': False}}
    if employee_id:
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
        result['value'] = {'department_id': employee.department_id.id, 'section_id': employee.section_id.id, 'sub_section_id': employee.sub_section_id.id}
    return result

#End 17/01/2018 KKW Add section and sub section field 

class res_users_city(models.Model):
    _name = 'res.partner.township'

    name = fields.Char("Name")

class res_users(models.Model):
    _inherit = 'res.partner'

    city = fields.Many2one("res.partner.township",string="Township")


