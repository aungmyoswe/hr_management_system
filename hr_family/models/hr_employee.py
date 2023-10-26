# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    
    fam_spouse = fields.Char("Name")
    fam_spouse_employer = fields.Char("Employer")
    fam_spouse_tel = fields.Char("Telephone.")
    fam_spouse_dob = fields.Date("Date of Birth")
    tax_spouse = fields.Boolean('Tax Exception')
    fam_children_ids = fields.One2many(
        'hr.employee.children', 'employee_id', "Children")
    fam_father = fields.Char("Father's Name")
    fam_father_date_of_birth = fields.Date(
        "Date of Birth", oldname='fam_father_dob')
    #Create tax Exception for family by thurein soe 9/19/2017
    tax_father = fields.Boolean('Tax Exception')

    fam_mother = fields.Char("Mother's Name")
    fam_mother_date_of_birth = fields.Date(
        "Date of Birth", oldname='fam_mother_dob')
    tax_mother = fields.Boolean('Tax Exception')

    fam_father_in_law = fields.Char('Father in Law')
    tax_father_law = fields.Boolean('Tax Exception')

    fam_mother_in_law = fields.Char('Mother in Law')
    tax_mother_law = fields.Boolean('Tax Exception')

    guardian_name = fields.Char('Guardian Name')
    guardian_phone = fields.Char('Guardian Phone')


