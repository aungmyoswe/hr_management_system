from openerp import models, fields

class hr_job(models.Model):
    _inherit = 'hr.job'
    
    def _auto_init(self, cr, context=None):
      print 'CONSTRAINT WORK'
      result = super(hr_job, self)._auto_init(cr, context=context)
      # This SQL Only Need First Time Install When Next Time Upgrade Should Remove
      # ALTER TABLE "hr_job" DROP CONSTRAINT "hr_job_name_company_uniq";
      cr.execute("""
       ALTER TABLE "hr_job" ADD CONSTRAINT "hr_job_name_company_uniq" unique (name, department_id, section_id,sub_section_id);
      """)
      return result
