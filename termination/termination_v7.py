from openerp.osv import fields, osv
    
class TerminationLine(osv.osv):
    _inherit = 'termination.line'
    
    def employee_change(self,cr,uid,ids,employee_id,context=None):
        employee_obj = self.pool.get('hr.employee')
        print '-----------'
        department_id = job_id = section_id = None
        if employee_id:
          print employee_id
          job_obj = employee_obj.browse(cr,uid,employee_id).job_id
          department_id = job_obj.department_id.id
          section_id = job_obj.section_id.id
          job_id = job_obj.id
        return {'value': {'department': department_id,'job': job_id,'section': section_id}}
      
# class TerminationDistribute(osv.osv):
#     _inherit = 'termination.distribute'
#     
#     def employee_change(self,cr,uid,ids,employee_id,context=None):
#         employee_obj = self.pool.get('hr.employee')
#         print '-----------'
#         department_id = job_id = None
#         if employee_id:
#           print employee_id
#           job_obj = employee_obj.browse(cr,uid,employee_id).job_id
#           department_id = job_obj.department_id.id
#           job_id = job_obj.id
#         return {'value': {'department': department_id,'job': job_id}}
       
    
