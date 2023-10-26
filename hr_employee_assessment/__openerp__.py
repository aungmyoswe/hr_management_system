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
    'name': 'HR Assessment',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """
Make Employee Assessment Records
=======================================================
    1. Create questions and question-types before creating assessment record
    2. Link to employees
    3. Review results of assessment for each employee
    """,
    'author': 'Infinite Business Solution Co.,Ltd',
    'website': 'www.ibizmyanmar.com',
    'depends':['hr','cci_employee_info_extension'],
    'category': 'Category',
    'application':True,
    'data':['hr_assessment_view.xml','views/resource_template.xml',],
}
