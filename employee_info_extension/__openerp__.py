# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Employee Information Extension',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'Infinite Business Solution Co.,Ltd',
    'website': 'www.ibizmyanmar.com',
    'category' : 'Employee',
    'description': """

Modify Employee Information
===========================

This module will modify employee information

    """,
    'depends': ['hr','hr_contract','hr_recruitment','base','web_m2x_options'],
    'data' : [
        'hr_employee_view.xml',
        #'security/ir.model.access.csv',
        #'security/hr_security.xml'
    ],
}
