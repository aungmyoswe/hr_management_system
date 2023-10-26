from datetime import datetime , timedelta
from zklib import zklib
from openerp.tools.translate import _
import time
from zklib import zkconst
from openerp import models, api, fields
from openerp.osv import osv
# class hr_employee(osv.Model):
#     _name = "hr.employee"
#     _inherit = "hr.employee"

#     _columns = {
#         'emp_code': fields.char("Emp Code"),
#         'category': fields.char("category"),
#     }


class biometric_machine(models.Model):
    _name= 'biometric.machine'
    name = fields.Char('Machine IP')
    ref_name = fields.Char('Location')
    port = fields.Integer('Port Number')
    address_id = fields.Many2one('res.partner', 'Working Address')
    company_id = fields.Many2one('res.company', 'Company Name')
    atten_ids = fields.One2many('hr.fingerprint.attendance', 'machine_id', 'Attendance')
    history_ids = fields.One2many('biometric.machine.history', 'machine_id', 'History')
    date_download = fields.Datetime('Last Downloaded Date', readonly=True)
    date_clear = fields.Datetime('Last Clear Date', readonly = True)

    def download_attendance(self, cr, uid, ids, context=None):
        machine_ip = self.browse(cr,uid,ids).name
        port = self.browse(cr,uid,ids).port
        zk = zklib.ZKLib(machine_ip, int(port))
        res = zk.connect()
        if res == True:
            zk.enableDevice()
            zk.disableDevice()
            attendance = zk.getAttendance()
            hr_attendance =  self.pool.get("hr.fingerprint.attendance")
            hr_employee = self.pool.get("hr.employee") 
            # biometric_data = self.pool.get("biometric.data")
            total_record = len(attendance)
            if (attendance):
                # print '\n'
                # print '#####################################'
                # print 'OS Version: ', zk.osversion()
                # print 'Version : ', zk.version()
                # print 'Device Name : ', zk.deviceName()
                # print 'Users : ', zk.getUser()
                # print 'Attendance : ', len(attendance)
                # print '#####################################'
                # print '\n'
                for att in attendance:
                    att_date = att[2].date()
                    att_time = float(att[2].hour + float(att[2].minute)/60)
                    finger_id = str(att[0])
                    if att[3] == 0 or att[3] == 4:
                        action = "sign_in"
                    elif att[3] == 1 or att[3] == 5:
                        action = "sign_out"
                    try:
                        del_atten_ids = hr_attendance.search(cr,uid,[('fingerprint_id','=',finger_id),('name','=',att_date),('submit_time','=',att_time)])
                        if del_atten_ids:
                            print 'OLD : ', att_date, att[2].time()
                            # print "Date %s, Name %s: %s" % ( lattendance[2].date(), lattendance[2].time(), lattendance[0] )
                            continue
                        else:
                            print 'NEW : ', att_date, att[2].time()
                            employee_id = hr_employee.search(cr, uid, [('otherid','=',finger_id)])
                            if employee_id:                                
                                # data_val = {
                                #     'employee_id' : employee_id[0],
                                #     'otherid' : finger_id,
                                #     'att_date' : att_date,
                                #     'att_time' : att_time,
                                #     'machine_id' : ids[0],
                                #     'action' : action,
                                # }
                                # data_id = biometric_data.create(cr, uid, data_val)
                                att_val = {
                                    'employee' : employee_id[0],
                                    'fingerprint_id' : finger_id,
                                    'name' : att_date,
                                    'submit_time' : att_time,
                                    'action' : action,
                                    'machine_id' : ids[0],
                                }
                                attendance_id = hr_attendance.create(cr, uid, att_val)
                                self.write(cr, uid, ids[0], {'date_download':datetime.today()})
                    except Exception,e:
                        pass
                        print "exception..Attendance creation======", e.args
                obj_history = self.pool.get('biometric.machine.history')
                history_val = {
                    'machine_id' : ids[0],
                    'sub_date' : datetime.today(),
                    'action' : 'download',
                    'result' : total_record,
                }
                obj_history.create(cr, uid, history_val)

            zk.enableDevice()
            zk.disconnect()
            return True
        else:
            raise osv.except_osv(_('Warning !'),_("Unable to connect, please check the parameters and network connections."))

    #Dowload attendence data regularly
    def schedule_download(self, cr, uid, context=None):
        
            scheduler_line_obj = self.pool.get('biometric.machine')
            scheduler_line_ids = self.pool.get('biometric.machine').search(cr, uid, [])
            for scheduler_line_id in scheduler_line_ids:
                scheduler_line =scheduler_line_obj.browse(cr, uid,scheduler_line_id,context=None)   
                try:
                    scheduler_line.download_attendance()
                except:
                    raise osv.except_osv(('Warning !'),("Machine with %s is not connected" %(scheduler_line.name)))


    def clear_attendance(self, cr, uid, ids, context=None):
        machine_ip = self.browse(cr,uid,ids).name
        port = self.browse(cr,uid,ids).port
        zk = zklib.ZKLib(machine_ip, int(port))
        res = zk.connect()
        if res == True:
            zk.enableDevice()
            zk.disableDevice()
            self.write(cr, uid, ids[0], {'date_clear':datetime.today()})
            obj_history = self.pool.get('biometric.machine.history')
            history_val = {
                'machine_id' : ids[0],
                'sub_date' : datetime.today(),
                'action' : 'clear',
                'result' : 'Success',
            }
            obj_history.create(cr, uid, history_val)
            zk.enableDevice()
            zk.disconnect()
            return True
        else:
            raise osv.except_osv(_('Warning !'),_("Unable to connect, please check the parameters and network connections."))

class MachineHistory(models.Model):
    _name = "biometric.machine.history"
    _rec_name = 'machine_id'

    machine_id = fields.Many2one('biometric.machine', 'Machine No')
    sub_date = fields.Datetime('Date')
    action = fields.Selection([('download', 'Downlaod'), ('clear', 'Clear')], 'Action')
    result = fields.Char('Total Records')

class HrAttendance(models.Model):
    _name = "hr.fingerprint.attendance"
    _inherit = "hr.fingerprint.attendance"
    _order = 'id desc'

    machine_id = fields.Many2one('biometric.machine', 'Machine No')

# class HrAttendance(models.Model):
#     _name = "biometric.data"
#     _rec_name = 'employee_id'
#     _order = 'id desc'

#     employee_id = fields.Many2one('hr.employee','Employee')
#     otherid = fields.Char('Fingerprint ID')
#     att_date = fields.Date('Date')
#     att_time = fields.Float('Time')
#     machine_id = fields.Many2one('biometric.machine', 'Machine No')
#     action = fields.Selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out')], 'Action')

