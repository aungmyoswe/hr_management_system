from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64
import logging
from openerp.exceptions import ValidationError
_logger = logging.getLogger(__name__)

header_fields = ['employee name','employee id','code','start time','end time','date','hours']
#### Field indexes for related database fields
header_indexes = {}

class Payroll_Input(osv.osv):
    _name = 'data_import.ot'
    _columns = {
              'name':fields.char('Description'),
              'import_date':fields.date('Import Date', readonly=True),
              'import_fname': fields.char('Filename', size=128),
              'import_file':fields.binary('File', required=True),
              'note':fields.text('Log'),
              'company_id': fields.many2one('res.company', 'Company', required=False),
              'user_id': fields.many2one('res.user', 'Employee'),
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

    def _check_file_ext(self, cursor, user, ids):
        for import_file in self.browse(cursor, user, ids):
            if '.xls' in import_file.import_fname:return True
            else: return False
        return True
    
    _constraints = [(_check_file_ext, "Please import EXCEL file!", ['import_fname'])]
    
    #### Load excel data file
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
    
    #### Check excel row headers with header_fields and define header indexes for database fields
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
        print date_value
        try:
            result_date = datetime.strptime(date_value,'%d-%m-%Y').date()
        except Exception, e:
            try:
                result_date = datetime.strptime(date_value, '%Y-%m-%d').date()
            except Exception, e:
                return None                     
        return result_date

    #### validate time values        
    def check_time_value(self, date_value, message):
        result_time = None
        print result_time
        try:
            result_time = datetime.strptime(date_value,'%H:%M').time()
        except Exception, e:
            return None                     
        return result_time
    
    ######### Read data and import to database ##########        
    
    def import_data_by_amount(self, cr, uid, ids, context=None):
        hr_employee_obj = self.pool.get('hr.employee')
        ot_request_obj = self.pool.get('hr.ot.request')
        od_request_obj = self.pool.get('hr.od.request')
        
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
        skipped_count = 0

        employee_skipped_list = []
        hours_skipped_list = []
        date_skipped_list = []
        code_skipped_list = []
        starttime_skipped_list = []
        endtime_skipped_list = []
        skipped_list = []
        
        for line in excel_rows:
            if not line or line and line[0] and line[0] in ['', '#']:
                continue
            
            if header_line:
                self.get_headers(line)
                header_line = False                           
            elif line and line[0] and line[0] not in ['#', '']:
                import_vals = {}
                # ## Fill excel row data into list to import to database
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
                excel_row = all_data.index(data) + 2
                print 'excel row => ' + str(excel_row)
                print 'data ' + str(data)

                employee_id = None                                 
                amount = None
                
                emp_id = data['employee id'].encode('utf-8').strip()
                employee_name = data['employee name'].encode('utf-8').strip()
                       
                if emp_id:
                    emp_ids = hr_employee_obj.search(cr, uid, [('emp_id', '=', emp_id)])
                    if emp_ids:
                        employee_id = emp_ids[0]
                        print employee_id
          
                if not employee_id:
                    print 'employee skip'
                    skipped_count = skipped_count + 1
                    employee_skipped_list.append(str(emp_id) + ' ,') 
                    continue

                start_time = data['start time']
                start_time = self.check_time_value(start_time, 'Start Time')
                print start_time                
                if not start_time:
                    print 'start_time skip'
                    skipped_count = skipped_count + 1
                    starttime_skipped_list.append(str(excel_row) + ' ,')
                    continue

                end_time = data['end time']
                end_time = self.check_time_value(end_time, 'Out Time')
                print end_time                
                if not end_time:
                    print 'end_time skip'
                    skipped_count = skipped_count + 1
                    endtime_skipped_list.append(str(excel_row) + ' ,')
                    continue

                date = data['date']
                date = self.check_date_value(date, 'Date')
                print date               
                if not date:
                    print 'date skip'
                    skipped_count = skipped_count + 1
                    date_skipped_list.append(str(excel_row) + ' ,')
                    continue

                hours = float(data['hours'])                
                if not hours:
                    print 'hours skip'
                    skipped_count = skipped_count + 1
                    hours_skipped_list.append(str(excel_row) + ' ,')
                    continue

                code = data['code']                
                if not code:
                    print 'code skip'
                    skipped_count = skipped_count + 1
                    code_skipped_list.append(str(excel_row) + ' ,')
                    continue

                if code == 'OT':
                    ot_value = {
                        'employee_id': employee_id,
                        'date': date,
                        'start_time': start_time,
                        'end_time': end_time,
                        'total_hours': hours
                    }
                    ot_request_ids = ot_request_obj.search(cr,uid,[('employee_id','=',employee_id),('date','=',date)])
                    if not ot_request_ids:
                        ot_request_obj.create(cr, uid, ot_value)
                    else:
                        ot_request_obj.write(cr, uid, ot_request_ids[0], ot_value)
                elif code == 'OD':
                    od_value = {
                        'employee_id': employee_id,
                        'date': date,
                        'start_time': start_time,
                        'end_time': end_time,
                        'total_hours': hours
                    }
                    od_request_ids = od_request_obj.search(cr,uid,[('employee_id','=',employee_id),('date','=',date)])
                    if not od_request_ids:
                        od_request_obj.create(cr, uid, od_value)
                    else:
                        od_request_obj.write(cr, uid, od_request_ids[0], od_value)

            skipped_list.append('employee skip list - ' + str(employee_skipped_list))
            skipped_list.append('code skip list     - ' + str(code_skipped_list))
            skipped_list.append('date skip list     - ' + str(date_skipped_list))
            skipped_list.append('starttime skip list- ' + str(starttime_skipped_list))
            skipped_list.append('endtime skip list  - ' + str(endtime_skipped_list))
            skipped_list.append('hours skip list    - ' + str(hours_skipped_list))

            message = 'Import Success at ' + str(datetime.strptime(datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                      '%Y-%m-%d %H:%M:%S'))+ '\n' + str(len(all_data)) +' records imported' +'\
                      \n' + str(created_counnt) + ' created\n' + str(updated_count) + ' updated' + '\
                      \n' + str(skipped_count) + ' skipped' + '\
                      \n' + str(skipped_list)
                      
            self.write(cr, uid, ids[0], {'state': 'completed','note': message})
