# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _

class hr_payslip_checking(osv.osv_memory):

    _name ='hr.payslip.checking.wizard'
    _description = 'Generate payslip checking for all selected employees'
    _columns = {
        'employee_ids': fields.many2many('hr.employee', string='Employees'),
    }

    _defaults = {
        'employee_ids' : lambda self, cr, uid, context: context.get('employee_ids',False),
        }
    
    def compute_sheet(self, cr, uid, ids, context=None):
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        payslilp_checking_obj = self.pool.get('hr.payslip.checking')
        duty_roster_obj = self.pool.get('hr.employee.duty.roster.line')

        # emp_id must unique
        # all employee have department and job and emp_id
        # all employee have contract and must one

        # all contract must have attendance
        # all contract must have dutyroster
        # all dutyroster must have approve state
        # late day is sutiable
        # all ot request must approve and refuse
        # all leave request must approve and refuse
        # all department name, job name unique

        emp_pool = self.pool.get('hr.employee')
        slip_pool = self.pool.get('hr.payslip')
        run_pool = self.pool.get('hr.payslip.run')
        active_id = None
        slip_ids = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            active_id = context['active_id']
            run_data = run_pool.read(cr, uid, [context['active_id']], ['date_start', 'date_end', 'credit_note'])[0]

        from_date =  run_data.get('date_start', False)
        to_date = run_data.get('date_end', False)
        credit_note = run_data.get('credit_note', False)

        message = []

        # ------------------------------------------------------

        contract_id = []
        duty_roster_contract_not_exit = []
        contract_ids = contract_obj.search(cr,uid,[])
        print contract_ids
        for cont in contract_ids:
            duty_roster_id = duty_roster_obj.search(cr,uid,[('contract_id','=',cont),('date_from','=',from_date)])
            if duty_roster_id:
                contract_id.append(duty_roster_id)
            else:
                emp_id = contract_obj.browse(cr,uid,cont).employee_id.emp_id
                if emp_id:
                    duty_roster_contract_not_exit.append(str(emp_id))

        duty_roster_contract_not_exit = 'DUTYROSTER NOT EXIST -> ' + str(duty_roster_contract_not_exit)
        message.append(duty_roster_contract_not_exit)
        print contract_id
        print duty_roster_contract_not_exit

        # ------------------------------------------------------

        sql = "SELECT he.emp_id FROM hr_contract hc LEFT JOIN hr_employee he ON (he.id=hc.employee_id) WHERE hc.wage = 0.0"
        cr.execute(sql)
        contract_wage_not_exit = []
        for a in cr.fetchall():
            if a[0]:
                contract_wage_not_exit.append(str(a[0]))
        contract_wage_not_exit = 'CONTRACT NO WAGE -> ' + str(contract_wage_not_exit)
        message.append(contract_wage_not_exit)
        print contract_wage_not_exit

        # ------------------------------------------------------

        duty_roster_approve = 0
        sql = "SELECT count(id) FROM hr_employee_duty_roster WHERE state='draft'"
        cr.execute(sql)
        duty_roster_approve = int(cr.fetchall()[0][0])
        message.append('DUTYROSTE NOT APPROVE -> ' + str(duty_roster_approve))

        # ------------------------------------------------------

        print message
        print len(duty_roster_contract_not_exit)
        print len(contract_wage_not_exit)
        print duty_roster_approve

        #if len(duty_roster_contract_not_exit) > 0 and len(contract_wage_not_exit) > 0 and duty_roster_approve > 0:
        #    raise osv.except_osv(_('Warning Data Not Exist!'),_(str(message)))

        if not data['employee_ids']:
            raise osv.except_osv(_("Warning!"), _("You must select employee(s) to generate payslip(s)."))
        for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
            context = {'from':'payslip_checking'}
            slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=False, context=context)
            #print slip_data
            #slip_data['value'].get('ot_check_id', False)

        all_contract = contract_obj.search(cr,uid,[])
        print 'all_contract ' + str(len(all_contract))
        all_payslip_checking = payslilp_checking_obj.search(cr,uid,[('date_from','=',from_date),('date_to','=',to_date)])
        print 'all_payslip_checking ' + str(len(all_payslip_checking))
        #if all_contract == all_payslip_checking:
        #    run_pool.write(cr,uid,active_id,{'state':'generate'},context=context)
        #else:
        #    message = "Payslip Checking Not Complete"
        #    raise osv.except_osv(_('Warning!'),_(str(message)))

        return {'type': 'ir.actions.act_window_close'}

class hr_payslip_employees(osv.osv_memory):

    _inherit ='hr.payslip.employees'
    _description = 'Generate payslips for all selected employees'
    _columns = {
        'employee_ids': fields.many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees'),
    }
    
    def compute_sheet(self, cr, uid, ids, context=None):
        # payslip batch manual approve check
        print 'child hr_payslip_employees work'
        emp_pool = self.pool.get('hr.employee')
        slip_pool = self.pool.get('hr.payslip')
        run_pool = self.pool.get('hr.payslip.run')
        slip_ids = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, [context['active_id']], ['date_start', 'date_end', 'credit_note'])[0]
        from_date =  run_data.get('date_start', False)
        to_date = run_data.get('date_end', False)
        credit_note = run_data.get('credit_note', False)
        if not data['employee_ids']:
            raise osv.except_osv(_("Warning!"), _("You must select employee(s) to generate payslip(s)."))
        for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
            slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=False, context=context)
            
            print slip_data['value'].get('ot_check_id', False)
            #print int('a')
            res = {
                'employee_id': emp.id,
                'name': slip_data['value'].get('name', False),
                'struct_id': slip_data['value'].get('struct_id', False),
                'contract_id': slip_data['value'].get('contract_id', False),
                'payslip_run_id': context.get('active_id', False),
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': credit_note,
                'ot_check_id': slip_data['value'].get('ot_check_id', False)
            }
            slip_ids.append(slip_pool.create(cr, uid, res, context=context))
        slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
