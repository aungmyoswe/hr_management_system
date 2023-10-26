from openerp import fields, models,api

class hr_payappl_wizard(models.TransientModel):
    _name = 'hr.schedule.wizard'
    
    schedule_ids = fields.Many2many('hr.applicant', string="Schedules")
    
    _defaults = {
        'schedule_ids' : lambda self, cr, uid, context: context.get('schedule_ids',False),
        }

    @api.multi
    def schedule_popup(self):
      
      partner_obj = self.pool.get('res.partner')
      applicant_obj = self.pool.get('hr.applicant')

      for rec in self:
            s_ids = []
            for appl in rec.schedule_ids:
                value = {}
                value1 = {}
                if not appl.partner_id.id:
                  #create partner by name
                  value['name'] = appl.partner_name
                  new_partner_id = partner_obj.create(self.env.cr, self.env.uid, value)
                  #print " Partner Id: " + str(new_partner_id) + " Create ..."
                  
                  value1['partner_id'] = new_partner_id
                  applicant_obj.write(self.env.cr, self.env.uid, appl.id, value1)
                  #print  " Name : " + appl.partner_name + " Update ..."
                  
                  s_ids.append(new_partner_id)
                else:
                  s_ids.append(appl.partner_id.id)
            #print s_ids
            #if s_ids:
            #    print 'work' + str(s_ids)
                
      view = {
        'type': 'ir.actions.act_window',
        'name': 'Schedules',
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'calendar.event',
        'view_id': False,
        'target': 'new',
        'flags': {'form': {'action_buttons': True}},
        'context':{'default_partner_ids':[schedule for schedule in s_ids]}
        }
      
      return view
    
# class Calendar(models.Model):    
# 
#     _inherit = 'calendar.event'
#     
#     @api.model
#     def create(self, vals):
#         #print 'Save Work'
#         #print str(vals['partner_ids'])
#         #print '--------------'
#         
#         if type(vals['partner_ids'][0]) is list:
#           print str(vals['partner_ids'][0][2])
#            
#           for partners in vals['partner_ids'][0][2]:
#             value = {}
#             applicant_obj = self.pool.get('hr.applicant')
#           
#             value['date_action'] = str(vals['stop_datetime'])
#             value['title_action'] = str(vals['name'])
#             applicant_id = applicant_obj.search(self.env.cr, self.env.uid, [('partner_id', '=', partners)])
#             applicant_obj.write(self.env.cr, self.env.uid, applicant_id, value)
#             #print  " ID : " + str(applicant_id) + " / " + str(vals['stop_datetime']) + " / " + str(vals['name']) + " Update ..."
# 
#         elif type(vals['partner_ids'][0]) is tuple:
#           print 'a tuple'
#         else:
#           print 'neither a tuple or a list'
#         
#         rec = super(Calendar, self).create(vals)
#         return rec
                
    
