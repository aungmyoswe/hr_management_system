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
    'name': 'Treatment',
    'description': """
Make Employee Treatment Records
====================================
    1. Create treatment list for each employee
    2. Link treatment record to employees
    3. Review results of employees for each treament
    """,
    'summary':'Treatment, Doctor, Drug',
    'author': 'Infinite Business Solution Co.,Ltd',
    'website': 'www.ibizmyanmar.com',
    'depends':['hr'],
    'category': 'Human Resources',
    'application':True,
    'data':['treatment_view.xml'],
}
