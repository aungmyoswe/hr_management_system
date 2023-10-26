from openerp.osv import fields, osv

class hr_employee(osv.osv):
    _inherit="hr.employee"
    
    def _set_remaining_days(self, cr, uid, empl_id, name, value, arg, context=None):
        employee = self.browse(cr, uid, empl_id, context=context)
        diff = value - employee.remaining_leaves
        type_obj = self.pool.get('hr.holidays.status')
        holiday_obj = self.pool.get('hr.holidays')
        # Find for holidays status
        status_ids = type_obj.search(cr, uid, [('limit', '=', False)], context=context)
        if len(status_ids) != 1 :
            raise osv.except_osv(_('Warning!'),_("The feature behind the field 'Remaining Legal Leaves' can only be used when there is only one leave type with the option 'Allow to Override Limit' unchecked. (%s Found). Otherwise, the update is ambiguous as we cannot decide on which leave type the update has to be done. \nYou may prefer to use the classic menus 'Leave Requests' and 'Allocation Requests' located in 'Human Resources \ Leaves' to manage the leave days of the employees if the configuration does not allow to use this field.") % (len(status_ids)))
        status_id = status_ids and status_ids[0] or False
        if not status_id:
            return False
        if diff > 0:
            leave_id = holiday_obj.create(cr, uid, {'name': _('Allocation for %s') % employee.name, 'employee_id': employee.id, 'holiday_status_id': status_id, 'type': 'add', 'holiday_type': 'employee', 'number_of_days_temp': diff}, context=context)
        elif diff < 0:
            raise osv.except_osv(_('Warning!'), _('You cannot reduce validated allocation requests'))
        else:
            return False
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday_obj.signal_workflow(cr, uid, [leave_id], sig)
        return True
    
    def _get_remaining_days(self, cr, uid, ids, name, args, context=None):
        hr_holiday_status_obj = self.pool.get('hr.holidays.status')
        medical_leave_ids = hr_holiday_status_obj.search(cr,uid,[('name','=','Medical Leaves')])
        if medical_leave_ids:
          medical_leave_id = medical_leave_ids[0]
          print 'medical_leave_id ' + str(medical_leave_id)
        
        cr.execute("""SELECT
                sum(h.number_of_days) as days,
                h.employee_id
            from
                hr_holidays h
                join hr_holidays_status s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                s.id != %s and
                s.limit=False and
                h.employee_id in %s
            group by h.employee_id""", (medical_leave_id,tuple(ids),))
        res = cr.dictfetchall()
        print res
        remaining = {}
        for r in res:
            remaining[r['employee_id']] = r['days']
        for employee_id in ids:
            if not remaining.get(employee_id):
                remaining[employee_id] = 0.0
        return remaining
    
    def _get_remaining_medical_days(self, cr, uid, ids, name, args, context=None):
        hr_holiday_status_obj = self.pool.get('hr.holidays.status')
        medical_leave_ids = hr_holiday_status_obj.search(cr,uid,[('name','=','Medical Leaves')])
        if medical_leave_ids:
          medical_leave_id = medical_leave_ids[0]
          print 'medical_leave_id ' + str(medical_leave_id)
        
        cr.execute("""SELECT
                sum(h.number_of_days) as days,
                h.employee_id
            from
                hr_holidays h
                join hr_holidays_status s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                s.id= %s and
                s.limit=False and
                h.employee_id in %s
            group by h.employee_id""", (medical_leave_id,tuple(ids),))
        res = cr.dictfetchall()
        remaining = {}
        for r in res:
            remaining[r['employee_id']] = r['days']
        for employee_id in ids:
            if not remaining.get(employee_id):
                remaining[employee_id] = 0.0
        return remaining
      
    _columns = {
        'remaining_medical_leaves': fields.function(_get_remaining_medical_days, string='Remaining Medical Leaves', type="float", help='Total number of legal leaves allocated to this employee, change this value to create allocation/leave request. Total based on all the leave types without overriding limit.'),
        'remaining_leaves': fields.function(_get_remaining_days, string='Remaining Legal Leaves', fnct_inv=_set_remaining_days, type="float", help='Total number of legal leaves allocated to this employee, change this value to create allocation/leave request. Total based on all the leave types without overriding limit.'),
     }
