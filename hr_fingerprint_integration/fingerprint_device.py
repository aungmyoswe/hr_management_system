from datetime import datetime , timedelta
#from zk import ZK, const
from openerp.tools.translate import _
import time
from openerp import models, api, fields
from openerp.osv import osv

from sample import AttLogsSys
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

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
    count_number = fields.Integer('',compute='_get_count_number')
    count_number = fields.Integer('',compute='_get_count_number')
    
    @api.depends('count_number')
    def _get_count_number(self):
        res = dict.fromkeys(self.ids, 0)
        for app_id in self.ids:
            res[app_id] = self.pool['hr.fingerprint.attendance'].search_count(self.env.cr, self.env.uid, [('status','=', 'raw')], context=self.env.context)
            self.count_number = res[app_id]

    def time_format(self,et):
      if et != '0':
        e_hour = int(str(et).split('.')[0])
        e_min = str(et).split('.')[1]
        print 'e_hour ' + str(e_hour)
        print 'e_min ' + str(e_min)

        if len(e_min) == 1:
          e_min = int(e_min) * 0.1
        elif len(e_min) == 2:
          e_min = int(e_min) * 0.01
  
        e_min = int(round(round(round(e_min,2) % 1,2) * 60))
        print 'e_min round ' + str(e_min)
       
        a_et =  str(str(e_hour) + '.' + str(e_min))
        return a_et
      else:
        return 0

    def download_attendance__(self, cr, uid, ids, context=None):
        _logger.info('download_attendance work')
        machine_ip = self.browse(cr,uid,ids).name
        port = self.browse(cr,uid,ids).port
        #zk = ZK(machine_ip, int(port), 60)
        #zk = zk.connect()
        #print zk
        atts = AttLogsSys('zkemkeeper.ZKEM', machine_ip, port)
        is_connect = atts.connect()
        if is_connect:
            #zk.enable_device()
            #zk.disable_device()
            #attendance = zk.get_attendance()
            attendance = atts.getAllAttLogs()
            atts.disConnect()
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
                    finger_id = str(att[0])
                    att_date = att[1]
                    att_hour = float(att[2])
                    att_min = att[3]
                    att_time = float(att_hour + float(att_min)/60)

                    #if att.status == 0 or att.status == 4:
                    #    action = "sign_in"
                    #elif att.status == 1 or att.status == 5:
                    #    action = "sign_out"
                    action = ''

                    try:
                        del_atten_ids = hr_attendance.search(cr,uid,[('fingerprint_id','=',finger_id),('name','=',att_date),('submit_time','=',att_time)]) #, ('action','=',action)
                        if del_atten_ids:
                            #_logger.info('OLD')
                            #print 'OLD : ', att_date, timestamp.time()
                            print 'fingerprint : ' + str(finger_id)
                            print 'att_date    : ' + str(att_date)
                            print 'att_time    : ' + str(att_time)
                            print 'action      : ' + str(action)
                            employee_id = hr_employee.search(cr, uid, [('otherid','=',finger_id)])
                            _logger.info('employee_id: ' + str(employee_id))
                            # print "Date %s, Name %s: %s" % ( lattendance[2].date(), lattendance[2].time(), lattendance[0] )
                            continue
                        else:
                            #_logger.info('NEW')
                            #print 'NEW : ', att_date, timestamp.time()
                            print 'Fingerprint : ' + str(finger_id)
                            employee_id = hr_employee.search(cr, uid, [('otherid','=',finger_id)])
                            _logger.info('employee_id: ' + str(employee_id))
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
                                    'status' : 'raw',
                                    #'detail_status': 'raw'
                                }
                                attendance_id = hr_attendance.create(cr, uid, att_val)
                                print '-----------------------------'
                                print '>>>> create ' + str(finger_id)
                                print '-----------------------------'
                                self.write(cr, uid, ids[0], {'date_download':datetime.today()})
                            else:
                                print '-----------------------------'
                                print '>>>> skip ' + str(finger_id)
                                print '-----------------------------'
                    except Exception,e:
                        pass
                        print "exception..Attendance creation======", e.args
                obj_history = self.pool.get('biometric.machine.history')
                history_val = {
                    'machine_id' : ids[0],
                    'sub_date' : datetime.today(),
                    'action' : 'download',
                    'result' : str(total_record),
                }
                obj_history.create(cr, uid, history_val)

            #zk.enable_device()
            #zk.disconnect()

            return True
        else:
            raise osv.except_osv(_('Warning !'),_("Unable to connect, please check the parameters and network connections."))

    def attendance_sequence(self, cr, uid, ids, context=None):
        attendance_obj = self.pool.get('hr.fingerprint.attendance')
        raw_attendance_ids = attendance_obj.search(cr,uid,[('status','=','raw')])
        raw_attendance_objs = attendance_obj.browse(cr, uid, raw_attendance_ids)

        count = 0
        skip_lists = []
        for att in raw_attendance_objs:
          count = count + 1
          before_attendance_ids = []
          att_list = []
          skip_list = []

          if skip_lists and att.id in skip_lists[0]:
            continue

          sql = "SELECT id,name,submit_time FROM hr_fingerprint_attendance WHERE employee=%s AND name=%s AND status=%s" # ORDER BY submit_time
          cr.execute(sql, (att.employee.id, att.name, 'raw'))
          attendances = cr.fetchall()

          attendance_ids = []
          for attendance in attendances:
            attendance_ids.append(attendance[0])

          if len(attendance_ids) >= 2:
            templist = []
            tempdic = {}

            before_attendance_ids = attendance_ids
            attendance_objs = attendance_obj.browse(cr, uid, attendance_ids)

            print 'before_attendance_ids ' + str(before_attendance_ids)
            for i in attendance_objs:
              tempdic[str(i.id)] = round(i.submit_time,2)
            templist = sorted(tempdic.values(), key=float)

            attendance_ids = []
            for i in templist:
              attendance_ids.append(int(tempdic.keys()[tempdic.values().index(i)]))

            print attendance_obj.write(cr, uid, attendance_ids[0],{'action':'sign_in','status':'sequence'},context)
            print attendance_obj.write(cr, uid, attendance_ids[-1],{'action':'sign_out','status':'sequence'},context)

            att_list.append(attendance_ids[0])
            att_list.append(attendance_ids[-1])
            skip_lists.append(attendance_ids)

            print 'attendance [0][1] ' + str(att_list)
            for before_attendance in before_attendance_ids:
              print before_attendance
              if before_attendance not in att_list:
                skip_list.append(before_attendance)
            
            #attendance_obj.unlink(cr,uid, skip_list)
            print 'attendance skip_list ' + str(skip_list)
            print attendance_obj.write(cr, uid, skip_list,{'action':'','status':'sequence'},context)
          else:
            today = datetime.today()
            att_day = datetime.strptime(att.name,'%Y-%m-%d')
            if today > att_day:
              diff = today - att_day
              if diff.days > 30:
                print attendance_obj.write(cr, uid, attendance_ids,{'action':'','status':'sequence'},context)

          _logger.info('>>> count ' + str(count))

    # First Time Generate - check attendace detail flag in attendance
    # Next Time Generate  - check raw flag in leave request, travel request and onduty request
    def attendance_detail_report(self, cr, uid, ids, context=None):
        _logger.info('attendance_detail_report work')
        attendance_obj = self.pool.get('hr.fingerprint.attendance')
        attendance_detail_obj = self.pool.get('hr.attendance.detail')
        office_time_obj = self.pool.get('hr.employee.office.time')
        contract_obj = self.pool.get('hr.contract')
        leave_obj = self.pool.get('hr.holidays')
        trip_obj = self.pool.get('hr.travel.request')
        duty_obj = self.pool.get('hr.onduty.request')
        att_history = self.pool.get('hr.attendance.history')

        #trip_ids = trip_obj.search(cr,uid,[('status','=','raw')])
        #leave_ids = leave_obj.search(cr,uid,[('status','=','raw')])
        #duty_ids = duty_obj.search(cr,uid,[('status','=','raw')])

        #trip_objs = trip_obj.browse(cr,uid,trip_ids)
        #leave_objs = leave_obj.browse(cr,uid,leave_ids)
        #duty_objs = duty_obj.browse(cr,uid,duty_ids)

        # for trip in trip_objs:
        #   print trip.from_date
        #   print trip.to_date
        #   day_from = datetime.strptime(str(trip.from_date), "%Y-%m-%d %H:%M:%S")
        #   day_to = datetime.strptime(str(trip.to_date), "%Y-%m-%d %H:%M:%S")
        #   nb_of_days = (day_to - day_from).days + 1

        #   detail_id = None
        #   for day in range(0,nb_of_days):
        #     w_day = day_from + timedelta(days=day)
        #     detail_ids = attendance_detail_obj.search(cr,uid,[('employee','=',trip.employee_id.id),('calculateddate','=',w_day)])
        #     print 'detail_ids ' + str(detail_ids)
        #     if detail_ids:
        #       detail_id = attendance_detail_obj.write(cr, uid, detail_ids, {'ontrip':'1','onduty':'0','leave':'0','reason':'onTrip'},context)
        #       print 'detail_id ' + str(detail_id)
          
        #   if detail_id:
        #     print 'trip.id ' + str(trip.id)
        #     print trip_obj.write(cr, uid, trip.id, {'status':'sequence'},context)

        # for duty in duty_objs:
        #   print duty.from_date
        #   print duty.to_date
        #   day_from = datetime.strptime(str(duty.from_date), "%Y-%m-%d")
        #   day_to = datetime.strptime(str(duty.to_date), "%Y-%m-%d")
        #   nb_of_days = (day_to - day_from).days + 1

        #   detail_id = None
        #   for day in range(0,nb_of_days):
        #     w_day = day_from + timedelta(days=day)
        #     detail_ids = attendance_detail_obj.search(cr,uid,[('employee','=',duty.employee_id.id),('calculateddate','=',w_day)])
        #     print 'detail_ids ' + str(detail_ids)
        #     if detail_ids:
        #       detail_id = attendance_detail_obj.write(cr, uid, detail_ids, {'ontrip':'0','onduty':'1','leave':'0','reason':'onDuty'},context)
        #       print 'detail_id ' + str(detail_id)
          
        #   if detail_id:
        #     print 'duty.id ' + str(duty.id)
        #     print duty_obj.write(cr, uid, duty.id, {'status':'sequence'},context)

        # for leave in leave_objs:
        #   day_from = datetime.strptime(str(leave.date_from), "%Y-%m-%d %H:%M:%S")
        #   day_to = datetime.strptime(str(leave.date_to), "%Y-%m-%d %H:%M:%S")
        #   nb_of_days = (day_to - day_from).days + 1

        #   detail_id = None
        #   for day in range(0,nb_of_days):
        #     w_day = day_from + timedelta(days=day)
        #     detail_ids = attendance_detail_obj.search(cr,uid,[('employee','=',leave.employee_id.id),('calculateddate','=',w_day)])
        #     print 'detail_ids ' + str(detail_ids)
        #     if detail_ids:

        #       leave_type = ""
        #       if leave.number_of_days_temp >= 1:
        #         leave_type = 'Full'
        #         leave_day = 1
        #       elif leave.number_of_days_temp < 1:
        #         leave_type = 'Half'
        #         leave_day = 0.5
                           
        #       reason = str(leave.holiday_status_id.name) + ' (' + leave_type + ')'

        #       detail_id = attendance_detail_obj.write(cr, uid, detail_ids, {'ontrip':'0','onduty':'0','leave':leave_day,'reason':reason},context)
        #       print 'detail_id ' + str(detail_id)
          
        #   if detail_id:
        #     print 'leave.id ' + str(leave.id)
        #     print leave_obj.write(cr, uid, leave.id, {'status':'sequence'},context)

        # all sequence attendance and date range between leave,travel,onduty
        attendance_ids = attendance_obj.search(cr,uid,[('status','=','sequence'),('detail_status','=','raw')]) #1 , ('history_id','=', history_id) 
        attendance_objs = attendance_obj.browse(cr, uid, attendance_ids)

        print '--------------------------------------'
        print 'raw len ' + str(len(attendance_ids))
        print 'raw att ' + str(attendance_ids)
        print 'raw obj ' + str(attendance_objs)

        detail_value = {}
        att_list = []
        skip_list = []
        skip_count = 0
        count = 0
        detail_count = 0
        
        # First Attendance
        for att in attendance_objs:
            skip_count += 1

            att_id = att.id
            emp_id = att.employee.id
            emp_name = att.employee.name_related
            emp_code = att.employee.emp_id
            department_id = att.employee.department_id
            finger_id = att.fingerprint_id
            att_date = att.name
            
            if emp_id in att_list:
                #print 'skip ' + str(emp_id)
                #print 'skip_count ' + str(skip_count)
                continue

            count += 1

            contract_id = contract_obj.search(cr,uid,[('employee_id','=', emp_id)])
            contract_objs = contract_obj.browse(cr, uid, contract_id)

            print '--------------------------------------'
            print 'att_id    ' + str(att_id)
            print 'emp_id    ' + str(emp_id)
            print 'emp_name  ' + str(emp_name)
            print 'emp_code  ' + str(emp_code)
            print 'depart_id ' + str(department_id)
            print 'contr_id  ' + str(contract_id)
            print 'finger_id ' + str(finger_id)
            print 'att_date  ' + str(att_date)

            # must raw employee , call once and keep overlap employee call 30
            raw_emp_ids = attendance_obj.search(cr,uid,[('employee','=', emp_id),('status','=','sequence'),('detail_status','=','raw')], order='id asc') #,order='id asc' ('status','=', 'sequence'),
            attendance_flag = attendance_obj.write(cr, uid, raw_emp_ids,{'detail_status':'sequence'},context)
            att_list.append(emp_id)
            print 'raw_emp_ids ' + str(raw_emp_ids)
            
            if raw_emp_ids and attendance_flag:
              date_from = attendance_obj.browse(cr, uid, raw_emp_ids[0]).name
              date_to = attendance_obj.browse(cr, uid, raw_emp_ids[-1]).name
              raw_emp_objs = attendance_obj.browse(cr, uid, raw_emp_ids)
          
              print 'raw emp len ' + str(len(raw_emp_ids))
              print 'raw emp att ' + str(raw_emp_ids)
              print 'raw emp obj ' + str(raw_emp_objs)
  
              day_from = datetime.strptime(str(date_from), "%Y-%m-%d")
              day_to = datetime.strptime(str(date_to), "%Y-%m-%d")
              nb_of_days = (day_to - day_from).days + 1
  
              print 'day_from ' + str(day_from)
              print 'day_to ' + str(day_to)
              print 'nb_of_days ' + str(nb_of_days)
              
              #raise ValidationError('')
              for day in range(0,nb_of_days):
                  detail_count += 1
                  
                  reason = ""
                  remark = ""
                  leave = 0
                  onduty = 0
                  ontrip = 0
                  late = 0
                  attendance = 0
                  absent = 0
                  #earlyot = 0
                  #earlyout = 0
                  ot = 0
                  
                  w_day = day_from + timedelta(days=day)
                  print 'w_day ' + str(w_day)

                  s = str(w_day)
                  detail_day = s[:str(w_day).find(' ')]
                  print 'detail_day ' + str(detail_day)
  
                  l_f_date = (str(w_day).split(' ')[0] + ' 23:59:59')
                  #print 'l_f_date ' + str(l_f_date)
  
                  leave_ids = leave_obj.search(cr, uid, [('employee_id','=', emp_id),('date_from','<=', l_f_date),('date_to','>=',str(w_day))]) #,('status','=','raw')                  
                  if leave_ids:
                    print 'leave found'
                    leave_objs = leave_obj.browse(cr, uid, leave_ids)
                    leave_type = ""
                    if leave_objs.number_of_days_temp >= 1:
                        leave_type = 'Full'
                        leave = 1
                    elif leave_objs.number_of_days_temp < 1:
                        leave_type = 'Half'
                        leave = 0.5
                           
                    reason = str(leave_objs.holiday_status_id.name) + ' (' + leave_type + ')'

                  # trip_ids = trip_obj.search(cr, uid, [('employee_id','=', emp_id),('from_date','<=', l_f_date),('to_date','>=',str(w_day)),('status','=','raw')])                 
                  # if trip_ids:
                  #   print 'trip found'
                  #   reason = 'onTrip '
                  #   ontrip = 1

                  # duty_ids = duty_obj.search(cr, uid, [('employee_id','=', emp_id),('from_date','<=', l_f_date),('to_date','>=',str(w_day)),('status','=','raw')])                 
                  # if duty_ids:
                  #   print 'duty found'
                  #   reason = 'onDuty '
                  #   onduty = 1

                  print 'count >>> ' + str(count)
                  print 'detail_count >>> ' + str(detail_count)
  
                  print contract_objs
                  print contract_objs.office_time
                  shift_code = contract_objs.office_time.code
                  print 'shift_code ' + str(shift_code)
                  shift_name = contract_objs.office_time.name
                  print 'shift_name ' + str(shift_name)
                  time_start = contract_objs.office_time.time_start
                  print 'time_start ' + str(time_start)
                  time_end = contract_objs.office_time.time_end
                  print 'time_end ' + str(time_end)
                  #eot_start = contract_objs.shift.eot_start
                  #print 'eot_start ' + str(eot_start)
                  #eot_end = contract_objs.shift.eot_end
                  #print 'eot_end ' + str(eot_end)
                  late_start = contract_objs.office_time.late_start
                  print 'late_start ' + str(late_start)
                  late_end = contract_objs.office_time.late_end
                  print 'late_end ' + str(late_end)
                  #early_out = contract_objs.shift.early_out
                  #print 'early_out ' + str(early_out)
                  ot_start = contract_objs.office_time.ot_start
                  print 'ot_start ' + str(ot_start)
                  ot_end = contract_objs.office_time.ot_end
                  print 'ot_end ' + str(ot_end)

                  for a in attendance_obj.search(cr,uid,[('employee','=',emp_id),('name','=',detail_day)]):
                    t_remark = attendance_obj.browse(cr, uid, a).reason
                    if t_remark:
                        remark += t_remark
    
                  detail_value = {
                                      'employee': emp_id,
                                      'enrollnumber': finger_id,
                                      'location': department_id.id,
                                      'employeecode': emp_code,
                                      'employeename': emp_name,
                                      'calculateddate': detail_day,
                                      'shiftcode': shift_code,
                                      'shiftname': shift_name,
                                      'dayin': time_start,
                                      'dayout': time_end,
                                      'leave': str(leave),
                                      'attendance': str(attendance),
                                      'absent': str(absent),
                                      'onduty': str(onduty),
                                      'ontrip': str(ontrip),
                                      'late': str(late),
                                      'ot': str(ot),
                                      'reason': reason, 
                                      'remark': remark,
                                      #'history_id': history_id
                                  }
      
                  print detail_value
                  
                  detail_sign_in = None
                  detail_sign_out = None
                  raw_signin_obj = None
                  raw_signout_obj = None

                  #first employee attendance
                  #if may search 3 times check by flag
                  #2 time may this employee this date
                  raw_sign_in = attendance_obj.search(cr,uid,[('employee','=',emp_id),('name','=',detail_day),('action','=','sign_in')])
                  print 'raw_sign_in ' + str(raw_sign_in)
                  raw_sign_out = attendance_obj.search(cr,uid,[('employee','=',emp_id),('name','=',detail_day),('action','=','sign_out')])
                  print 'raw_sign_out ' + str(raw_sign_out)

                  if raw_sign_in:
                      #detail_sign_in = attendance_detail_obj.search(cr,uid,[('employee','=',emp_id),('calculateddate','=',detail_day),('action_signin','=', True)])
                      #print 'detail_sign_in ' + str(detail_sign_in)
                      
                      #if not detail_sign_in:
                    raw_signin_obj = attendance_obj.browse(cr, uid, raw_sign_in[0])
                    print 'raw_signin_obj ' + str(raw_signin_obj)
                    print 'raw_signin_submittime ' + str(raw_signin_obj.submit_time)
                    sign_in = round(raw_signin_obj.submit_time,2)
      
                    if sign_in > late_start and sign_in < late_end:
                        print 'late'
                        late = 1
                        # elif sign_in < time_start and sign_in >= eot_end:
                        #     print 'early ot'
                        #     earlyot = time_start - sign_in
      
                    detail_value.update({'intime': self.time_format(round(raw_signin_obj.submit_time,2)),
                                         #'action_signin': True,
                                         'late': str(late),
                                         #'earlyot': str(earlyot)
                                        })
                  else:
                      print 'No SignIn'
      
                  if raw_sign_out:
                      #detail_sign_out = attendance_detail_obj.search(cr,uid,[('employee','=',emp_id),('calculateddate','=',detail_day),('action_signout','=', True)])
                      #print 'detail_sign_out ' + str(detail_sign_out)
      
                      #if not detail_sign_out:
                    raw_signout_obj = attendance_obj.browse(cr, uid, raw_sign_out[0])
                    print 'raw_signout_obj ' + str(raw_signout_obj)
                    print 'raw_signout_submittime ' + str(raw_signout_obj.submit_time)
                          
                    sign_out = round(raw_signout_obj.submit_time,2)
      
                          # if sign_out < early_out:
                          #     print 'early_out'
                          #     earlyout = early_out - sign_out
                    if sign_out > ot_start and sign_out < ot_end:
                        print 'ot'
                        ot = sign_out - ot_start
      
                    detail_value.update({'outtime': self.time_format(round(raw_signout_obj.submit_time,2)),
                                         #'action_signout': True,
                                         #'earlyout': str(earlyout),
                                         'ot': str(ot)
                                        })
                  else:
                      print 'No SignOut'
      
                  print '-----------------------------------'
                  print 'detail_sign_in ' + str(detail_sign_in)
                  print 'detail_sign_out ' + str(detail_sign_out)
                  
                  #TO DO Absent
                  print detail_value['leave']
                  has_leave = int(detail_value['leave']) > 0
                  has_ontrip = int(detail_value['ontrip']) > 0 
                  has_onduty = int(detail_value['onduty']) > 0

                  print 'has_leave ' + str(has_leave)
                  print 'has_ontrip ' + str(has_ontrip)
                  print 'has_onduty ' + str(has_onduty)

                  if not raw_sign_in and not raw_sign_out and not has_leave and not has_ontrip and not has_onduty:
                      print detail_value
                      # check sun and sat day
                      detail_value.update({'absent':1})

                  if raw_sign_in and raw_sign_out:
                      print detail_value
                      detail_value.update({'attendance':1})
                  
                  #if raw_sign_in or raw_sign_out:
                  print detail_value
                  detail_id = attendance_detail_obj.create(cr, uid, detail_value,context)
                  print 'detail_id ' + str(detail_id)
                  _logger.info('>>> Detail ID Created')

    def download_attendance(self, cr, uid, ids, context=None):
        print '>>> download_attendance'
        _logger.info('>>> download_attendance')
        att_history = self.pool.get('hr.attendance.history')
        hr_attendance =  self.pool.get("hr.fingerprint.attendance")
        hr_employee = self.pool.get("hr.employee")
        machine_ip = self.browse(cr,uid,ids).name
        port = self.browse(cr,uid,ids).port
        atts = AttLogsSys('zkemkeeper.ZKEM', machine_ip, int(port))
        is_connect = atts.connect()

        logUser = atts.getAllUserInfo()
        #logUser = [(u'1', u'028'), (u'6', u'220'), (u'7', u'079'), (u'8', u'191')]

        if logUser:
          for user in logUser:
            #raise ValidationError('' + str(user))
            fingerprint_id = user[0]
            emp_id = user[1]
            fingerprint_output_name = emp_id
            fingeprint_name = None

            record = self.pool.get('biometric.machine').browse(cr,uid,ids)[0]
            company_name = record.company_id.name
            system_emp_id = None
            
            if str(emp_id).isdigit():
              # it ytci
              if 'ytci' in company_name.lower():
                zero = 0
                if emp_id[0] == '0':
                    zero = 1
                    if emp_id[1] == '0':
                        zero = 2
                        if emp_id[2] == '0':
                            zero = 3
                            if emp_id[3] == '0':
                                zero = 4
                emp_id = emp_id[zero:]

                #raise ValidationError(emp_id)

                employee_ids = hr_employee.search(cr,uid,[('emp_id','=',emp_id)])
                employee_objs = hr_employee.browse(cr,uid,employee_ids)
                system_emp_id = employee_objs.emp_id

                #raise ValidationError('id ' + str(emp_id) + 'fingeprint ' + str(employee_objs.otherid) + ' - ' + str(fingerprint_id) )

                if system_emp_id and system_emp_id == emp_id:
                    # it emp_id Have and Match
                    if employee_objs.otherid and employee_objs.otherid == fingerprint_id:
                        # skip
                        print 'skip'
                        _logger.info('>>> skip')
                    else:
                        # old write
                        hr_employee.write(cr,uid,employee_ids,{'otherid': fingerprint_id,'fingerprint_name': fingerprint_output_name})
                        _logger.info('>>> old_write')

            elif fingerprint_id:
              # it cci or zarla

              if 'cho' in company_name.lower():
                zero_dic = {'1': '00','2': '0'}
                if len(fingerprint_id) < 3:
                  system_emp_id = zero_dic.get(str(len(fingerprint_id))) + fingerprint_id
                  #raise ValidationError('' + fingerprint_id)

              if 'zar' in company_name.lower():
                zero_dic = {'1': '000','2': '00','3': '0'}
                if len(fingerprint_id) < 4:
                  system_emp_id = zero_dic.get(str(len(fingerprint_id))) + fingerprint_id

              employee_ids = hr_employee.search(cr,uid,[('emp_id','=', system_emp_id)])
              if len(employee_ids) > 1:
                #raise ValidationError('Duplicate Employee ID -> ' + str(fingerprint_id))
                print 'Duplicate Employee ID'
                employee_ids = employee_ids[0]
                
              employee_objs = hr_employee.browse(cr,uid,employee_ids)
              fingeprint_name = emp_id

              if employee_objs.otherid == fingerprint_id:
                hr_employee.write(cr,uid,employee_ids,{'fingerprint_name': fingeprint_name})
                _logger.info('>>> update_fingerprint_name')
              else:
                  #print '>>> Fingerprint ID and Name Not Exist !'
                  hr_employee.write(cr,uid,employee_ids,{'otherid': fingerprint_id,'fingerprint_name': fingeprint_name})

        #raise ValidationError('')

        total_record = atts.getAllAttLogs()
        atts.disConnect()

        if is_connect: 
            if len(total_record) > 0:
                for att in total_record:
                    #print '----------------------------'
                    #print 'att ' + str(att)
                    finger_id = str(att[0])
                    att_date = att[1]
                    att_hour = att[2]
                    att_min = att[3]
                    status = int(att[4])
                    att_time = float(float(att_hour) + float(att_min)/60)

                    # if status == 0 or status == 4:
                    #     action = "sign_in"
                    # elif status == 1 or status == 5:
                    #     action = "sign_out"
                    action = ''
                        
                    # print 'finger_id ' + str(finger_id)
                    # print 'att_date  ' + str(att_date)
                    # print 'att_time  ' + str(att_time)
                    # print 'action    ' + str(action)
                    # _logger.info(finger_id)
                    # _logger.info(att_date)
                    # _logger.info(att_time)
                    # _logger.info(action)

                    try:
                        del_atten_ids = hr_attendance.search(cr,uid,[('fingerprint_id','=',finger_id),('name','=',att_date),('submit_time','=',att_time)]) # ('action','=',action)
                        if del_atten_ids:
                            #_logger.info('OLD')
                            #print 'OLD : ', att_date, timestamp.time()
                            # print 'fingerprint : ' + str(finger_id)
                            # print 'att_date    : ' + str(att_date)
                            # print 'att_time    : ' + str(att_time)
                            # print 'action      : ' + str(action)
                            employee_id = hr_employee.search(cr, uid, [('otherid','=',finger_id)])
                            _logger.info('employee_id: ' + str(employee_id))
                            # print "Date %s, Name %s: %s" % ( lattendance[2].date(), lattendance[2].time(), lattendance[0] )
                            continue
                        else:
                            #_logger.info('NEW')
                            #print 'NEW : ', att_date, timestamp.time()
                            #print 'Fingerprint : ' + str(finger_id)
                            employee_id = hr_employee.search(cr, uid, [('otherid','=',finger_id)])
                            _logger.info('employee_id: ' + str(employee_id))
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
                                    'status' : 'raw',
                                    #'detail_status': 'raw'
                                }
                                attendance_id = hr_attendance.create(cr, uid, att_val)
                                print '-----------------------------'
                                print '>>>> create ' + str(finger_id)
                                print '-----------------------------'
                                self.write(cr, uid, ids[0], {'date_download':datetime.today()})
                            else:
                                print '-----------------------------'
                                print '>>>> skip ' + str(finger_id)
                                print '-----------------------------'
                    except Exception,e:
                        pass
                        print "exception..Attendance creation======", e.args

                obj_history = self.pool.get('biometric.machine.history')
                history_val = {
                  'machine_id' : ids[0],
                  'sub_date' : datetime.today(),
                  'action' : 'download',
                  'result' : str(len(total_record)),
                }
                obj_history.create(cr, uid, history_val)
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
        zk = ZK(machine_ip, int(port), 60)
        zk = zk.connect()
        if zk:
            zk.enable_device()
            zk.disable_device()
            zk.clear_attendance()
            self.write(cr, uid, ids[0], {'date_clear':datetime.today()})
            obj_history = self.pool.get('biometric.machine.history')
            history_val = {
                'machine_id' : ids[0],
                'sub_date' : datetime.today(),
                'action' : 'clear',
                'result' : 'All'
            }
            obj_history.create(cr, uid, history_val)
            
            zk.enable_device()
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