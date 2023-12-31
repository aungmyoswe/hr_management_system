# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    public_holiday_id = fields.Many2one(
        'hr.public.holiday',
        string="Public Holiday")

    # open when import leave allocation
    # def write(self, cr, uid, ids, vals, context=None):
    #     print 'hr_holiday write child call '
    #     employee_id = vals.get('employee_id', False)
    #     if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'cancel'] and not self.pool['res.users'].has_group(cr, uid, 'base.group_hr_user'):
    #         raise osv.except_osv(_('Warning!'), _('You cannot set a leave request as \'%s\'. Contact a human resource manager.') % vals.get('state'))
        
    #     print 'hr_holiday write child before vals ' + str(vals)
    #     if 'state' in vals and 'manager_id2' not in vals:
    #         vals.update({'state': 'validate'})
    #         print 'hr_holiday write child after vals ' + str(vals)
    #         #raise ValidationError('')

    #     hr_holiday_id = super(HrHolidays, self).write(cr, uid, ids, vals, context=context)
    #     #self.add_follower(cr, uid, ids, employee_id, context=context)
    #     return hr_holiday_id

    @api.model
    def get_employee_calendar(self, employee):
        calendar = None
        if employee.resource_id.calendar_id:
            calendar = employee.resource_id.calendar_id.id
        return calendar

    @api.one
    def holidays_validate(self):
        if not self.holiday_type == 'employee':
            return super(HrHolidays, self).holidays_validate()

        try:
            res_id = self.env['ir.model.data'].get_object(
                'hr_public_holidays', 'hr_public_holiday').id
        except ValueError:
            raise Warning(
                _("Leave Type for Public Holiday not found!"))

        if self.holiday_status_id.id != res_id:
            return super(HrHolidays, self).holidays_validate()

        calendar = self.get_employee_calendar(self.employee_id)

        self.env['resource.calendar.leaves'].create({
            'name': self.name,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'resource_id': self.employee_id.resource_id.id,
            'calendar_id': calendar,
            'holiday_id': self.id
        })
        self.state = 'validate'
