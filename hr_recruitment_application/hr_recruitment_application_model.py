from openerp import models, fields,api
from openerp.exceptions import ValidationError
from openerp.modules.module import get_module_resource
from openerp import tools
from datetime import datetime, timedelta


class hr_applicant(models.Model):
    _name = "hr.applicant"
    _inherit = 'hr.applicant'

    name = fields.Char('Job Title (Department)', required=True)
    date_deadline = fields.Date('Date')
    age = fields.Integer('Age')
    partner_name = fields.Char('Applicant\'s Name')
    partner_burmese_name = fields.Char('Applicant\'s Name')
    street = fields.Char('Street')
    township = fields.Many2one('res.partner.township','Address')
    address = fields.Char('Address')
    nrc_number=fields.Char('NRC No')
    
    working_experience = fields.One2many('working_experience.task', 'experience_parent')
    interview_status = fields.Selection(string=' ',selection=[('interview_have', 'Yes'), ('interview_no_have', 'No')],default='interview_have')
    
    #interviewer = fields.One2many('interviewer.task', 'interviewer_parent')
    nod_note = fields.Text(' ')
    team_motivate = fields.Char(' ')
    working_environment = fields.Char(' ')
    hod_presentation = fields.Text(' ')
    recommentation_from_hr = fields.Text(' ')
    
    background_check_report = fields.One2many('background_check_report.task', 'background_check_report_parent')
    
    interview_result = fields.Selection(string=' ',selection=[('interview_result_yes', 'Yes'), ('interview_result_no', 'No')])
    medicine_check = fields.Selection(string=' ',selection=[('medicine_check_yes', 'Yes'), ('medicine_check_no', 'No'),('medicine_check_wait', 'Wait')])
    permit_company_name = fields.Selection(string=' ',selection=[('ccc', 'CCC'), ('ytci', 'YTCI'),('cci', 'CCI'),('zarla', 'ZARLA'),('parama', 'PARAMA')])
    #final_interviewer = fields.One2many('interviewer.task','interviewer_parent')
    
    first_interviewer_name = fields.Char(' ')
    first_interviewer_sign = fields.Binary(string='Signature')
    second_interviewer_name = fields.Char(' ')
    second_interviewer_sign = fields.Binary(string='Signature')

    #first_date = fields.Date(compute='_previous_interview_date',string='Previous Interview Date')
    first_date = fields.Date('First Interview Date')
    inv_status = fields.Boolean('Reject')
    second_date = fields.Date('Second Interview Date')
    #final_date = fields.Date('Final Interview Date')
    bg_check_date = fields.Date('Background Check Date')
    medical_check_date = fields.Date('Medical Check Date')
    job_offer_date = fields.Date('Job Offer Date')
    acceptence_date = fields.Date('Acceptence Date')
    reject_date = fields.Date('Reject Date')
    
    type_id1 = fields.Many2one('application.question.type',related = 'question_line1_1.type_id')
    question_line1_1 = fields.One2many('application.question.line','record_id','Applications Question',domain=[('type_number', '=', 1)]) 
    type_id2 = fields.Many2one('application.question.type',related = 'question_line2_1.type_id')
    question_line2_1 = fields.One2many('application.question.line','record_id','Applications Question',domain=[('type_number', '=', 2)]) 
    type_id3 = fields.Many2one('application.question.type',related = 'question_line3_1.type_id')
    question_line3_1 = fields.One2many('application.question.line','record_id','Applications Question',domain=[('type_number', '=', 3)]) 
    type_id4 = fields.Many2one('application.question.type',related = 'question_line4_1.type_id')
    question_line4_1 = fields.One2many('application.question.line','record_id','Applications Question',domain=[('type_number', '=', 4)]) 
    
    type_id5 = fields.Many2one('application.question.type',related = 'question_line1_1.type_id')
    question_line5_1 = fields.One2many('application.question.line','record_id','Applications Question',domain=[('type_number', '=', 5)]) 
    type_id6 = fields.Many2one('application.question.type',related = 'question_line2_1.type_id')
    question_line6_1 = fields.One2many('application.question.line','record_id','Applications Question',domain=[('type_number', '=', 6)]) 
    type_id7 = fields.Many2one('application.question.type',related = 'question_line3_1.type_id')
    question_line7_1 = fields.One2many('application.question.line','record_id','Applications Question',domain=[('type_number', '=', 7)]) 
    type_id8 = fields.Many2one('application.question.type',related = 'question_line4_1.type_id')
    question_line8_1 = fields.One2many('application.question.line','record_id','Application Question',domain=[('type_number', '=', 8)]) 
    type_id9 = fields.Many2one('application.question.type',related = 'question_line4_1.type_id')
    question_line9_1 = fields.One2many('application.question.line','record_id','Applications Question',domain=[('type_number', '=', 9)]) 
    type_id10 = fields.Many2one('application.question.type',related = 'question_line4_1.type_id')
    question_line10_1 = fields.One2many('application.question.line','record_id','Applications Question',domain=[('type_number', '=', 10)]) 
    
    show_question_1 = fields.Boolean('Question 1', compute="_compute_question")
    show_question_1_1 = fields.Boolean('Question 1_1', compute="_compute_question")
    show_question_2 = fields.Boolean('Question 2', compute="_compute_question")
    show_question_2_1 = fields.Boolean('Question 2_1', compute="_compute_question")
    show_question_3 = fields.Boolean('Question 3', compute="_compute_question")
    show_question_3_1 = fields.Boolean('Question 3_1', compute="_compute_question")
    show_question_4 = fields.Boolean('Question 4', compute="_compute_question")
    show_question_4_1 = fields.Boolean('Question 4_1', compute="_compute_question")

    show_question_5 = fields.Boolean('Question 5', compute="_compute_question")
    show_question_5_1 = fields.Boolean('Question 5_1', compute="_compute_question")
    show_question_6 = fields.Boolean('Question 6', compute="_compute_question")
    show_question_6_1 = fields.Boolean('Question 6_1', compute="_compute_question")
    show_question_7 = fields.Boolean('Question 7', compute="_compute_question")
    show_question_7_1 = fields.Boolean('Question 7_1', compute="_compute_question")
    show_question_8 = fields.Boolean('Question 8', compute="_compute_question")
    show_question_8_1 = fields.Boolean('Question 8_1', compute="_compute_question")
    show_question_9 = fields.Boolean('Question 9', compute="_compute_question")
    show_question_9_1 = fields.Boolean('Question 9_1', compute="_compute_question")
    show_question_10 = fields.Boolean('Question 10', compute="_compute_question")
    show_question_10_1 = fields.Boolean('Question 10_1', compute="_compute_question")
    
    def _compute_question(self):
      question_line_obj = self.pool.get('application.question.line')
      
      self.show_question_1 = False
      self.show_question_1_1 = False
      self.show_question_2 = False
      self.show_question_2_1 = False
      self.show_question_3 = False
      self.show_question_3_1 = False
      self.show_question_4 = False
      self.show_question_4_1 = False
      self.show_question_5 = False
      self.show_question_5_1 = False
      self.show_question_6 = False
      self.show_question_6_1 = False
      self.show_question_7 = False
      self.show_question_7_1 = False
      self.show_question_8 = False
      self.show_question_8_1 = False
      self.show_question_9 = False
      self.show_question_9_1 = False
      self.show_question_10 = False
      self.show_question_10_1 = False
      
      for i in range(1,11):
        question_line_ids = question_line_obj.search(self.env.cr, self.env.uid,[('record_id', '=', self.id),('type_number', '=', i)])
        print question_line_ids
        if question_line_ids and i == 1:
          self.show_question_1 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            if question_line_id.type_number == '1':
              self.show_question_1_1 = True
        elif question_line_ids and i == 2:
          self.show_question_2 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            if question_line_id.type_number == '2':
              self.show_question_2_1 = True
        elif question_line_ids and i == 3:
          self.show_question_3 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            if question_line_id.type_number == '3':
              self.show_question_3_1 = True
        elif question_line_ids and i == 4:
          self.show_question_4 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            if question_line_id.type_number == '4':
              self.show_question_4_1 = True
        elif question_line_ids and i == 5:
          self.show_question_5 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            if question_line_id.type_number == '5':
              self.show_question_5_1 = True
        elif question_line_ids and i == 6:
          self.show_question_6 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            if question_line_id.type_number == '6':
              self.show_question_6_1 = True
        elif question_line_ids and i == 7:
          self.show_question_7 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            if question_line_id.type_number == '7':
              self.show_question_7_1 = True
        elif question_line_ids and i == 8:
          self.show_question_8 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            if question_line_id.type_number == '8':
              self.show_question_8_1 = True
        elif question_line_ids and i == 9:
          self.show_question_9 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            if question_line_id.type_number == '9':
              self.show_question_9_1 = True
        elif question_line_ids and i == 10:
          self.show_question_10 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            if question_line_id.type_number == '10':
              self.show_question_10_1 = True

    
    def create(self, cr, uid, data, context=None):
        context = dict(context or {})
        print 'Application Record Create ----------'
        if data.get('first_date'):
          data.update({'stage_id': 2})
        elif data.get('inv_status'):
          data.update({'stage_id': 6})
        record_id = super(hr_applicant, self).create(cr, uid, data, context=context)
        print 'res'
        question_type_obj = self.pool.get('application.question.type')
        question_line_obj = self.pool.get('application.question.line')
        
        q_type_ids = question_type_obj.search(cr,uid,[('q_active', '=', True)])
        q_type_line_ids = question_type_obj.browse(cr,uid,q_type_ids)
          
        for q_type_id in q_type_line_ids:
            for question_ids in q_type_id.question_ids:
              record_line_value = {
                                   'question_id':question_ids.id,
                                   'record_id':record_id, 
                                   'type_id':q_type_id.id,
                                   'type_number':q_type_id.number,
                                   }
              question_line_id = question_line_obj.create(cr, uid, record_line_value, context) 
        return record_id
    
    def write(self, cr, uid, ids, vals, context=None):
      print 'vals ' + str(vals)
      stage_obj = self.pool.get('hr.recruitment.stage')
      if 'name' in vals:
        for record_ids in super(hr_applicant, self).browse(cr,uid,ids,vals):
          print '<<< record_ids ' + str(record_ids)
          sequence = record_ids.stage_id.sequence
          last_stage_id = record_ids.last_stage_id
          print sequence
          
        next_sequence = sequence + 1
        print 'next sequence ' + str(next_sequence) 
        stage_id = stage_obj.search(cr,uid,[('sequence', '=', next_sequence)])
        vals.update({'stage_id': stage_id[0]})

      print vals

      res_id = super(hr_applicant, self).write(cr, uid, ids, vals, context=context)
      print res_id
      return res_id

    @api.one
    @api.constrains('nrc_number')
    def _check_record_nrc_number(self):
        hr_employee_obj=self.pool.get('hr.employee')
        if self.nrc_number:
          records = hr_employee_obj.search(self.env.cr, self.env.uid ,[('identification_id','=',self.nrc_number)])                                   
          if records:
              raise ValidationError('Employee NRC No ' + self.nrc_number + ' Already Exist !' )
    
class experience(models.Model):
    _name='working_experience.task'
    company_name = fields.Char(' ')
    worked_post = fields.Char(' ')
    worked_duringtime= fields.Date(' ')
    leave_information = fields.Char(' ')
    experience_parent = fields.Many2one('hr.applicant')
    
class background_check_report(models.Model):
    _name ='background_check_report.task'
    bg_company_name = fields.Char(' ')
    bg_check_report = fields.Char(' ')
    bg_note = fields.Date(' ')
    background_check_report_parent = fields.Many2one('hr.applicant')

#Start 20/01/2018 KKW
QUESTION_NUMBER = [
    ('1', 'Question (1)'),
    ('2', 'Question (2)'),
    ('3', 'Question (3)'),
    ('4', 'Question (4)'),
    ('5', 'Question (5)'),
    ('6', 'Question (6)'),
    ('7', 'Question (7)'),
    ('8', 'Question (8)'),
    ('9', 'Question (9)'),
    ('10', 'Question (10)')
    ]
class HrApplicationQuestion(models.Model):
    _name = "application.question"
    name = fields.Char('Question', required = True)
    
class HrApplicationQuestionLine(models.Model):
    _name = 'application.question.line'
    
    question_id = fields.Many2one('application.question','Question')
    type_id = fields.Many2one('application.question.type', store = True)
    type_number = fields.Char('Question Type Number')
    note_id = fields.Char('Note')
    record_id = fields.Many2one('hr.applicant','Applications Records')
    answer = fields.Char('Answers')

    

class HrApplicationQuestionType(models.Model):
    _name = 'application.question.type'
    name = fields.Char('Question Type', required=True)
    number = fields.Selection(QUESTION_NUMBER, "Question No.", default='1')
    q_active = fields.Boolean('Question Active')
    question_ids = fields.Many2many(
                               'application.question', # related model
                               'application_question_and_type_rel',  # relation table name
                               'question_id', 
                               'type_id',# field for "other" record
                               string='Question')


    

    



    
