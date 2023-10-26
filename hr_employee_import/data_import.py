from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging
_logger = logging.getLogger(__name__)

header_fields = ['emp id','eng name','burmese name','nrc no'  ,'position' ,'section','sub section','department'  ,
                 'joining date'  ,'education'  ,'blood type'  ,'birthday'  ,'ssn id'  ,'father name' , 'work email',
                 'mother name'  ,'marital status'  ,'spouse name' ,'spouse job', 'spouse birthday', 'working experiences',
                 'child number','address' ,'mobile phone' ,'wage' ,'special allowance', 'office order no','gender','religion',
                 'license no','permenant date','guardian name','guardian phone','promotion order no',
                 'child name 1' ,'child birthday 1','child education 1',
                 'child name 2' ,'child birthday 2','child education 2',
                 'child name 3' ,'child birthday 3','child education 3',
                 'child name 4' ,'child birthday 4','child education 4',
                 'child name 5' ,'child birthday 5','child education 5',]

#### Field indexes for related database fields
header_indexes = {}

class employee(osv.osv):
    _name = 'data_import.employee'
    _columns = {
              'name':fields.char('Description'),
              'import_date':fields.date('Import Date', readonly=True),
              'import_fname': fields.char('Filename', size=128),
              'import_file':fields.binary('File', required=True),
              'note':fields.text('Log'),
              'company_id': fields.many2one('res.company', 'Company', required=False),
              'state':fields.selection([
                ('draft', 'Draft'),
                ('completed', 'Completed'),
                ('error', 'Error'),
            ], 'States'),
              
              }
    _defaults = {
            'state':'draft',
            'import_date':datetime.today(),
                 }
    
    err_log = ''
#     finger_id_i = employee_id_i = name_i = position_i = deaprtment_i = first_working_day_i = end_of_probation_i = None
#     lcoation_i = job_level_i = job_family_i = agd_bank_ac_no_i = ssb_no_i = income_tax_ac_no_i = end_date_i = None
#     nrc_no_i = father_name_i = nationallity_i = religion_i = education_background_i = others_qualification_i = None
#     date_of_birth_i = age_i = blood_type_i = marital_status_i = child_i = contact_address_i = company_email_i = None
#     email_address_i = mobile_i = None
    
    
    
    def _check_file_ext(self, cursor, user, ids):
        for import_file in self.browse(cursor, user, ids):
            if '.xls' in import_file.import_fname:return True
            else: return False
        return True
    
    _constraints = [(_check_file_ext, "Please import EXCEL file!", ['import_fname'])]
    
    # ## Load excel data file
    def get_excel_datas(self, sheets):
        result = []
        for s in sheets:
            # # header row
            headers = []
            header_row = 0
            for hcol in range(0, s.ncols):
                headers.append(s.cell(header_row, hcol).value)
                            
            result.append(headers)
            
            # # value rows
            for row in range(header_row + 1, s.nrows):
                values = []
                for col in range(0, s.ncols):
                    values.append(s.cell(row, col).value)
                result.append(values)
        return result
    
    # ## Check excel row headers with header_fields and define header indexes for database fields
    def get_headers(self, line):
        if line[0].strip().lower() not in header_fields:
                    raise orm.except_orm(_('Error :'), _("Error while processing the header line %s.\
                     \n\nPlease check your Excel separator as well as the column header fields") % line)
        else:
            # ## set header_fields to header_index with value -1
            for header in header_fields:
                header_indexes[header] = -1  
                     
            col_count = 0
            for ind in range(len(line)):
                if line[ind] == '':
                    col_count = ind
                    break
                elif ind == len(line) - 1:
                    col_count = ind + 1
                    break
            
            for i in range(col_count):                
                header = line[i].strip().lower()
                if header not in header_fields:
                    self.err_log += '\n' + _("Invalid Excel File, Header Field '%s' is not supported !") % header
                else:
                    header_indexes[header] = i
                                
            for header in header_fields:
                if header_indexes[header] < 0:                    
                    self.err_log += '\n' + _("Invalid Excel file, Header '%s' is missing !") % header
    
    #### Fill excel row data into list to import to database
    def get_line_data(self, line):
        result = {}
        for header in header_fields:                        
            result[header] = line[header_indexes[header]].strip()
    
    #### validate date values        
    def check_date_value(self, date_value, message):
        result_date = None
        try:
            data_time = float(date_value)
            print data_time
            result = xlrd.xldate.xldate_as_tuple(data_time, 0)
            a = str(result[0]) + '/' + str(result[1]) + '/' + str(result[2]) + ' ' + str(result[3]) + ':' + str(result[4]) + ':' + str(result[5])
    
            result_date = datetime.strptime(a, '%Y/%m/%d %H:%M:%S').date()
        except Exception, e:
            try:
                str_date = str(date_value) + ' 00:00:00'
                print str_date
                result_date = datetime.strptime(str_date, '%d.%m.%Y %H:%M:%S').date()
		print '1'
            except Exception, e:
                try:
                    str_date = str(date_value) + ' 00:00:00'
                    result_date = datetime.strptime(str_date, '%Y.%m.%d %H:%M:%S').date()
                    print '2'
                except Exception, e:
                    try:
                        str_date = str(date_value) + ' 00:00:00'
                        result_date = datetime.strptime(str_date, '%d.%m.%Y %H:%M:%S').date()
                        print '3'
                    except Exception, e:
                        try:
                          str_date = str(date_value) + ' 00:00:00'
                          result_date = datetime.strptime(str_date, '%d-%m-%y %H:%M:%S').date()
                          print '4'
                        except Exception, e:
                          return None             
                          print '5'         
#                             raise orm.except_orm(_('Error :'), _("Error while processing Excel Columns.\
#                          \n\nPlease check your " + message + " !"))                        
        return result_date
    
    ######### Read data and import to database ##########        
    def import_data(self, cr, uid, ids, context=None):
        hr_employee_obj = self.pool.get('hr.employee')
        hr_job_obj = self.pool.get('hr.job')
        hr_department_obj = self.pool.get('hr.department')
        hr_section_obj = self.pool.get('hr.section')
        hr_sub_section_obj = self.pool.get('hr.sub.section')
        res_partner_obj = self.pool.get('res.partner')
        hr_contract_obj = self.pool.get('hr.contract')
        hr_employee_children_obj = self.pool.get('hr.employee.children')
        #hr_struct_obj = self.pool.get('hr.payroll.structure')
        #struct_id = hr_struct_obj.search(cr, uid, [('code','=','SSOPER')])[0]
        
        data = self.browse(cr, uid, ids)[0]
        import_file = data.import_file                
        
        header_line = True
        lines = base64.decodestring(import_file)
        wb = open_workbook(file_contents=lines)
        excel_rows = self.get_excel_datas(wb.sheets())        
        value = {}
        all_data = []
        created_counnt = 0
        updated_count = 0
        
        for line in excel_rows:
            if not line or line and line[0] and line[0] in ['', '#']:
                continue
            
            if header_line:
                self.get_headers(line)
                header_line = False                           
            elif line and line[0] and line[0] not in ['#', '']:
                import_vals = {}
                # ## Fill excel row data into list to import to database
                print header_fields 
                print line
                for header in header_fields:
                    import_vals[header] = line[header_indexes[header]]
                
                all_data.append(import_vals)
       
        if self.err_log <> '':
            self.write(cr, uid, ids[0], {'note': ''})
            self.write(cr, uid, ids[0], {'note': self.err_log})
            self.write(cr, uid, ids[0], {'state': 'error'})
        else:
            for data in all_data:
                print '------------'
                print 'excel row => ' + str(all_data.index(data) + 2)
                print 'data ' + str(data)
                                  
                #### ids of relation table
                job_id = department_id = section_id = sub_section_id = None 
                address = address_home_id = None                
                 
                birthday = None
                
                ##### to hold value for database
                value = {}
                
                emp_id = data['emp id'].encode('utf-8')
                print emp_id
                emp_eng_name = data['eng name'].encode('utf-8')
                emp_burmese_name = data['burmese name'].encode('utf-8')
                #### Those data are relation in employee table
                #### Must be validate and insert into relation table if data not found
           
                job_name = data['position'].encode('utf-8')
                work_email = data['work email'].encode('utf-8')
                department_name = data['department'].encode('utf-8')
                section_name = data['section'].encode('utf-8')
                sub_section_name = data['sub section'].encode('utf-8')
                address = data['address'].encode('utf-8')
                wage = data['wage']
                specail_allowance = data['special allowance']
                 
                #### Date values need to validate
                joining_date = data['joining date']
                trial_date_end = data['permenant date']
                birthday = data['birthday']
		spouse_birthday = data['spouse birthday']
                 
                #### For Department
                if department_name: 
                    dept_ids = hr_department_obj.search(cr, uid, [('name', '=', department_name)])                    
                    if not dept_ids:
                        dept_value = {'name':department_name} #,'sequence':0
                        department_id = hr_department_obj.create(cr, uid, dept_value, context)
                        print 'department create ...'
                    else:
                        department_id = dept_ids[0]
                        
                #### For Section
                if job_name:
                  sec_ids = hr_section_obj.search(cr, uid, [('name', '=', section_name),('department_id', '=', department_id)])
                  if not sec_ids:
                    sec_value = {'name':section_name,'department_id':department_id} #,'sequence':0
                    section_id = hr_section_obj.create(cr, uid, sec_value, context)
                    print 'section create ...'
                  else:
                    section_id = sec_ids[0]
                        
                #### For Sub Section
                if job_name: 
                    sub_sec_ids = hr_sub_section_obj.search(cr, uid, [('name', '=', sub_section_name),('section_id', '=', section_id),('department_id', '=', department_id)])                    
                    if not sub_sec_ids:
                        sub_sec_value = {'name':sub_section_name,'section_id': section_id,'department_id':department_id} #,'sequence':0
                        sub_section_id = hr_sub_section_obj.create(cr, uid, sub_sec_value, context)
                        print 'sub section create ...'
                    else:
                        sub_section_id = sub_sec_ids[0]

                #### For Position
                # first department search,second section,that used in sub section
                if job_name:
                    job_ids = hr_job_obj.search(cr, uid, [('name', '=', job_name),('department_id', '=', department_id),('section_id', '=', section_id),('sub_section_id', '=', sub_section_id)])
                    if not job_ids:
                        job_value = {'name':job_name,'department_id':department_id,'section_id':section_id,'sub_section_id':sub_section_id,}
                        job_id = hr_job_obj.create(cr, uid, job_value, context)
                        print 'job create ...'
                    else:
                        job_id = job_ids[0]
                        
                #### For Contact Address        
                if address and emp_eng_name:
                    address_ids = res_partner_obj.search(cr, uid, [('name', '=', emp_eng_name)])
                    if not address_ids:
                        address_value = {
                                     'name':emp_eng_name,
                                     'street':address,
                                     'customer':False,
                                     'supplier':False
                                     }
                        address_id = address_home_id = res_partner_obj.create(cr, uid, address_value, context)
                    else:
                        address_id = address_home_id = address_ids[0]
                        address_value = {
                                     'street':address,
                                     }
                        res_partner_obj.write(cr,uid,address_id,address_value)
                  
                if birthday:
                    birthday = self.check_date_value(birthday, 'Date_Of_Birth')
                    print 'birthday=' + str(birthday)
                     
                if joining_date:
                    joining_date = self.check_date_value(joining_date, 'Joining Date')
                    print 'joining=' + str(joining_date)

		if trial_date_end:
                    trial_date_end = self.check_date_value(trial_date_end, 'Trial Date End')
                    print 'trial_date_end=' + str(trial_date_end)

                if spouse_birthday:
                    spouse_birthday = self.check_date_value(spouse_birthday, 'Spouse Birthday')
                    print 'spouse_birthday=' + str(spouse_birthday)
                 
                 
                #### set values for employees      
                if emp_id: value['emp_id'] = emp_id          
                if job_id : value['job_id'] = job_id
                if section_id : value['section_id'] = section_id
                if sub_section_id : value['sub_section_id'] = sub_section_id
                if department_id : value['department_id'] = department_id
                if address_home_id : value['address_home_id'] = address_home_id
                if birthday: value['birthday'] = birthday
                 
                if emp_eng_name: value['name'] = emp_eng_name      
                if emp_burmese_name: value['burmese_name'] = emp_burmese_name                    
                 
                marital = data['marital status']
                if marital == 'Single':
                  value['marital'] = 'single'
                elif marital == 'Married':
                  value['marital'] = 'married'

                gender = data['gender']
                if gender == 'Male':
                  value['gender'] = 'male'
                elif gender == 'Female':
                  value['gender'] = 'female'
                 
                if data['nrc no']:value['identification_id']= data['nrc no'].encode('utf-8')
                  
                #### Date values need to validate
                 
                if data['education']:value['education'] = data['education']
                if data['working experiences']:value['working_experience'] = data['working experiences']
                if data['office order no']:value['office_order_no'] = data['office order no']
                if data['religion']:value['religion'] = data['religion']
                if data['blood type']:value['blood_group'] = data['blood type']
                if data['ssn id']: value['ssnid'] = data['ssn id'] 
                if data['license no']: value['license_no'] = data['license no'] 
		if data['promotion order no']: value['promotion_order_no'] = data['promotion order no']
                if data['father name']: value['fam_father'] = data['father name']
                if data['mother name']: value['fam_mother'] = data['mother name']
                if data['spouse name']:value['fam_spouse'] = data['spouse name']
                if data['spouse job']:value['fam_spouse_employer'] = data['spouse job']
                if spouse_birthday:value['fam_spouse_dob'] = spouse_birthday
		if data['guardian name']:value['guardian_name'] = data['guardian name']
                if data['guardian phone']:value['guardian_phone'] = data['guardian phone']
                if data['child number']:value['children'] = data['child number']
                if data['address']:value['address_home_id'] = address_id
                if data['mobile phone']:value['mobile'] = data['mobile phone']
                if data['work email']:value['work_email'] = work_email
                if joining_date :value['trial_date_start'] = joining_date
                if trial_date_end :value['trial_date_end'] = trial_date_end
                 
                if wage:value['wage'] = data['wage']
                 
                employee_ids = hr_employee_obj.search(cr, uid, [('name', '=', emp_eng_name),('emp_id', '=', data['emp id'])]) 
                print employee_ids
                       
                if employee_ids: 
                    hr_employee_obj.write(cr, uid, employee_ids[0], value)
                    print 'employee update ...'
                    employee_id = employee_ids[0]
                    updated_count = updated_count + 1
                else :
                    employee_id = hr_employee_obj.create(cr, uid, value, context = context)
                    print 'employee create ...'
                    created_counnt = created_counnt + 1
                     
                print data['child number']
                  
                if employee_id:
                  if data['child number']:
                    chil_ids = hr_employee_children_obj.search(cr, uid, [('employee_id', '=', employee_id)])                    
                      
                    ch_no = data['child number']
                    count = 1
                    index = 0
                      
                    while(count <= ch_no):
                      #print count
                      chil_value = {}
                        
                      #print data['child name '] + str(int(count))
                      chil_value['employee_id'] = employee_id
                      if data['child name ' + str(int(count))]:
                        chil_value['name'] = data['child name ' + str(int(count))]
                      else:
                        count = count + 1
                        continue
                      if data['child birthday ' + str(int(count))]:
                        chil_value['date_of_birth']= self.check_date_value(data['child birthday ' + str(int(count))], 'child Birthday')
                      if data['child education ' + str(int(count))]:
                        chil_value['education'] = data['child education ' + str(int(count))]
                      else:
                        chil_value['education'] = ''
                        
                      count = count + 1
                        
                      #print 'chil ids'
                      #print chil_ids
                      print '---------------'
                      print chil_value
                      if not chil_ids:
                          hr_employee_children_obj.create(cr, uid, chil_value, context)
                          print 'child create ...'
                      else:
                          print chil_value
                          print index
                          print chil_ids[index]
                          hr_employee_children_obj.write(cr, uid, chil_ids[index],chil_value[index])
                          index = index + 1
                          print 'child update ...'
  
                if employee_id and joining_date:
                    contract_ids = hr_contract_obj.search(cr, uid, [('employee_id','=',employee_id)])
                    if not contract_ids:
                        contract_value={}
                        contract_type = self.pool.get('hr.contract.type').search(cr, uid, [('name','=','Employee')])
                        contract_value['name'] = emp_eng_name + ' Contract'        
                        contract_value['employee_id'] = employee_id
                        contract_value['type_id'] = contract_type[0] or 1
                        contract_value['job_id'] = job_id
                        contract_value['date_start'] = joining_date
                        contract_value['trial_date_start'] = joining_date
                        if trial_date_end: contract_value['trial_date_end'] = trial_date_end
                        contract_value['specail_allowance'] = specail_allowance
                        contract_value['wage'] = wage
                        contract_value['struct_id'] = 1
                        hr_contract_obj.create(cr, uid, contract_value, context = context)
                        print 'contract create ...'
                    else:
                        employee = hr_employee_obj.browse(cr, uid, employee_id)
                        contract_value = {}
                        contract_value['job_id'] = job_id
                        contract_value['date_start'] = joining_date
                        contract_value['trial_date_start'] = joining_date
                        if trial_date_end: contract_value['trial_date_end'] = trial_date_end
                        contract_value['specail_allowance'] = specail_allowance
                        contract_value['wage'] = wage
                        contract_value['struct_id'] = 1
                        hr_contract_obj.write(cr, uid, employee.contract_id.id, contract_value)
                        print 'contract update ...'
                
            message = 'Import Success at ' + str(datetime.strptime(datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                      '%Y-%m-%d %H:%M:%S'))+ '\n' + str(updated_count + created_counnt)+' records imported' +'\
                      \n' + str(created_counnt) + ' created\n' + str(updated_count) + ' updated'
                      
            self.write(cr, uid, ids[0], {'state': 'completed','note': message})            

# Under class is for hr_contract
