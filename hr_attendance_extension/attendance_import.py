from openerp.osv import orm
from openerp.osv import fields, osv
import xlrd
import codecs
from xlrd import open_workbook
from openerp.tools.translate import _
from datetime import datetime
import base64, StringIO, csv
import io
from tempfile import TemporaryFile
import logging
from passlib.tests.backports import skip
from openerp.exceptions import ValidationError
_logger = logging.getLogger(__name__)

header_indexes = {}

class attendance(osv.osv):
    _name = 'data_import.attendance'
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

    def _check_file_ext(self, cursor, user, ids):
        for import_file in self.browse(cursor, user, ids):
            if '.dat' or '.DAT' or '.xls' in import_file.import_fname:return True
            else: return False
        return True
    
    _constraints = [(_check_file_ext, "Please import EXCEL file!", ['import_fname'])]
    
    # ## Load excel data file
    def get_excel_datas(self, sheets):
        result = []
        for s in sheets:
            cell_row=0
            for row in range(cell_row, s.nrows):
                values = []
                for col in range(0, s.ncols):
                    values.append(s.cell(row, col).value)
                result.append(values)
        return result
    
    
    #### validate date values        
    def check_date_value(self, date_value, message):
        result_date = None
        try:
            print 'here'
            result_date = datetime.strptime(date_value, '%Y-%m-%d').date()
        except Exception, e:
            try:
                str_date = str(date_value) + ' 00:00:00'
                result_date = datetime.strptime(str_date, '%d-%m-%Y %H:%M:%S').date()
            except Exception, e:
                try:
                    str_date = str(date_value) + ' 00:00:00'
                    result_date = datetime.strptime(str_date, '%Y/%m/%d %H:%M:%S').date()
                except Exception, e:
                    try:
                        str_date = str(date_value) + ' 00:00:00'
                        result_date = datetime.strptime(str_date, '%m/%d/%Y %H:%M:%S').date()
                    except Exception, e:
                        try:
                            data_time = str(date_value).split('-')
                            a = data_time[2] + '/' + data_time[1] + '/' + data_time[0] + ' 00:00:00'
                            result_date = datetime.strptime(a, '%Y/%m/%d %H:%M:%S').date()
                        except Exception, e:
                            return None                       
        return result_date
    
    ######### Read data and import to database ##########        
    def import_data(self, cr, uid, ids, context=None):
        hr_employee_obj = self.pool.get('hr.employee')
        hr_attendance_obj = self.pool.get('hr.fingerprint.attendance')
        hr_conf_obj = self.pool.get('hr.holidays.config')
        
        data = self.browse(cr, uid, ids)[0]
        company_id = data.company_id.id
        import_file = data.import_file  
        file_name= data['import_fname'] 
        if file_name.find('.dat') or file_name.find('.DAT') !=-1:           
            lines = base64.decodestring(data['import_file'])
            r = csv.reader(StringIO.StringIO(lines), delimiter=",")
        else:
            if file_name.find('.xls')  !=-1:
                lines = base64.decodestring(import_file)
                wb = open_workbook(file_contents=lines)
                excel_rows = self.get_excel_datas(wb.sheets())    
        all_data=[]
        created_counnt = 0
        updated_count = 0
        skipped_count = 0
        skip_data = []
        print r,"Xls_____________"
        for ln in r:
            if not ln or ln and ln[0] and ln[0][0] in ['', '#']:
                continue

            else:
                if ln and ln[0] and ln[0][0] not in ['#','']:
                    import_vals={}
                    data =ln[0].split('\n')
                    data1=data[0].split('\t')
                    import_vals['initial']=data1[0]
                    import_vals['datetime']=data1[1]
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

                value = {}
                fingerprint = str(int(data['initial'])).strip().encode('utf-8')
                submit_datetime = data['datetime'].strip()
                sub_datetime = submit_datetime.split(' ')
                submit_date=sub_datetime[0]
                submit_time=sub_datetime[1]

                if not fingerprint:
                        print '1'
                        skipped_count = skipped_count + 1
                        continue
                if not submit_date:
                        print '2'
                        skipped_count = skipped_count + 1
                        continue
                employee_ids = hr_employee_obj.search(cr, uid, [('otherid','=',fingerprint)])
                if not employee_ids:
                        print '3'
                        skipped_count = skipped_count + 1

                        loop = 0
                        fp = int(fingerprint)
                        same = True
                        while (loop < len(skip_data)):
                            if (skip_data[loop] == fp):
                                same = False
                                break
                            loop=loop+1
                            
                        if same == True:
                            skip_data.append(fp)
                        continue
                else:
                        employee_id = employee_ids[0]

                submit_date = self.check_date_value(submit_date, 'Date')
                
                value['fingerprint_id'] = fingerprint
                value['employee'] = employee_id
                value['name'] = submit_date
                value['reason'] = None
                print "CHECK>>>",fingerprint,"Employee" , employee_id,"Date" , submit_date
                att_ids = None
                sub_time = 0.0
                if len(submit_time) > 0:
                    sub_time1 = submit_time.split(':')
                    s_hour = sub_time1[0]
                    s_min = sub_time1[1]
                    sub_time = float(s_hour)
                    sub_time = sub_time + float((float(s_min)/60))
                    if  sub_time < 12:
                        value['submit_time'] = sub_time
                        value['action'] = 'sign_in'

                        att_ids_1 = hr_attendance_obj.search(cr, uid, [('fingerprint_id','=',fingerprint),('employee','=',employee_id),('name','=',submit_date),('action','=','sign_in')])
                        if att_ids_1:
                            att_ids = hr_attendance_obj.browse(cr, uid, att_ids_1)
                            print "Import Write>>>",att_ids_1[0]," , ",sub_time
                            att_val = {'fingerprint_id':fingerprint,
                                            'employee':employee_id,
                                            'name':submit_date,
                                            'submit_time': sub_time
                                            }
                            hr_attendance_obj.write(cr, uid, att_ids_1[0], att_val)
                            updated_count += 1
                        else:
                            hr_attendance_obj.create(cr, uid, value, context = context)
                            created_counnt += 1
                    if sub_time > 12:
                        value['submit_time'] = sub_time
                        value['action'] = 'sign_out'
                        att_ids_1 = hr_attendance_obj.search(cr, uid, [('fingerprint_id','=',fingerprint),('employee','=',employee_id),('name','=',submit_date),('action','=','sign_out')])
                        if att_ids_1:
                            att_ids = hr_attendance_obj.browse(cr, uid, att_ids_1)
                            print "Import Write>>>",att_ids_1[0]," , ",sub_time
                            att_val = {'fingerprint_id':fingerprint,
                                            'employee':employee_id,
                                            'name':submit_date,
                                            'submit_time': sub_time
                                            }
                            hr_attendance_obj.write(cr, uid, att_ids_1[0], att_val)
                            updated_count += 1
                        else:
                            hr_attendance_obj.create(cr, uid, value, context = context)
                            created_counnt += 1

                    percent = ((created_counnt + updated_count)*100)/len(all_data)                
                    print '(' + str(percent) + '%)' + str(updated_count + created_counnt) + ' records of total ' + str(len(all_data)) + ' completed'
                
                message = 'Import Success at ' + str(datetime.strptime(datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
                      '%Y-%m-%d %H:%M:%S'))+ '\n' + str(len(all_data))+' records imported' +'\
                      \n' + str(created_counnt) + ' created\n' + str(updated_count) + ' updated' + '\
                      \n' + str(skipped_count) + ' skipped'+ '\
                      \n' + 'Skipped Fingerprint : ' + str(skip_data)
                self.write(cr, uid, ids[0], {'state': 'completed','note': message})             