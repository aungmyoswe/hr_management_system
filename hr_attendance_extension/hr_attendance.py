from openerp import api, models, fields
from openerp.exceptions import ValidationError

class HrFingerprintAttendance(models.Model):    
	_name = 'hr.fingerprint.attendance'
	_order = 'name,submit_time desc'

	fingerprint_id = fields.Char("Fingerprint ID", compute="_compute_fingerprint", store=True)
	employee = fields.Many2one('hr.employee', string='Employee',required=True, store=True, readonly=False) 
	department_name = fields.Char(related='employee.department_id.name',string='Department', store=True)
	name = fields.Date('Date', required=True)
	action = fields.Selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out')], 'Action', required=True)
	submit_time = fields.Float('Time', required=True)
	reason = fields.Text('Reason')
	status = fields.Selection([('raw', 'Raw'), ('sequence', 'Sequence')], 'Attendance Status')
	detail_status = fields.Selection([('raw', 'Raw'), ('sequence', 'Sequence')], 'Detail Report Status')

	@api.one
	@api.depends('employee')
	def _compute_fingerprint(self):
		self.fingerprint_id = self.employee.otherid

	def attendance_check_create(self, cr,uid,ids, context=None):
		attendances = []
		print "---------------------CHECK CREATE-------------------"
		cr.execute("SELECT id FROM hr_fingerprint_attendance order by id asc;")
		attendances = cr.fetchall()
		print attendances
		for row in attendances:
			print row[0]
			result_ids = self.search(cr, uid, [('id','=',row[0])])
			result_ids = self.browse(cr, uid, result_ids)
			result_ids._attendance_check()

class HrAttendanceDetail(models.Model):    
 	_name = 'hr.attendance.detail'

	employee = fields.Many2one('hr.employee',"Employee")
	enrollnumber = fields.Char("EnrollNumber")
	location = fields.Many2one('hr.department',"Location")
	employeecode = fields.Char("EmployeeCode")
	employeename = fields.Char("EmployeeName")
	calculateddate = fields.Date("CalculatedDate")
	shiftcode = fields.Char("ShiftCode")
	shiftname = fields.Char("ShiftName")
	dayin = fields.Char("DutyIn")
	dayout = fields.Char("DutyOut")
	#action_signin = fields.Boolean("Action SignIn")
	#action_signout = fields.Boolean("Action SignOut")
	intime = fields.Char("InTime")
	outtime = fields.Char("OutTime")
	#workinghours = fields.Char("WorkingHours")
	#earlyot = fields.Char("EarlyOT")
	#earlyout = fields.Char("EarlyOut")
	attendance = fields.Float("Attendance")
	leave = fields.Float("Leave")
	offday = fields.Char("OffDay")
	absent = fields.Float("Absent")
	onduty = fields.Float("OnDuty")
	ontrip = fields.Float("OnTrip")
	late = fields.Float("Late")
	ot = fields.Float("OT")
	# onDuty,onTrip,Absent or Leave Type (Full/Half)
	reason = fields.Char("Reason")
	# Travel Reason, On Duty Reason, Attendance Reason
	remark = fields.Char("Remark")

	def write(self, cr, uid, ids, vals, context=None):
		context = dict(context or {})
		print 'HrAttendanceDetail Write Call'

		attendance_obj = self.pool.get('hr.fingerprint.attendance')
		record = self.pool.get('hr.attendance.detail').browse(cr, uid, ids)[0]
		#print record
		#print record.employee
		#print record.calculateddate
		#print vals
		if 'intime' in vals:
			print 'intime ' + str(vals['intime'])
			attendance_id = attendance_obj.search(cr,uid,[('employee','=', record.employee.id),('action','=','sign_in'),('name','=', record.calculateddate)])
			attendance_obj.write(cr,uid,attendance_id, {'submit_time': vals['intime']})
		if 'outtime' in vals:
			print 'outtime ' + str(vals['outtime'])
			attendance_id = attendance_obj.search(cr,uid,[('employee','=', record.employee.id),('action','=','sign_out'),('name','=', record.calculateddate)])
			attendance_obj.write(cr,uid,attendance_id, {'submit_time': vals['outtime']})

		flag = super(HrAttendanceDetail, self).write(cr, uid, ids, vals, context=context)
		return flag


		


