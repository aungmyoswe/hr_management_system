from openerp import fields, models
from datetime import datetime, date, timedelta
from openerp.exceptions import ValidationError

class attendance_detail_wizard(models.TransientModel):
    _name = 'attendance.detail.wizard'

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To",default=datetime.today())

    def time_format(self,et):
      if et != '0':
        e_hour = int(str(et).split('.')[0])
        e_min = str(et).split('.')[1]
        #print 'e_hour ' + str(e_hour)
        #print 'e_min ' + str(e_min)

        if len(e_min) == 1:
          e_min = int(e_min) * 0.1
        elif len(e_min) == 2:
          e_min = int(e_min) * 0.01
  
        e_min = int(round(round(round(e_min,2) % 1,2) * 60))
        #print 'e_min round ' + str(e_min)
       
        a_et =  str(str(e_hour) + '.' + str(e_min))
        return a_et
      else:
        return 0
    
    def generate_attendance_detail(self, cr, uid, ids, context=None):
        #_logger.info('attendance_detail_report work')
        attendance_obj = self.pool.get('hr.fingerprint.attendance')
        attendance_detail_obj = self.pool.get('hr.attendance.detail')
        office_time_obj = self.pool.get('hr.employee.office.time')
        roster_line_obj = self.pool.get('hr.employee.duty.roster.line')
        contract_obj = self.pool.get('hr.contract')
        employee_obj = self.pool.get('hr.employee')
        leave_obj = self.pool.get('hr.holidays')
        trip_obj = self.pool.get('hr.travel.request')
        duty_obj = self.pool.get('hr.onduty.request')

        rec = self.browse(cr,uid,ids)
        date_from = rec.date_from
        date_to = rec.date_to
        today = date.today().strftime('%Y-%m-%d')
        day_from = datetime.strptime(str(date_from), "%Y-%m-%d")
        day_to = datetime.strptime(str(date_to), "%Y-%m-%d") #today
        nb_of_days = (day_to - day_from).days + 1
  
        print '>>> day_from ' + str(day_from)
        print '>>> day_to ' + str(day_to)
        print 'nb_of_days ' + str(nb_of_days)

        all_employee = employee_obj.search(cr,uid,[])
        all_employee_ids = employee_obj.browse(cr,uid,all_employee)

        for day in range(0,nb_of_days):
            
            w_day = day_from + timedelta(days=day)
            year = w_day.year
            month = w_day.month
            detail_day = str(w_day)[:str(w_day).find(' ')]
            l_f_date = (str(w_day).split(' ')[0] + ' 23:59:59')

            print '>> w_day ' + str(w_day)
            print 'detail_day ' + str(detail_day)
            print 'l_f_date ' + str(l_f_date)

            # one day for one employee
            for employees in all_employee_ids:

                employee = employees.id
                raw_sign_in = raw_sign_out = False
                reason = remark = ""
                leave = onduty = ontrip = late = attendance = absent = ot = 0.0
                sat_day = sun_day = False

                contract_id = contract_obj.search(cr,uid,[('employee_id','=', employee)])
                contract_objs = contract_obj.browse(cr, uid, contract_id)

                roster_line_ids = roster_line_obj.search(cr,uid,[('contract_id','=',contract_id),('date_from','<=', w_day),('date_to','>=',w_day)])
                #roster_line_ids = True
                if roster_line_ids:
                    print '>>> Duty Roster Have'
                    roster_line = roster_line_obj.browse(cr,uid,roster_line_ids[0])
                    shift = roster_line.get_shift_id_by_day(w_day.day)

                    shift_code = shift.code
                    shift_name = shift.name
                    time_start = shift.time_start
                    time_end = shift.time_end
                    late_start = shift.late_start
                    late_end = shift.late_end
                    ot_start = shift.ot_start
                    ot_end = shift.ot_end

                    # print contract_objs
                    # print contract_objs.shift
                    # print 'shift_code ' + str(shift_code)
                    # print 'shift_name ' + str(shift_name)
                    # print 'time_start ' + str(time_start)
                    # print 'time_end ' + str(time_end)
                    # print 'late_start ' + str(late_start)
                    # print 'late_end ' + str(late_end)
                    # print 'ot_start ' + str(ot_start)
                    # print 'ot_end ' + str(ot_end)

                    leave_ids = leave_obj.search(cr, uid, [('employee_id','=', employee),('date_from','<=', l_f_date),('date_to','>=',str(w_day)),('state','=','validate')])                 
                    if leave_ids:
                        print '> leave found'
                        leave_objs = leave_obj.browse(cr, uid, leave_ids)
                        leave_type = ""
                        if leave_objs.number_of_days_temp >= 1:
                            leave_type = 'Full'
                            leave = 1
                        elif leave_objs.number_of_days_temp < 1:
                            leave_type = 'Half'
                            leave = 0.5
                        reason = str(leave_objs.holiday_status_id.name) + ' (' + leave_type + ')'

                    # trip_ids = trip_obj.search(cr, uid, [('employee_id','=', employee),('from_date','<=', l_f_date),('to_date','>=',str(w_day)),('state','=','validate')])                 
                    # if trip_ids:
                    #     print '> trip found'
                    #     trip_objs = trip_obj.browse(cr, uid, trip_ids)
                    #     reason = trip_objs.reason
                    #     remark = 'On Trip '
                    #     ontrip = 1

                    # duty_ids = duty_obj.search(cr, uid, [('employee_id','=', employee),('from_date','<=', l_f_date),('to_date','>=',str(w_day)),('state','=','validate')])                 
                    # if duty_ids:
                    #     print '> duty found'
                    #     duty_objs = duty_obj.browse(cr, uid, duty_ids)
                    #     reason = duty_objs.purpose
                    #     remark = 'On Duty '
                    #     onduty = 1

                    detail_value = {
                        'employee': employee,
                        'enrollnumber': employees.otherid,
                        'location': employees.department_id.id,
                        'employeecode': employees.emp_id,
                        'employeename': employees.name_related,
                        'calculateddate': detail_day,
                        'shiftcode': shift_code,
                        'shiftname': shift_name,
                        'dayin': time_start,
                        'dayout': time_end,
                        'leave': leave,
                        'attendance': attendance,
                        'absent': absent,
                        'onduty': onduty,
                        'ontrip': ontrip,
                        'late': late,
                        'ot': ot,
                        'reason': reason, 
                        'remark': remark,
                    }
      
                    print detail_value

                    sql = "SELECT name,submit_time FROM hr_fingerprint_attendance WHERE EXTRACT(YEAR FROM name)=%s"
                    sql = sql + "AND EXTRACT(MONTH FROM name)=%s AND EXTRACT(DAY FROM name)=%s AND employee=%s AND action=%s ORDER BY submit_time"
                    cr.execute(sql, (year, month, w_day.day, employee, 'sign_in'))
                    sign_in = cr.fetchall()              
                    if len(sign_in) > 0:
                        print '>>> Sign In Have'
                        raw_sign_in = True
                        start_time = sign_in[0][1]

                        start_time = round(start_time,2)
                        if start_time > late_start and start_time < late_end:
                            #print 'late'
                            late = 1

                        detail_value.update({
                            'intime': self.time_format(round(start_time,2)),
                            'late': late,
                        })

                        sql = "SELECT name,submit_time FROM hr_fingerprint_attendance WHERE EXTRACT(YEAR FROM name)=%s"
                        sql = sql + "AND EXTRACT(MONTH FROM name)=%s AND EXTRACT(DAY FROM name)=%s AND employee=%s AND action=%s ORDER BY submit_time DESC"
                        cr.execute(sql, (year, month, w_day.day, employee, 'sign_out'))
                        sign_out = cr.fetchall()
                        if sign_out:
                            print '>>> Sign Out Have'
                            raw_sign_out = True
                            end_time = sign_out[0][1]
                            end_time = round(end_time,2)

                            if end_time > ot_start and end_time < ot_end:
                                #print 'ot'
                                ot = end_time - ot_start
                  
                            detail_value.update({
                                'outtime': self.time_format(round(end_time,2)),
                                'ot': ot
                            })

                    #print detail_value['leave']
                    has_leave = int(detail_value['leave']) > 0
                    has_ontrip = int(detail_value['ontrip']) > 0 
                    has_onduty = int(detail_value['onduty']) > 0

                    #print 'has_leave ' + str(has_leave)
                    #print 'has_ontrip ' + str(has_ontrip)
                    #print 'has_onduty ' + str(has_onduty)

                    date_format = "%Y-%m-%d"
                    detail_day_ = datetime.strptime(detail_day,date_format)

                    if detail_day_.strftime("%A") == 'Saturday':
                        #print '######## it saturday'
                        sat_day = True
                        detail_value.update({
                            'remark': 'Saturday',
                        })
                    if detail_day_.strftime("%A") == 'Sunday':
                        #print '######## it sunday'
                        sun_day = True
                        detail_value.update({
                            'remark': 'Sunday',
                        })

                    if not raw_sign_in and not raw_sign_out and not has_leave and not has_ontrip and not has_onduty and not sat_day and not sun_day:
                        #print detail_value
                        detail_value.update({'absent':1})

                    if raw_sign_in and raw_sign_out:
                        #print detail_value
                        detail_value.update({'attendance':1})

                    detail_id = attendance_detail_obj.search(cr,uid,[('employee','=',employee),('calculateddate','=',detail_day)])
                    
                    print detail_value
                    if detail_id:
                        print 'detail write'
                        detail_id = attendance_detail_obj.write(cr, uid, detail_id, detail_value,context)
                    else:
                        print 'detail create'
                        detail_id = attendance_detail_obj.create(cr, uid, detail_value,context)
                    print 'detail_id ' + str(detail_id)

                else:
                    #print '----------------------'
                    print "NO SIGN IN AND OUT"
                    #print '----------------------'
              
    
