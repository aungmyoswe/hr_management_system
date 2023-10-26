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

header_fields = ['employee name','employee id','date','code','amount']
#### Field indexes for related database fields
header_indexes = {}

class Payroll_Input(osv.osv):
    _name = 'data_import.payroll'
    _columns = {
              'name':fields.char('Description'),
              'import_date':fields.date('Import Date', readonly=True),
              'import_fname': fields.char('Filename', size=128),
              'import_file':fields.binary('File', required=True),
              'payslip_run':fields.many2one('hr.payslip.run','Payslip Batch'),
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
    
    ######### Read data and import to database ##########        
    
    def import_data_by_amount(self, cr, uid, ids, context=None):
        hr_employee_obj = self.pool.get('hr.employee')
        hr_contract_obj = self.pool.get('hr.contract')
        pay_slip_obj = self.pool.get('hr.payslip')
        input_amount_obj = self.pool.get('hr.payslip.input')
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
        amount_skipped_list = []
        slip_skipped_list = []
        contract_skipped_list = []
        date_skipped_list = []
        code_skipped_list = []
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
                    employee_skipped_list.append(str(excel_row)) 
                    continue
                
                amount = float(data['amount'])                
                if not amount:
                    print 'amount skip'
                    skipped_count = skipped_count + 1
                    amount_skipped_list.append(str(excel_row))
                    continue

                date_from = data['date']
                date_from = self.check_date_value(date_from, 'Date')
                print date_from                
                if not date_from:
                    print 'date_from skip'
                    skipped_count = skipped_count + 1
                    date_skipped_list.append(str(excel_row))
                    continue

                code = data['code']                
                if not code:
                    print 'code skip'
                    skipped_count = skipped_count + 1
                    code_skipped_list.append(str(excel_row))
                    continue

                is_yei = False
                if code == 'YEI':
                    is_yei = True
                    contract_ids = hr_contract_obj.search(cr,uid,[('employee_id','=',employee_id)]) #,('year_end_date','!=',date_from)
                    contract = hr_contract_obj.browse(cr,uid,contract_ids[0])
                    if not contract_ids:
                        print 'contract skip'
                        skipped_count = skipped_count + 1
                        contract_skipped_list.append(str(excel_row))
                        continue
                    else:
                        year_end_date = contract.year_end_date
                        print '-'
                        print year_end_date
                        print date_from
                        if year_end_date != str(date_from) and year_end_date < str(date_from):
                            hr_contract_obj.write(cr, uid, contract_ids[0], {"year_end_increment": amount,"year_end_date": date_from})
                            updated_count += 1
                else:

                    slip_ids = pay_slip_obj.search(cr, uid, [('employee_id','=',employee_id),('date_from','=',date_from)])
                    if not slip_ids:
                        print 'slip skip'
                        skipped_count = skipped_count + 1
                        slip_skipped_list.append(str(excel_row))
                        continue
                    else:
                        for slip_id in slip_ids:
                            input_amount_ids = input_amount_obj.search(cr, uid, [('payslip_id', '=', slip_id),('code', '=', code)])
                            if not input_amount_ids:
                                skipped_count = skipped_count + 1
                                slip_skipped_list.append(str(excel_row))
                                continue
                            else:
                                input_amount_obj.write(cr, uid, input_amount_ids[0], {'amount':amount})
                                updated_count += 1

                            # print code
                            # print slip_ids
                            # print slip_id
                            # raise ValidationError('')
                            
                            print 'Employee ID =' + emp_id
                            print 'ID = ' + str(slip_id)
            
            skipped_list.append('employee skip list - ' + str(employee_skipped_list))
            skipped_list.append('amount skip list   - ' + str(amount_skipped_list))

            if is_yei:
                skipped_list.append('contract skip list - ' + str(contract_skipped_list))
            else:
                skipped_list.append('slip skip list     - ' + str(slip_skipped_list))
            skipped_list.append('date skip list     - ' + str(date_skipped_list))
            skipped_list.append('code skip list     - ' + str(code_skipped_list))

            message = 'Import Success at ' + str(datetime.strptime(datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                      '%Y-%m-%d %H:%M:%S'))+ '\n' + str(len(all_data)) +' records imported' +'\
                      \n' + str(created_counnt) + ' created\n' + str(updated_count) + ' updated' + '\
                      \n' + str(skipped_count) + ' skipped' + '\
                      \n' + str(skipped_list)
                      
            self.write(cr, uid, ids[0], {'state': 'completed','note': message})
