import calendar
import time
from datetime import datetime
from datetime import timedelta
from dateutil import tz
from openerp import tools
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

class hr_payslip(osv.osv):
    '''
    Pay Slip
    '''

    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    def s(self,ss):
      if ss != '0':
        if len(str(ss)) == 1:
            ss = str(ss) + ' ' 
        elif len(str(ss)) == 2:
            ss = str(ss)
          
        return ss
      else:
        return '0 '

    def o(self,ot):
      if ot != '0':

        o_hour = int(str(ot).split('.')[0])
        o_min = str(ot).split('.')[1]

        if len(str(o_hour)) == 1:
            o_hour = ' ' + str(o_hour)  
        elif len(str(o_hour)) == 2:
            o_hour = str(o_hour)

        if len(str(o_min)) == 1:
            o_min = str(o_min) + ' '  
        elif len(str(o_min)) == 2:
            o_min = str(o_min)

        a_ot =  str(str(o_hour) + '.' + str(o_min))
        return a_ot
      else:
        return '0 '

    def b(self,et):
      #print 'b et ' + str(et)
      if et != '0':
        if '.' in str(et):
            e_hour = int(str(et).split('.')[0])
            e_min = str(et).split('.')[1]

            #print e_hour
            #print e_min
            if len(e_min) == 1:
              e_min = int(e_min) * 0.1
            elif len(e_min) == 2:
              e_min = int(e_min) * 0.01
      
            #print e_min
            e_min = int(round(round(round(e_min,2) % 1,2) * 60))
            #print 'e_min round ' + str(e_min)
      
            if len(str(e_min)) == 1:
              #if e_min == 0:
              #  e_min = str(e_min) + '0'
              #else:
              e_min = '0' + str(e_min) 
            elif len(str(e_min)) == 2:
              e_min = str(e_min)

        else:
            e_hour = et
            e_min = '00'
          
        if len(str(e_hour)) == 1:
          e_hour = '0' + str(e_hour) 
        elif len(str(e_hour)) == 2:
          e_hour = str(e_hour)
                          
        #print 'e_min ' + str(e_min)
        a_et =  str(str(e_hour) + '.' + str(e_min))
        return a_et
      else:
        return 'None '

    def create(self, cr, uid, data, context=None):
        context = dict(context or {})
        print data
        ot_check_obj = self.pool.get('hr.ot_check')

        ot_check_id = []
        if data.get('ot_check_id'):
            ot_check_id = data.get('ot_check_id')
            data.pop('ot_check_id')
            print data
            print ot_check_id
            #print int('c')

        record_id = super(hr_payslip, self).create(cr, uid, data, context=context)
        print 'record_id ' + str(record_id)

        if ot_check_id:
            print ot_check_obj.write(cr, uid, ot_check_id,{'slip_id':record_id}, context=context)

        return record_id

    def get_worked_day_lines(self, cr, uid, ids, contract_ids, date_from, date_to, context=None):
        print 'Work day calculation started'
        print context
        payslip_checking = False
        if context and context.get('from'):
            if 'payslip_checking' in context.get('from'):
                print 'work'
                payslip_checking = True

        res = super(hr_payslip,self).get_worked_day_lines(cr,uid,contract_ids,date_from,date_to,context=context)
        wage_adjust_obj = self.pool.get('hr.wage.adjustment')
        roster_line_obj = self.pool.get('hr.employee.duty.roster.line')
        travel_obj = self.pool.get('hr.travel.record')
        leave_obj = self.pool.get('hr.holidays')
        public_holiday_obj = self.pool.get('hr.public.holiday')
        office_time_obj = self.pool.get('hr.employee.office.time')
        holiday_line_obj = self.pool.get('hr.holidays.line')
        attendance_obj = self.pool.get('hr.fingerprint.attendance')
        ot_check_obj = self.pool.get('hr.ot_check')
        payslip_checking_obj = self.pool.get('hr.payslip.checking')
        ot_request_obj = self.pool.get('hr.ot.request')
        od_request_obj = self.pool.get('hr.od.request')
        otrate_adjustment_obj = self.pool.get('hr.otrate.adjustment.ex')

        for contract in self.pool.get('hr.contract').browse(cr,uid,contract_ids,context=context):
            day_from = datetime.strptime(str(date_from), "%Y-%m-%d")
            day_to = datetime.strptime(str(date_to), "%Y-%m-%d")
            year = datetime.strptime(str(date_to), "%Y-%m-%d").year
            month = datetime.strptime(str(date_to), "%Y-%m-%d").month
            nb_of_days = (day_to - day_from).days + 1
            month_days = calendar.monthrange(year,month)[1]
            #print 'month day ' + str(month_days)

            actual_days = {
                 'name': _("Acutal Working Days"),
                 'sequence': 1,
                 'code': 'ACWD',
                 'number_of_days': nb_of_days,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            attendances = {
                 'name': _("Normal Working Days"),
                 'sequence': 2,
                 'code': 'WD30',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            actual_attendances = {
                 'name': _("Working Days"),
                 'sequence': 3,
                 'code': 'WD',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            month_day = {
                 'name': _("Month Days"),
                 'sequence': 4,
                 'code': 'MD',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            # Leave
            normal_leave = {
                 'name': _("Leaves"),
                 'sequence': 5,
                 'code': 'L',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            # Late Leave
            late_leave = {
                 'name': _("Late Leaves"),
                 'sequence': 6,
                 'code': 'LL',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            # Absent Leave
            absent_leave = {
                 'name': _("Absent Leaves"),
                 'sequence': 7,
                 'code': 'AL',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            lates_under_25 = {
                 'name': _("Late Under 25 Minutes"),
                 'sequence': 8,
                 'code': 'LTMA',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            lates_over_25 = {
                 'name': _("Late Over 25 Minutes"),
                 'sequence': 9,
                 'code': 'LTMB',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            lates_half = {
                 'name': _("Late in Half Day"),
                 'sequence': 10,
                 'code': 'LTMC',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            
            df_over_time = {
                 'name': _("WeekDay/DayOff Overtime Hours"),
                 'sequence': 11,
                 'code': 'OTH',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            normal_over_time = {
                 'name': _("Public/Normal Overtime Hours"),
                 'sequence': 12,
                 'code': 'NOTH',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            on_duty = {
                 'name': _("On Duty"),
                 'sequence': 13,
                 'code': 'OD',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            
            travel_all = {
                 'name': _("Travel Days"),
                 'sequence': 14,
                 'code': 'TRAD',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            
            worked_days = 0.0
            worked_hours = 0.0
            late_under_days = late_under_mins = late_over_days = late_over_mins = 0.0
            late_half_mins = late_half_days = half_days = 0.0
            total_late = 0.0
            total_late_mins = 0.0
            bonus_for_att_marks = 0.0
            bonus_for_late_marks = 0.0
            df_ot_days = df_ot_hours = 0.0
            normal_ot_days = normal_ot_hours = 0.0
            od_days = od_hours = 0.0
            absent_days = 0.0
            tra_days = 0.0
            att_bns_before = 0.0
            att_bns_after = 0.0
            leaves = 0.0
            un_leaves = 0.0
            leaves_view = 0.0
            bot_days = 0.0
            botm = 0.0
            otm = 0.0
            bot_hours = 0.0
            tmp_half_leave_before = 0
            tmp_half_leave_after = 0
            
            start_time = 0
            end_time = 0
            ot_time = 0
            skip_day = 0
            a_st = '0'
            a_et = '0'
            el_check = False
            att_bonus_check = False
            absent = ""
            wd_day = 0
            greter_than_late = small_late = 0
            ot_check_ids = []
            
            for day in range(0,nb_of_days):
                leave_found = False
                start_time = 0
                end_time = 0
                ot_time = 0
                wk_hr = 0
                a_st = '0'
                a_et = '0'
                ab = ''
                l = late = ''
                wd = ''
                dfot = npot = od = '0'
                late_have = False
                el_check = False
                ot_check_id = None

                w_day = day_from + timedelta(days=day)
                
                #print 'contract.date_start ' + str(contract.date_start)
                joing_date = datetime.strptime(contract.date_start,"%Y-%m-%d")
                print 'w_day ' + str(w_day)
                
                if joing_date > day_from:
                  print 'skip'
                  if joing_date > w_day:
                    print 'continue'
                    skip_day += 1
                    continue
                  
                #print ''
                #print w_day
                roster_line_ids = roster_line_obj.search(cr,uid,[('contract_id','=',contract.id),('date_from','<=', w_day),('date_to','>=',w_day)])
                if roster_line_ids:
                    #print '>>> Duty Roster Have'
                    # from_zone = tz.gettz('UTC +00')
                    # to_zone = tz.gettz('Asia/Rangoon')

                    roster_line = roster_line_obj.browse(cr,uid,roster_line_ids[0])
                    shift = roster_line.get_shift_id_by_day(w_day.day)

                    #print 'Shift -> ' + str(shift.code)
                    year = w_day.year
                    month = w_day.month

                    l_f_date = (str(w_day).split(' ')[0] + ' 23:59:59')
                    #print 'l_f_date ' + str(l_f_date)

                    ########################### Leave ###########################

                    # #print 'employee_id >>> ' + str(contract.employee_id.id)
                    # leave_ids = leave_obj.search(cr, uid, [('employee_id','=',contract.employee_id.id),('type','=','remove'),('state','=','validate')])                 
                    
                    # if leave_ids:
                    #   # first leave request
                    #   #print 'leave_ids : ' + str(leave_ids)
                    #   for i in leave_ids:
                    #     holiday_ids = holiday_line_obj.search(cr, uid, [('holidays_id','=', i),('name','=',w_day)])
                        
                    #     if holiday_ids:
                    #       leave_found = True
                    #       leave = holiday_line_obj.browse(cr, uid, holiday_ids)

                    #       l += leave.status_id.name + ' (' +str(leave.duration) + ') '

                    #       if leave.status_id.name in ('Unpaid','WP','WPHL'):
                    #         if leave.duration:
                    #           leaves += leave.duration
                          
                    #       # if leave.duration > 0:
                    #       #   leaves_view += leave.duration
                    #       #   wd = '1'
                    #       #   wd_day += 1

                    #       if leave.duration >= 1:
                    #         leaves_view += 1
                    #       elif leave.duration < 1:
                    #         leaves_view += 0.5
                    #         # wd = '0.5'
                    #         # wd_day += 0.5
                    #         # print 'wd - 0.5'

                    # #print 'leaves : ' + str(leaves)

                    ########################### Leave ###########################

                    # no need to check without pay leave and unpaid leave becoz
                    # if attendance not exit this day will auto absent
                    leave_ids = leave_obj.search(cr, uid, [('employee_id','=',contract.employee_id.id),('date_from','<=', l_f_date),('date_to','>=',str(w_day))])                 
                    if leave_ids:

                        leave_found = True
                        leave = leave_obj.browse(cr, uid, leave_ids)
                        
                        print 'leave.number_of_days_temp ' + str(leave.number_of_days_temp)
                        if leave.number_of_days_temp >= 1:
                            leaves_view += 1
                        elif leave.number_of_days_temp < 1:
                            leaves_view += 0.5

                    sql = "SELECT name,submit_time FROM hr_fingerprint_attendance WHERE EXTRACT(YEAR FROM name)=%s"
                    sql = sql + "AND EXTRACT(MONTH FROM name)=%s AND EXTRACT(DAY FROM name)=%s AND employee=%s AND action=%s ORDER BY submit_time"
                    ### To add ygn time zone to date form database

                    cr.execute(sql, (year, month, w_day.day, contract.employee_id.id, 'sign_in'))
                    sign_in = cr.fetchall()              
                    if len(sign_in) > 0:
                        #print '>>> Sign In Have'
                        tra_days += 1
                        start_time = sign_in[0][1]

                        sql = "SELECT name,submit_time FROM hr_fingerprint_attendance WHERE EXTRACT(YEAR FROM name)=%s"
                        sql = sql + "AND EXTRACT(MONTH FROM name)=%s AND EXTRACT(DAY FROM name)=%s AND employee=%s AND action=%s ORDER BY submit_time DESC"
                        cr.execute(sql, (year, month, w_day.day, contract.employee_id.id, 'sign_out'))
                        sign_out = cr.fetchall()
                        if sign_out:
                            #print '>>> Sign Out Have'
                            end_time = sign_out[0][1]
                            
                            # e.g to skip 5 late 1 day deduction, they request morning half leave  
                            if start_time < end_time:
                              wd_diff = end_time - start_time

                              if wd_diff >= 6:
                                wd = '1'
                                wd_day += 1
                                print 'wd - 1'

                              # check it Half Off Days ?
                              elif wd_diff >= 2 and shift.duration < 8 and shift.duration >= 4:
                                wd = '0.5'
                                wd_day += 0.5
                                print 'wd - 0.5'

                              # check it Half Leave ?
                              elif leave_found and leave.number_of_days_temp < 1:
                                wd = '0.5'
                                wd_day += 0.5
                                print 'wd - 0.5'

                              # it may Late Half Day or Early Out ???
                              # TODO No Deduction For Earout
                              # TODO No Deduction For late_half
                              else:
                                absent_days = absent_days + 0.5
                                ab = 'AB 1/2'
                        else:
                            end_time = shift.time_end

                        worked_days += 1
                        wk_hr = end_time - start_time
                        if wk_hr < 0:
                            wk_hr = wk_hr + 24

                        worked_hours += wk_hr

                        ########################### Late ###########################

                        # # check for half day leave
                        # if not leave_found:

                        #     # late under 25 and late over 25
                        #     # 1 min free time
                        #     f_time = shift.time_start #+ 0.02
                        #     start_time = round(start_time,2)
                        #     end_time = round(end_time,2)
                        #     #print start_time
                        #     #print end_time

                        #     # check for off day becoz SSS shift have no time
                        #     if shift.code != 'SSS':
                        #       if f_time < start_time:
                        #         t_diff = round(start_time - f_time,2)
                        #         #print t_diff
                        #         if t_diff <= 1.50:
                        #           late_have = True
                        #           if t_diff < 0.40:
                        #             #print 'late_under_days'
                        #             late = 'Late <25'
                        #             late_under_days += 1
                        #             late_under_mins += t_diff
                        #           elif t_diff > 0.40:
                        #             #print 'late_over_days'
                        #             late = 'Late >25' 
                        #             late_over_days += 1
                        #             late_over_mins += t_diff

                        #         # TO Skip - Create Morning Half Off Shift
                        #         elif t_diff > 1.50:
                        #           #print 'late_half'
                        #           late = 'Late Halfday'
                        #           late_have = True
                        #           late_half_days += 1
                        #           late_half_mins += t_diff

                        ########################### Late ###########################

                            ########################### OT Request ###########################

                            # ot_request_ids = ot_request_obj.search(cr,uid,[('employee_id','=',contract.employee_id.id),('date','=',w_day)])

                            # if ot_request_ids:
                            #   #print 'OT REQUEST ' + str(ot_request_ids[0])
                            #   ot_request_objs = ot_request_obj.browse(cr,uid,ot_request_ids[0])
                            #   public_holiday = public_holiday_obj.search(cr, uid,[('date_from','<=', w_day),('date_to','>=', w_day)])
                            #   #print 'public_holiday ' + str(public_holiday)

                            #   #print contract.employee_id.department_id.name
                            #   parent_department_name = contract.employee_id.department_id.parent_id.name
                              
                            #   #raise ValidationError('')
                            #   ot_request_date = datetime.strptime(str(ot_request_objs.date),"%Y-%m-%d")
                            #   #print ot_request_date

                            #   if public_holiday:
                            #     normal_ot_days += 1
                            #     normal_ot_hours += float(ot_request_objs.total_hours)
                            #     ot = str(float(ot_request_objs.total_hours)) + ' (NP)'
                            #   elif ot_request_date.strftime("%A") == 'Saturday' and parent_department_name == 'PD':
                            #     normal_ot_days += 1
                            #     normal_ot_hours += float(ot_request_objs.total_hours)
                            #     ot = str(float(ot_request_objs.total_hours)) + ' (NP)'
                            #   else:
                            #     df_ot_days += 1
                            #     df_ot_hours += float(ot_request_objs.total_hours)
                            #     ot = str(float(ot_request_objs.total_hours)) + ' (DF)'
                            #     #print 'OT REQUEST HOURS ' + str(float(ot_request_objs.total_hours))

                            ########################### OT Request ###########################
                    else:
                      #print '----------------------'
                      #print "NO SIGN IN AND OUT"
                      #print '----------------------'

                      ########################### OD Request ###########################

                      # od_request_ids = od_request_obj.search(cr,uid,[('employee_id','=',contract.employee_id.id),('date','=',w_day)])

                      # if od_request_ids:
                      #   #print 'OD REQUEST ' + str(od_request_ids[0])
                      #   od_request_objs = od_request_obj.browse(cr,uid,od_request_ids[0])

                      #   od_days += 1
                      #   od_hours += float(od_request_objs.total_hours)
                      #   od = '1'

                      ########################### AUTO ABSENT ###########################

                      # check no attendance,no leave,no dayoff,no onduty
                      if not leave_found and shift.code !=False and shift.code != 'SSS': # and not od_request_ids:
                        absent_days = absent_days + 1
                        ab = 'AB'
                      ########################### AUTO ABSENT ###########################

                      ########################### OD Request ###########################

                    ########################### Console Debug ###########################

                    ss = datetime.strptime(str(w_day),"%Y-%m-%d 00:00:00").strftime("%a")
                    check_work_day = str(w_day.strftime('%m-%d')) + ' (' + ss + ')'
                    
                    if len(str(shift.code)) == 1:
                      sc = str(shift.code) + '  '
                    elif len(str(shift.code)) == 2:
                      sc = str(shift.code) + ' '
                    else:
                      sc = str(shift.code)

                    ss = str(int(shift.time_start))
                    se = str(int(shift.time_end))
                    ss = str(self.s(ss))
                    se = str(self.s(se))
                    st = '0'
                    et = '0'

                    if start_time and end_time:
                      st = start_time
                      et = end_time
                    
                    a_st = str(self.b(st))
                    #print 'a_st ' + str(a_st)
                    a_et = str(self.b(et))
                    #print 'a_et ' + str(a_et)
                            
                    ot = str(round(ot_time,2))
                    ot = str(self.o(ot))
                    ot_m = str(int(round(ot_time*60,0)))
                    
                    if len(ot_m) == 1:
                      ot_m = ' ' + ot_m + ' '
                    elif len(ot_m) == 2:
                      ot_m = ot_m + ' '
                    else:
                      ot_m = ot_m
                    
                    if ids:
                        ot_check_id = ot_check_obj.search(cr,uid,[('slip_id','=',ids[0]),('work_day','=',check_work_day)])
                    #else:
                    #    ot_check_ids = ot_check_obj.search(cr,uid,[('employee_id','=',contract.employee_id.id),('date_from','=', date_from),('date_to','=',date_to),('work_day','=',check_work_day)])
                    #print 'ot_check_ids ' + str(ot_check_ids)
                      
                    lh = leave_found
                    if wk_hr > 0:
                      wd = wd +' ('+str(round(wk_hr,2))+') '
                    else:
                      wd = '0'
                      
                    ot_check_value = {
                                #'slip_id':
                                'employee_id': contract.employee_id.id,
                                'date_from': date_from,
                                'date_to': date_to,
                                'work_day': check_work_day,
                                'shift': sc +' ('+ss+'-'+se+') ',
                                'in_out':'IN '+a_st+' - '+'OUT '+a_et,
                                'wd': wd,
                                'ot': ot,
                                'od': od,
                                'wp': ab,
                                'l': l,
                                'lh': lh,
                                'late_have': late_have
                    }
                    
                    if late_have:
                      ot_check_value.update({'in_out':'IN '+a_st+' - '+'OUT '+a_et+'  -  ('+late+')'})
                    
                    if not payslip_checking:
                        #print ids
                        #print ot_check_id
                        if ids and ot_check_id:
                            #print '>>>> ot check write'
                            ot_check_flag = ot_check_obj.write(cr, uid, ot_check_id,ot_check_value, context=context)
                            #print '>>>> ot check flag ' + str(ot_check_flag)
                        elif ids and not ot_check_id:
                            #print '>>>> ot check create'
                            ot_check_value.update({'slip_id':ids[0]})
                            ot_check_id = ot_check_obj.create(cr, uid, ot_check_value, context=context)
                        elif not ids and not ot_check_id:
                            #print '>>>> ot check create'
                            ot_check_id = ot_check_obj.create(cr, uid, ot_check_value, context=context)
                            ot_check_ids.append(ot_check_id)
                            #print '>>>> ot check id ' + str(ot_check_id)

                    #print   '---------------------------------------------------------------------------------------------------------'
                    #print '| '+check_work_day+' | '+sc+' ('+ss+'-'+se+') | '+'IN '+a_st+' - '+'OUT '+a_et+' | '+'OT '+ot+' ('+ot_m+')'+' | '+wp+' | '
                    #print  '----------------------------------------------------------------------------------------------------------'
                      
                    ########################### Console Debug ###########################

            total_late_mins = late_under_mins + late_over_mins + late_half_mins
            #print 'total_late_mins ' + str(total_late_mins)
            #print 'skip_day ' + str(skip_day)

            # if od_days >= 0:
            #   on_duty['number_of_days'] += od_days
            #   on_duty['number_of_hours'] += od_hours

            # if late_over_days >= 0:
            #   if late_over_days >= 2:
            #     late_leave['number_of_days'] += int(late_over_days) / 2
            #     late_leave['number_of_hours'] += late_over_mins

            # if late_under_days >= 0:
            #   if late_under_days >= 5:
            #     late_leave['number_of_days'] += int(late_under_days) / 5
            #     late_leave['number_of_hours'] += late_under_mins

            attendances['number_of_days'] = month_days - leaves - absent_days - skip_day #- late_leave['number_of_days'] + od_days
            attendances['number_of_hours'] = worked_hours #- total_late_mins + od_hours
            #travel_all['number_of_days'] = tra_days

            if ot_check_ids:
                res += [{'ot_check_id':ot_check_ids}]

            #res += [on_duty]
            res += [actual_days]
            res += [attendances]
            #res += [late_leave]

            actual_attendances['number_of_days'] = wd_day #+ od_days
            actual_attendances['number_of_hours'] = (wd_day) * 8 # + od_days

            month_day['number_of_days'] = month_days
            month_day['number_of_hours'] = month_days * 8
            res += [actual_attendances]
            res += [month_day]

            if leaves_view >= 0:
              #print 'leaves_view ' + str(leaves_view)
              normal_leave['number_of_days'] = leaves_view
              normal_leave['number_of_hours'] = leaves_view * 8
              #print 'Leave ' + str(leaves_view)
              res += [normal_leave]
            
            if absent_days >= 0:
              #print absent_days
              absent_leave['number_of_days'] = absent_days
              absent_leave['number_of_hours'] = absent_days * 8
              #print '-------------------------------------'
              #print absent
              #print 'Absent Total - ' + str(absent_days)
              #print '-------------------------------------'
              res += [absent_leave]

            # if late_under_days >= 0:
            #     lates_under_25['number_of_days'] = late_under_days
            #     lates_under_25['number_of_hours'] = late_under_mins
            #     res += [lates_under_25]
            #     #print 'lates_15[number_of_days] ' + str(lates_15['number_of_days'])
            # if late_over_days >= 0:
            #     lates_over_25['number_of_days'] = late_over_days
            #     lates_over_25['number_of_hours'] = late_over_mins
            #     res += [lates_over_25]
            #     #print 'lates_1[number_of_days] ' + str(lates_1['number_of_days'])
            # if late_half_days >= 0:
            #     lates_half['number_of_days'] = late_half_days
            #     lates_half['number_of_hours'] = late_half_mins
            #     res += [lates_half]
            #     #print 'lates_half[number_of_days] ' + str(lates_half['number_of_days'])

            # if df_ot_days >= 0:
            #   df_over_time['number_of_days'] = df_ot_days
            #   df_over_time['number_of_hours'] = round(df_ot_hours,2)
            #   res += [df_over_time]

            # if normal_ot_days >= 0:
            #   normal_over_time['number_of_days'] = normal_ot_days
            #   normal_over_time['number_of_hours'] = round(normal_ot_hours,2)
            #   res += [normal_over_time]

            # Payslip Checking
            payslip_checking_ids = payslip_checking_obj.search(cr, uid, [('date_from','=',day_from),('date_to','=',day_to),('employee_id','=',contract.employee_id.id)])

            # late_leave_exception = False
            # if late_over_days > 5:
            #     late_leave_exception = True

            # absent_exception = False
            # if absent_days > 5:
            #     absent_exception = True

            if payslip_checking:
                payslip_checking_value = {
                    'employee_id': contract.employee_id.id,
                    'parent_department_id': contract.employee_id.parent_department_id.id,
                    'date_from': day_from,
                    'date_to': day_to,
                    'wd': actual_attendances['number_of_days'],
                    'leave': normal_leave['number_of_days'],
                    'late_leave': 0.0, # late_leave['number_of_days']
                    'late_big': 0.0, # late_over_days
                    'late_small': 0.0 , # late_under_days
                    'late_half': late_half_days,
                    'absent': absent_days,
                    'df_ot': 0.0, # df_over_time['number_of_days']
                    'n_ot': 0.0, # normal_over_time['number_of_days']
                    'od': od_days,
                    # 'late_leave_exception': late_leave_exception,
                    # 'absent_exception': absent_exception
                }
                
                if payslip_checking_ids:
                    print '>>>> payslip_checking write'
                    payslip_checking_obj.write(cr, uid, payslip_checking_ids,payslip_checking_value, context=context)
                else:
                    print '>>>> payslip_checking create'
                    payslip_checking_id = payslip_checking_obj.create(cr, uid, payslip_checking_value, context=context)
                    #print '>>>> payslip_checking_id' + str(payslip_checking_id)

            # WAGE ADJUSTMENT
            # wage_adjustment_ids = wage_adjust_obj.search(cr,uid,[('employee_id','=',contract.employee_id.id)])
            # if wage_adjustment_ids:
            #     #print 'wage adjustment started'
            #     cal_month = {'1':4, '2':3, '3':2, '4':1, '5':12, '6':11, '7':10, '8':9, '9':8, '10':7, '11':6, '12':5}
            #     adjust = None
            #     for adjust_id in wage_adjust_obj.browse(cr,uid,wage_adjustment_ids):
            #         if adjust == None:
            #             adjust = adjust_id
            #         else:
            #             if adjust.id < adjust_id.id:
            #                 adjust = adjust_id
            #     eff_date = datetime.strptime(adjust.effective_date, "%Y-%m-%d")
            #     eff_date_str = datetime.strftime(eff_date,'%Y-%m-%d')
            #     date_to = datetime.strptime(date_to, "%Y-%m-%d")
            #     old_income = {
            #              'name': _(""),
            #              'sequence': 15,
            #              'code': 'OIT',
            #              'number_of_days': 0.0,
            #              'number_of_hours': 0.0,
            #              'contract_id': contract.id,
            #              }
            #     new_income = {
            #              'name': _(""),
            #              'sequence': 16,
            #              'code': 'NIT',
            #              'number_of_days': 0.0,
            #              'number_of_hours': 0.0,
            #              'contract_id': contract.id,
            #              }
            #     if eff_date.year == date_to.year and ((eff_date.month > 4 and date_to.month > 4) or (eff_date.month <= 4 and date_to.month <= 4)) :
            #         #print 'He has wage adjustment this year'
            #         #print 'pay month=',date_to.month
            #         #print 'eff month=',eff_date.month
            #         if date_to.month >= eff_date.month:                            
            #             new_income_total = adjust.new_wage * cal_month[str(eff_date.month)]    
            #             old_income_total = adjust.old_wage * (12 - cal_month[str(eff_date.month)])
            #             #print 'New Wage=', adjust.new_wage, 'Calc Months=',cal_month[str(eff_date.month)], 'Total=', new_income_total
            #             #print 'Old Wage=', adjust.old_wage, 'Calc Months=',(12 - cal_month[str(eff_date.month)]), 'Total=', old_income_total
                        
            #             new_name_str = "New Income total ("+str(adjust.new_wage)+' started from '+eff_date_str+')'
            #             old_name_str = "Old Income total ("+str(adjust.old_wage)+' until '+eff_date_str+')'
            #             new_income['name']=_(new_name_str)
            #             new_income['number_of_days'] = cal_month[str(eff_date.month)]
            #             new_income['number_of_hours'] = new_income_total
            #             old_income['name']=_(old_name_str)
            #             old_income['number_of_days'] = 12 - cal_month[str(eff_date.month)]
            #             old_income['number_of_hours'] = old_income_total
            #             res += [new_income] + [old_income]
            #         else:
            #             new_income_total = 0    
            #             old_income_total = adjust.old_wage * 12
            #             #print 'New Wage=', adjust.new_wage, 'Calc Months=',cal_month[str(eff_date.month)], 'Total=', new_income_total
            #             #print 'Old Wage=', adjust.old_wage, 'Calc Months=',(12 - cal_month[str(eff_date.month)]), 'Total=', old_income_total
                        
            #             new_name_str = "New Income total 0.0"
            #             old_name_str = "Old Income total ("+str(adjust.old_wage)+' until '+eff_date_str+')'
            #             new_income['name']=_(new_name_str)
            #             new_income['number_of_days'] = 0
            #             new_income['number_of_hours'] = new_income_total
            #             old_income['name']=_(old_name_str)
            #             old_income['number_of_days'] = 12
            #             old_income['number_of_hours'] = old_income_total
            #             res += [new_income] + [old_income]
            #     elif date_to.year - eff_date.year == 1 and eff_date.month > 4 and date_to.month <= 5:
            #         #print 'He has wage adjustment last year'
            #         #print 'pay month=',date_to.month
            #         #print 'eff month=',eff_date.month
            #         if date_to.month <= eff_date.month:                            
            #             new_income_total = adjust.new_wage * cal_month[str(eff_date.month)]    
            #             old_income_total = adjust.old_wage * (12 - cal_month[str(eff_date.month)])
            #             #print 'New Wage=', adjust.new_wage, 'Calc Months=',cal_month[str(eff_date.month)], 'Total=', new_income_total
            #             #print 'Old Wage=', adjust.old_wage, 'Calc Months=',(12 - cal_month[str(eff_date.month)]), 'Total=', old_income_total
            #             new_name_str = "New Income total ("+str(adjust.new_wage)+' started from '+eff_date_str+')'
            #             old_name_str = "Old Income total ("+str(adjust.old_wage)+' until '+eff_date_str+')'
            #             new_income['name']=_(new_name_str)
            #             new_income['number_of_days'] = cal_month[str(eff_date.month)]
            #             new_income['number_of_hours'] = new_income_total
            #             old_income['name']=_(old_name_str)
            #             old_income['number_of_days'] = 12 - cal_month[str(eff_date.month)]
            #             old_income['number_of_hours'] = old_income_total
            #             res += [new_income] + [old_income]
            #     else:
            #         #print 'He has wage adjustment but no effect to payslip'
            #         #print 'pay month=',date_to.month
            #         #print 'eff month=',eff_date.month                
            #         new_income_total = adjust.new_wage * 12
            #         new_name_str = "Income total ("+str(adjust.new_wage)+' started from '+eff_date_str+')'
            #         new_income['name']=_(new_name_str)
            #         new_income['number_of_days'] = 12
            #         new_income['number_of_hours'] = new_income_total
            #         old_income['name']=_("Old income total")
            #         res += [new_income] + [old_income]
            # else:
            #     old_income = {
            #              'name': _("Old"),
            #              'sequence': 15,
            #              'code': 'OIT',
            #              'number_of_days': 0.0,
            #              'number_of_hours': 0.0,
            #              'contract_id': contract.id,
            #              }
            #     new_income = {
            #              'name': _(""),
            #              'sequence': 16,
            #              'code': 'NIT',
            #              'number_of_days': 0.0,
            #              'number_of_hours': 0.0,
            #              'contract_id': contract.id,
            #              }
            #     date_to = datetime.strptime(date_to, "%Y-%m-%d")
            #     #print 'He has no wage adjustment'
            #     #print 'pay month=',date_to.month
            #     total_month_wage = contract.wage + contract.month_allowance
            #     total_year_wage = (contract.wage + contract.year_allowance) * 11

            #     new_income_total = total_month_wage + total_year_wage #contract.wage * 12
            #     new_name_str = "Income total ("+str(contract.wage)+')'
            #     new_income['name']=_(new_name_str)
            #     new_income['number_of_days'] = 12
            #     new_income['number_of_hours'] = new_income_total #7483000
            #     res += [old_income] + [new_income]
        return res

    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, context=None):
        print 'child onchange_employee_id work'
        empolyee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        worked_days_obj = self.pool.get('hr.payslip.worked_days')
        input_obj = self.pool.get('hr.payslip.input')

        if context is None:
            context = {}
        #delete old worked days lines
        worked_days_ids_to_remove=[]
        old_worked_days_ids = ids and worked_days_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
        if old_worked_days_ids:
            worked_days_ids_to_remove = map(lambda x: (2, x,),old_worked_days_ids)

        #delete old input lines
        input_line_ids_to_remove=[]
        old_input_ids = ids and input_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
        if old_input_ids:
            input_line_ids_to_remove = map(lambda x: (2,x,), old_input_ids)


        #defaults
        res = {'value':{
                      'line_ids':[],
                      'input_line_ids': input_line_ids_to_remove,
                      'worked_days_line_ids': worked_days_ids_to_remove,
                      #'details_by_salary_head':[], TODO put me back
                      'name':'',
                      'contract_id': False,
                      'struct_id': False,
                      }
            }
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_to, "%Y-%m-%d")))
        employee_id = empolyee_obj.browse(cr, uid, employee_id, context=context)
        res['value'].update({
                    'name': _('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(ttyme.strftime('%B-%Y'))),
                    'company_id': employee_id.company_id.id
        })

        if not context.get('contract', False):
            #fill with the first contract of the employee
            contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)
        else:
            if contract_id:
                #set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                #if we don't give the contract, then the input to fill should be for all current contracts of the employee
                contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)

        if not contract_ids:
            return res
        contract_record = contract_obj.browse(cr, uid, contract_ids[0], context=context)
        res['value'].update({
                    'contract_id': contract_record and contract_record.id or False
        })
        struct_record = contract_record and contract_record.struct_id or False
        if not struct_record:
            return res
        res['value'].update({
                    'struct_id': struct_record.id,
        })
        #computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(cr, uid, ids,contract_ids, date_from, date_to, context=context)
        #print worked_days_line_ids
        worked_days_line = []
        ot_check_id = []
        for wdl in worked_days_line_ids:
            #print wdl
            if 'ot_check_id' in wdl:
                ot_check_id = wdl.get('ot_check_id')
            else:
                worked_days_line.append(wdl)
        worked_days_line_ids = worked_days_line
        #print worked_days_line_ids
        #print ot_check_id
        #print int('b')

        input_line_ids = self.get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
        res['value'].update({
                    'worked_days_line_ids': worked_days_line_ids,
                    'input_line_ids': input_line_ids,
        })
        if ot_check_id:
            res['value'].update({
                    'ot_check_id': ot_check_id
        })
        return res