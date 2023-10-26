
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

{
    'name': 'HR Payroll extension',
    'description':'To calculate overtime',
    'summary':'HR Payroll extension',
    'author': 'Infinite Business Solution Co.,Ltd',
    'website': 'www.ibizmyanmar.com',
    'depends':['base','hr_payroll','hr_contract_extension','hr_attendance_extension','web_list_view_sticky'],
    'category': 'HR',
    'application':True,
    'data':[
            'hr_payroll_view.xml',
    		'ot_check_view.xml',
    		#'ot_request_workflow.xml',
            'wizard/hr_payroll_payslips_checking.xml',
    		'security/ir.model.access.csv',
    		'security/hr_security.xml'
    	],
    
}