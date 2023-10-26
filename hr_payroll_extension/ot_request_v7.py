from openerp.osv import fields, osv
from operator import attrgetter
from openerp.tools.translate import _

class hr_ot_request(osv.osv):
    _name = "hr.ot.request"
    _inherit = ['mail.thread','hr.ot.request']

    def _get_can_reset(self, cr, uid, ids, name, arg, context=None):
        """User can reset a leave request if it is its own leave request or if
        he is an Hr Manager. """
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        group_hr_manager_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_hr_manager')[1]
        if group_hr_manager_id in [g.id for g in user.groups_id]:
            return dict.fromkeys(ids, True)
        result = dict.fromkeys(ids, False)
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.employee_id and holiday.employee_id.user_id and holiday.employee_id.user_id.id == uid:
                result[holiday.id] = True
        return result

    def _get_can_approve(self, cr, uid, ids, name, arg, context=None):
        """ Manager Only Can See and Approve his Employee Request. """
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        resource = self.pool['resource.resource'].search(cr, uid, [('user_id','=',user.id)], context=context)
        result = dict.fromkeys(ids, False)
        if len(resource) > 0:
        	employee = self.pool['hr.employee'].search(cr, uid, [('resource_id','=',resource[0])], context=context)
        	if len(employee) > 0:
		        for holiday in self.browse(cr, uid, ids, context=context):
		            if holiday.employee_id and holiday.employee_id.parent_id and holiday.employee_id.parent_id.id == employee[0]:
		                result[holiday.id] = True
        return result

    _columns = {
        'state': fields.selection([('draft', 'To Submit'), ('cancel', 'Cancelled'),('confirm', 'To Approve'), ('refuse', 'Refused'), ('validate1', 'Second Approval'), ('validate', 'Approved')],
            'Status', readonly=True, track_visibility='onchange', copy=False,
            help='The status is set to \'To Submit\', when a holiday request is created.\
            \nThe status is \'To Approve\', when holiday request is confirmed by user.\
            \nThe status is \'Refused\', when holiday request is refused by manager.\
            \nThe status is \'Approved\', when holiday request is approved by manager.'),
        'can_reset': fields.function(
            _get_can_reset,
            type='boolean'),
        'can_approve': fields.function(
            _get_can_approve,
            type='boolean'),
    }
    _defaults = {
        'state': 'confirm'
    }

    # _constraints = [
    #     (_check_date, 'You can not have 2 leaves that overlaps on same day!', ['date_from','date_to']),
    #     (_check_holidays, 'The number of remaining leaves is not sufficient for this leave type', ['state','number_of_days_temp'])
    # ] 
    
    # _sql_constraints = [
    #     ('type_value', "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or (holiday_type='category' AND category_id IS NOT NULL))", 
    #      "The employee or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
    #     ('date_check2', "CHECK ( (type='add') OR (date_from <= date_to))", "The start date must be anterior to the end date."),
    #     ('date_check', "CHECK ( number_of_days_temp >= 0 )", "The number of days must be greater than 0."),
    # ]

    def ot_request_reset(self, cr, uid, ids, context=None):
        print 'ot_request_reset'
        self.write(cr, uid, ids, {
            'state': 'draft',
            'manager_id': False,
            'manager_id2': False,
        })
        return True

    def ot_request_first_validate(self, cr, uid, ids, context=None):
        print 'ot_request_first_validate'
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.ot_request_first_validate_notificate(cr, uid, ids, context=context)
        return self.write(cr, uid, ids, {'state':'validate1', 'manager_id': manager})

    def ot_request_validate(self, cr, uid, ids, context=None):
    	print 'ot_request_validate'
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'validate'})
        return True

    def ot_request_confirm(self, cr, uid, ids, context=None):
    	print 'ot_request_confirm'
        for record in self.browse(cr, uid, ids, context=context):
            if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [record.id], user_ids=[record.employee_id.parent_id.user_id.id], context=context)
        return self.write(cr, uid, ids, {'state': 'confirm'})

    def ot_request_refuse(self, cr, uid, ids, context=None):
    	print 'ot_request_refuse'
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.state == 'validate1':
                self.write(cr, uid, [holiday.id], {'state': 'refuse', 'manager_id': manager})
            else:
                self.write(cr, uid, [holiday.id], {'state': 'refuse', 'manager_id2': manager})
        return True

    def ot_request_first_validate_notificate(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            self.message_post(cr, uid, [obj.id],
                _("Request approved, waiting second validation."), context=context)
