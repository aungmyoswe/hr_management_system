from openerp import fields, models, api
from openerp.exceptions import ValidationError

class Shift(models.Model):
    _name = "hr.employee.shift"
    _rec_name = 'code'
    
    name = fields.Char("Name", required=True)
    code = fields.Char("Code", required=True)
    time_start = fields.Float("Start", required=True)
    time_end = fields.Float("End", required=True)
    time_break = fields.Float("Break", required=True)
    description = fields.Text("Description")
    duration = fields.Float("Duration", compute="_compute_duration")

    eot_start = fields.Float("Early OT Start", required=True)
    eot_end = fields.Float("Early OT End", required=True)
    ot_start = fields.Float("OT Start", required=True)
    ot_end = fields.Float("OT End", required=True)
    late_start = fields.Float("Late Start", required=True)
    late_end = fields.Float("Late End", required=True)
    early_out = fields.Float("Early Out", required=True)
    
    @api.one
    @api.depends('time_start','time_end')
    def _compute_duration(self):
    	dur = 0
    	if(self.time_start and self.time_end):
    		dur = self.time_end - self.time_start
    		if dur < 0:
    			dur = dur + 24
    	self.duration = dur
      
class HrOfficeTime(models.Model):
    _name = 'hr.employee.office.time'
    _rec_name = 'code'
    
    name = fields.Char('Name',required=True)
    code = fields.Char('Code',required=True)
    time_start = fields.Float("Start", required=True)
    time_end = fields.Float("End", required=True)
    description = fields.Text("Description")

    ot_start = fields.Float("OT Start", required=True)
    ot_end = fields.Float("OT End", required=True)
    late_start = fields.Float("Late Start", required=True)
    late_end = fields.Float("Late End", required=True)

    @api.multi
    def name_get(self):
        print 'HrOfficeTime name_get() Call'
        res = super(HrOfficeTime, self).name_get()
        data = []
        for office in self:
            display_value = ''
            display_value += str(office.name) or ""
            display_value += ' [ '
            display_value += str(office.time_start)
            display_value += ' - '
            display_value += str(office.time_end)
            display_value += ' ]'
            data.append((office.id, display_value))
        return data

class ShiftGroup(models.Model):
    _name = 'dutyroster.shift.group'

    name = fields.Char('Name', required=True)
    #sat_shift_id = fields.Many2one('hr.employee.shift', string="Saturday Shift", required=True)
    note = fields.Text('Note')

class GroupDayOff(models.Model):
    _name = 'dutyroster.group.dayoff'

    group_id = fields.Many2one('dutyroster.shift.group',string = "Group Name")
    date = fields.Date("Date", required=True)
    #date_from = fields.Date("From Date", required=True)
    #date_to = fields.Date("To Date", required=True)
    reason = fields.Text('Reason')

    



