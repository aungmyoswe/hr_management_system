from openerp import fields, models, api
from datetime import datetime
from datetime import timedelta

class DutyRosterLine(models.Model):
  
    _inherit = "hr.employee.duty.roster.line"
    
    show_color_1 = fields.Char('Color', compute="_compute_color")
    show_color_2 = fields.Char('Color', compute="_compute_color")
    show_color_3 = fields.Char('Color', compute="_compute_color")
    show_color_4 = fields.Char('Color', compute="_compute_color")
    show_color_5 = fields.Char('Color', compute="_compute_color")
    show_color_6 = fields.Char('Color', compute="_compute_color")
    show_color_7 = fields.Char('Color', compute="_compute_color")  
    show_color_8 = fields.Char('Color', compute="_compute_color")
    show_color_9 = fields.Char('Color', compute="_compute_color")
    show_color_10 = fields.Char('Color', compute="_compute_color")
    show_color_11 = fields.Char('Color', compute="_compute_color")
    show_color_12 = fields.Char('Color', compute="_compute_color")
    show_color_13 = fields.Char('Color', compute="_compute_color")
    show_color_14 = fields.Char('Color', compute="_compute_color")
    show_color_15 = fields.Char('Color', compute="_compute_color")  
    show_color_16 = fields.Char('Color', compute="_compute_color")
    show_color_17 = fields.Char('Color', compute="_compute_color")
    show_color_18 = fields.Char('Color', compute="_compute_color")
    show_color_19 = fields.Char('Color', compute="_compute_color")
    show_color_20 = fields.Char('Color', compute="_compute_color")
    show_color_21 = fields.Char('Color', compute="_compute_color")
    show_color_22 = fields.Char('Color', compute="_compute_color")
    show_color_23 = fields.Char('Color', compute="_compute_color")  
    show_color_24 = fields.Char('Color', compute="_compute_color")
    show_color_25 = fields.Char('Color', compute="_compute_color")
    show_color_26 = fields.Char('Color', compute="_compute_color")
    show_color_27 = fields.Char('Color', compute="_compute_color")
    show_color_28 = fields.Char('Color', compute="_compute_color")
    show_color_29 = fields.Char('Color', compute="_compute_color")
    show_color_30 = fields.Char('Color', compute="_compute_color")
    show_color_31 = fields.Char('Color', compute="_compute_color")
    
    @api.one
    def _compute_color(self):
      if self.date_from and self.date_to:
            date_format = "%Y-%m-%d"
            date_start = datetime.strptime(self.date_from,date_format)
            date_end = datetime.strptime(self.date_to,date_format)
            for i in range(1,32):
                str_shift = 'shift_id_' + str(date_start.day)
                
                if(date_start > date_end):
                    break            
                
                if str_shift == 'shift_id_1':
                    self.show_color_1 = date_start.strftime("%A")
                elif str_shift == 'shift_id_2':
                    self.show_color_2 = date_start.strftime("%A")
                elif str_shift == 'shift_id_3':
                    self.show_color_3 = date_start.strftime("%A")
                elif str_shift == 'shift_id_4':
                    self.show_color_4 = date_start.strftime("%A")
                elif str_shift == 'shift_id_5':
                    self.show_color_5 = date_start.strftime("%A")
                elif str_shift == 'shift_id_6':
                    self.show_color_6 = date_start.strftime("%A")
                elif str_shift == 'shift_id_7':
                    self.show_color_7 = date_start.strftime("%A")
                elif str_shift == 'shift_id_8':
                    self.show_color_8 = date_start.strftime("%A")
                elif str_shift == 'shift_id_9':
                    self.show_color_9 = date_start.strftime("%A")
                elif str_shift == 'shift_id_10':
                    self.show_color_10 = date_start.strftime("%A")
                elif str_shift == 'shift_id_11':
                    self.show_color_11 = date_start.strftime("%A")
                elif str_shift == 'shift_id_12':
                    self.show_color_12 = date_start.strftime("%A")
                elif str_shift == 'shift_id_13':
                    self.show_color_13 = date_start.strftime("%A")
                elif str_shift == 'shift_id_14':
                    self.show_color_14 = date_start.strftime("%A")
                elif str_shift == 'shift_id_15':
                    self.show_color_15 = date_start.strftime("%A")
                elif str_shift == 'shift_id_16':
                    self.show_color_16 = date_start.strftime("%A")
                elif str_shift == 'shift_id_17':
                    self.show_color_17 = date_start.strftime("%A")
                elif str_shift == 'shift_id_18':
                    self.show_color_18 = date_start.strftime("%A")
                elif str_shift == 'shift_id_19':
                    self.show_color_19 = date_start.strftime("%A")
                elif str_shift == 'shift_id_20':
                    self.show_color_20 = date_start.strftime("%A")
                elif str_shift == 'shift_id_21':
                    self.show_color_21 = date_start.strftime("%A")
                elif str_shift == 'shift_id_22':
                    self.show_color_22 = date_start.strftime("%A")
                elif str_shift == 'shift_id_23':
                    self.show_color_23 = date_start.strftime("%A")
                elif str_shift == 'shift_id_24':
                    self.show_color_24 = date_start.strftime("%A")
                elif str_shift == 'shift_id_25':
                    self.show_color_25 = date_start.strftime("%A")
                elif str_shift == 'shift_id_26':
                    self.show_color_26 = date_start.strftime("%A")
                elif str_shift == 'shift_id_27':
                    self.show_color_27 = date_start.strftime("%A") 
                elif str_shift == 'shift_id_28':
                    self.show_color_28 = date_start.strftime("%A")
                elif str_shift == 'shift_id_29':
                    self.show_color_29 = date_start.strftime("%A")
                elif str_shift == 'shift_id_30':
                    self.show_color_30 = date_start.strftime("%A")
                elif str_shift == 'shift_id_31':
                    self.show_color_31 = date_start.strftime("%A")
                    
                date_start = date_start + timedelta(days=1)
