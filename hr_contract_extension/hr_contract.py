from openerp import fields, models, api
from datetime import datetime, timedelta

class contract_init(models.Model):

    _name = 'hr.contract'
    _inherit = 'hr.contract'

    insurance_amount = fields.Float('Insurance')
    #is_permanent = fields.Boolean('Is Permanent') 
    #trining_status = fields.Selection(RESULT,'Training Status',default='0')
    year_end_increment = fields.Float('Year End Increment')
    year_end_date = fields.Date('Year End Date')
    previous_wage = fields.Float('Previous Salary')
    specail_allowance = fields.Float('Special Allowance')
    trial_date_end = fields.Date('Trial Start Date',compute='_compute_trial_date_end',store=True)
    #permanent_date = fields.Date('Permanent Date')
    payment_type = fields.Selection([('cash', 'Cash'),
                             ('mpu', 'MPU'),
                             ('saving', 'Saving')],string="Payment Type")
    # shift_type = fields.Selection([('morning', 'Morning'),
    #                                 ('evermorning', 'EverMorning'),
    #                                 ('evening', 'Evening'),
    #                                 ('everevening', 'EverEvening'),
    #                                 ('night', 'Night'),
    #                                 ('office', 'Office')],string="Shift Group", store=True)
    shift_type = fields.Many2one('dutyroster.shift.group',string = "Shift Group")
    sub_shift_type = fields.Many2one('dutyroster.shift.group',string = "Sub Group")
    office_time = fields.Many2one('hr.employee.office.time',string = "Office Time")
    #show_shift_group = fields.Boolean('Show Shift Group', compute="_compute_show_shift_group")

    job_id = fields.Many2one('hr.job', related='employee_id.job_id',string='Job Title',readonly=True)
    section_id = fields.Many2one(related='employee_id.section_id',string="Section",store=True)
    sub_section_id = fields.Many2one(related='employee_id.sub_section_id', string="Sub Section",store=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id',string='Department',readonly=True,store=True)
    active = fields.Boolean(related='employee_id.active',string='Active')
    is_hr_manager = fields.Boolean(compute="_is_hr_manager")
    is_above_supervisor = fields.Boolean(compute="_is_above_supervisor")

    _defaults = {'payment_type' : 'mpu'}

    # @api.one
    # @api.onchange('shift_type')
    # def _compute_show_shift_group(self):
    #     print '_compute_show_shift_group work'
    #     if self.shift_type:
    #         s = self.shift_type.name
    #         print 'shift_type ' + str(s)
    #         if "Office" in s:
    #             self.show_shift_group = True
    #         else:
    #             self.show_shift_group = False

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
            if not self.job_id.is_above_supervisor:
                self.is_above_supervisor = True

        print self.is_above_supervisor

    @api.one
    def _is_hr_manager(self):
      print '_is_hr_manager call'
      is_manager = True
      user = self.pool['res.users'].browse(self.env.cr, self.env.uid, self.env.uid, context=self.env.context)
      group_hr_manager_id = self.pool.get('ir.model.data').get_object_reference(self.env.cr, self.env.uid, 'base', 'group_hr_manager')[1]
      if group_hr_manager_id in [g.id for g in user.groups_id]:
        print 'is hr_manager'
        is_manager = False

      if self.employee_id.user_id.id == self.env.uid:
        is_manager = False

      self.is_hr_manager = is_manager

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

    def write(self, cr, uid, ids, vals, context=None):
        context = dict(context or {})
        print vals

        if "year_end_increment" in vals:
            record = self.pool.get('hr.contract').browse(cr,uid,ids)[0]
            total_wage = record.wage + vals['year_end_increment']
            #ot_rate = (total_wage*12)/(52 * 48)
            ot_rate = round(total_wage * 0.0048,2)
            vals.update({'wage': total_wage, 'ot_rate': ot_rate, 'previous_wage': record.wage})

        flag = super(contract_init, self).write(cr, uid, ids, vals, context=context)
        return flag

class Hr_Employee(models.Model):

    _name = 'hr.employee'
    _inherit = 'hr.employee'

    contract_count = fields.Integer('Contracts' , compute = '_contracts_count')
    count_number = fields.Integer(compute='_get_count_number')
    
    @api.depends('count_number')
    def _get_count_number(self):
        res = dict.fromkeys(self.ids, 0)
        print res
        for cou_id in self.ids:
            part_id = self.pool['hr.employee'].browse(self.env.cr, self.env.uid, cou_id, context=self.env.context)
            print part_id
            res[cou_id] = self.pool['assessment.record'].search_count(self.env.cr, self.env.uid, [('employee', '=', part_id.id)], context=self.env.context)
            self.count_number = res[cou_id]
        self.count_number = 1

    @api.one
    def _contracts_count(self):
        print 'child _contracts_count'
        contract = self.pool.get('hr.contract')
        count = contract.search_count(self.env.cr, self.env.uid,[('employee_id', '=', self.id)])
        print count
        self.contract_count = count

    def create(self, cr, uid, data, context=None):
        context = dict(context or {})
        if context.get("mail_broadcast"):
            context['mail_create_nolog'] = True

        employee_id = super(Hr_Employee, self).create(cr, uid, data, context=context)

        # assessment auto create
        assessment_obj = self.pool.get('assessment.record')
        record_value = {
                      'employee': employee_id,
        }
        assessment_obj.create(cr, uid, record_value, context=context)

        # contract auto create
        contract_obj = self.pool.get('hr.contract')
        salary_structure_obj = self.pool.get('hr.payroll.structure')
        name=str(data['name']+' Contract')

        #print data['parent_department_id']
        #salary_structure_ids = salary_structure_obj.search(cr,uid,[('department_id','=',data['department_id'])])
        #if not salary_structure_ids:
        #    print 'parent department'
        #    salary_structure_ids = salary_structure_obj.search(cr,uid,[('parent_department_id','in',data['parent_department_id'])])
        
        #print salary_structure_ids[0]
        contract_value = {
	        'name' : name,
	        'employee_id': employee_id,
            'department_id': data['department_id'],
	        'job_id' : data['job_id'],
            'trial_date_start': data['trial_date_start'],
	        'wage' : 0.0,
	        #'struct_id' : salary_structure_ids[0],
	        'type_id' : 1,
        	}
        print contract_value
        contract_obj.create(cr, uid, contract_value, context=context)

        if context.get("mail_broadcast"):
            self._broadcast_welcome(cr, uid, employee_id, context=context)
        return employee_id

