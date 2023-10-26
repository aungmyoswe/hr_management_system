from datetime import datetime, timedelta
from openerp import api, models, fields
from openerp.exceptions import ValidationError

AVAILABLE_PRIORITIES = [
    ('0', 'Yes'),
    ('1', 'No'),
    ]

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

ANSWER_TYPE = [
    ('1', 'Yes/No'),
    ('2', 'Text')
    ]

class hr_employee(models.Model):

    _inherit = 'hr.employee'
    
    count_number = fields.Integer(compute='_get_count_number')
    
    @api.depends('count_number')
    def _get_count_number(self):
        res = dict.fromkeys(self.ids, 0)
        print res
        for cou_id in self.ids:
            part_id = self.pool['hr.employee'].browse(self.env.cr, self.env.uid, cou_id, context=self.env.context)
            print part_id
            res[cou_id] = self.pool['assessment.record'].search_count(self.env.cr, self.env.uid, [('employee', '=', part_id.id)], context=self.env.context)
            self.count_number = res[cou_id]
        self.count_number = 1
    
class AssessmentRecord(models.Model):
    _name = "assessment.record"
    
    type_id1 = fields.Many2one('assessment.question.type',related = 'question_line1.type_id')
    question_line1 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 1)]) 
    question_line1_1 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 1),('type_answer', '=', 1)]) 
    question_line1_2 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 1),('type_answer', '=', 2)])
    type_id2 = fields.Many2one('assessment.question.type',related = 'question_line2.type_id')
    question_line2 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 2)])
    question_line2_1 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 2),('type_answer', '=', 1)]) 
    question_line2_2 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 2),('type_answer', '=', 2)])
    type_id3 = fields.Many2one('assessment.question.type',related = 'question_line3.type_id')
    question_line3 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 3)]) 
    question_line3_1 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 3),('type_answer', '=', 1)]) 
    question_line3_2 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 3),('type_answer', '=', 2)])
    type_id4 = fields.Many2one('assessment.question.type',related = 'question_line4.type_id')
    question_line4 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 4)]) 
    question_line4_1 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 4),('type_answer', '=', 1)]) 
    question_line4_2 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 4),('type_answer', '=', 2)])
    type_id5 = fields.Many2one('assessment.question.type',related = 'question_line5.type_id')
    question_line5 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 5)])
    question_line5_1 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 5),('type_answer', '=', 1)]) 
    question_line5_2 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 5),('type_answer', '=', 2)])
    type_id6 = fields.Many2one('assessment.question.type',related = 'question_line6.type_id')
    question_line6 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 6)])
    question_line6_1 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 6),('type_answer', '=', 1)]) 
    question_line6_2 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 6),('type_answer', '=', 2)])
    type_id7 = fields.Many2one('assessment.question.type',related = 'question_line7.type_id')
    question_line7 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 7)])
    question_line7_1 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 7),('type_answer', '=', 1)]) 
    question_line7_2 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 7),('type_answer', '=', 2)])
    type_id8 = fields.Many2one('assessment.question.type',related = 'question_line8.type_id')
    question_line8 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 8)])
    question_line8_1 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 8),('type_answer', '=', 1)]) 
    question_line8_2 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 8),('type_answer', '=', 2)])
    type_id9 = fields.Many2one('assessment.question.type',related = 'question_line9.type_id')
    question_line9 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 9)])
    question_line9_1 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 9),('type_answer', '=', 1)]) 
    question_line9_2 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 9),('type_answer', '=', 2)])
    type_id10 = fields.Many2one('assessment.question.type',related = 'question_line10.type_id')
    question_line10 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 10)])
    question_line10_1 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 10),('type_answer', '=', 1)]) 
    question_line10_2 = fields.One2many('assessment.question.line','record_id','Assessment Question',domain=[('type_number', '=', 10),('type_answer', '=', 2)])
    
    desc_1 = fields.Text('Description')
    desc_2 = fields.Text('Description')
    desc_3 = fields.Text('Description')
    desc_4 = fields.Text('Description')
    desc_5 = fields.Text('Description')
    desc_6 = fields.Text('Description')
    desc_7 = fields.Text('Description')
    desc_8 = fields.Text('Description')
    desc_9 = fields.Text('Description')
    desc_10 = fields.Text('Description')
    
    employee = fields.Many2one('hr.employee','Employee', required = True)
    department = fields.Char(related='employee.department_id.name',string='Department')
    job = fields.Char(related='employee.job_id.name',string='Position')
    trial_start = fields.Date(related='employee.trial_date_start',string="Date Start")
    
    trial_end = fields.Date(related='employee.trial_date_end', string="Trial Date End")
    #trial_end = fields.Date(compute = "_compute_trial_date_end",string="Trial Date End",store=True,copy=True)
    assessment_date = fields.Date('Date')
    
    show_question_1 = fields.Boolean('Question 1', compute="_compute_question")
    show_question_1_1 = fields.Boolean('Question 1_1', compute="_compute_question")
    show_question_1_2 = fields.Boolean('Question 1_2', compute="_compute_question")
    show_question_2 = fields.Boolean('Question 2', compute="_compute_question")
    show_question_2_1 = fields.Boolean('Question 2_1', compute="_compute_question")
    show_question_2_2 = fields.Boolean('Question 2_2', compute="_compute_question")
    show_question_3 = fields.Boolean('Question 3', compute="_compute_question")
    show_question_3_1 = fields.Boolean('Question 3_1', compute="_compute_question")
    show_question_3_2 = fields.Boolean('Question 3_2', compute="_compute_question")
    show_question_4 = fields.Boolean('Question 4', compute="_compute_question")
    show_question_4_1 = fields.Boolean('Question 4_1', compute="_compute_question")
    show_question_4_2 = fields.Boolean('Question 4_2', compute="_compute_question")
    show_question_5 = fields.Boolean('Question 5', compute="_compute_question")
    show_question_5_1 = fields.Boolean('Question 5_1', compute="_compute_question")
    show_question_5_2 = fields.Boolean('Question 5_2', compute="_compute_question")
    show_question_6 = fields.Boolean('Question 6', compute="_compute_question")
    show_question_6_1 = fields.Boolean('Question 6_1', compute="_compute_question")
    show_question_6_2 = fields.Boolean('Question 6_2', compute="_compute_question")
    show_question_7 = fields.Boolean('Question 7', compute="_compute_question")
    show_question_7_1 = fields.Boolean('Question 7_1', compute="_compute_question")
    show_question_7_2 = fields.Boolean('Question 7_2', compute="_compute_question")
    show_question_8 = fields.Boolean('Question 8', compute="_compute_question")
    show_question_8_1 = fields.Boolean('Question 8_1', compute="_compute_question")
    show_question_8_2 = fields.Boolean('Question 8_2', compute="_compute_question")
    show_question_9 = fields.Boolean('Question 9', compute="_compute_question")
    show_question_9_1 = fields.Boolean('Question 9_1', compute="_compute_question")
    show_question_9_2 = fields.Boolean('Question 9_2', compute="_compute_question")
    show_question_10 = fields.Boolean('Question 10', compute="_compute_question")
    show_question_10_1 = fields.Boolean('Question 10_1', compute="_compute_question")
    show_question_10_2 = fields.Boolean('Question 10_2', compute="_compute_question")
    
    @api.one
    @api.depends('trial_start')
    def _compute_trial_date_end(self):
        if self.trial_start:
          date_start=datetime.strptime(str(self.trial_start),"%Y-%m-%d")
          self.trial_end=timedelta(days=90)+date_start
          return self.trial_end
          print self.trial_end
          
    def _compute_question(self):
      question_line_obj = self.pool.get('assessment.question.line')
      
      self.show_question_1 = False
      self.show_question_1_1 = False
      self.show_question_1_2 = False
      self.show_question_2 = False
      self.show_question_2_1 = False
      self.show_question_2_2 = False
      self.show_question_3 = False
      self.show_question_3_1 = False
      self.show_question_3_2 = False
      self.show_question_4 = False
      self.show_question_4_1 = False
      self.show_question_4_2 = False
      self.show_question_5 = False
      self.show_question_5_1 = False
      self.show_question_5_2 = False
      self.show_question_6 = False
      self.show_question_6_1 = False
      self.show_question_6_2 = False
      self.show_question_7 = False
      self.show_question_7_1 = False
      self.show_question_7_2 = False
      self.show_question_8 = False
      self.show_question_8_1 = False
      self.show_question_8_2 = False
      self.show_question_9 = False
      self.show_question_9_1 = False
      self.show_question_9_2 = False
      self.show_question_10 = False
      self.show_question_10_1 = False
      self.show_question_10_2 = False
      
      for i in range(1,11):
        question_line_ids = question_line_obj.search(self.env.cr, self.env.uid,[('record_id', '=', self.id),('type_number', '=', i)])
        print question_line_ids
        if question_line_ids and i == 1:
          self.show_question_1 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            print 'question_line_id.type_answer ' + str(question_line_id.type_answer)
            if question_line_id.type_answer == '1':
              self.show_question_1_1 = True
            elif question_line_id.type_answer == '2':
              self.show_question_1_2 = True
        elif question_line_ids and i == 2:
          self.show_question_2 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            print 'question_line_id.type_answer ' + str(question_line_id.type_answer)
            if question_line_id.type_answer == '1':
              self.show_question_2_1 = True
            elif question_line_id.type_answer == '2':
              self.show_question_2_2 = True
        elif question_line_ids and i == 3:
          self.show_question_3 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            print 'question_line_id.type_answer ' + str(question_line_id.type_answer)
            if question_line_id.type_answer == '1':
              self.show_question_3_1 = True
            elif question_line_id.type_answer == '2':
              self.show_question_3_2 = True
        elif question_line_ids and i == 4:
          self.show_question_4 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            print 'question_line_id.type_answer ' + str(question_line_id.type_answer)
            if question_line_id.type_answer == '1':
              self.show_question_4_1 = True
            elif question_line_id.type_answer == '2':
              self.show_question_4_2 = True
        elif question_line_ids and i == 5:
          self.show_question_5 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            print 'question_line_id.type_answer ' + str(question_line_id.type_answer)
            if question_line_id.type_answer == '1':
              self.show_question_5_1 = True
            elif question_line_id.type_answer == '2':
              self.show_question_5_2 = True
        elif question_line_ids and i == 6:
          self.show_question_6 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            print 'question_line_id.type_answer ' + str(question_line_id.type_answer)
            if question_line_id.type_answer == '1':
              self.show_question_6_1 = True
            elif question_line_id.type_answer == '2':
              self.show_question_6_2 = True
        elif question_line_ids and i == 7:
          self.show_question_7 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            print 'question_line_id.type_answer ' + str(question_line_id.type_answer)
            if question_line_id.type_answer == '1':
              self.show_question_7_1 = True
            elif question_line_id.type_answer == '2':
              self.show_question_7_2 = True
        elif question_line_ids and i == 8:
          self.show_question_8 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            print 'question_line_id.type_answer ' + str(question_line_id.type_answer)
            if question_line_id.type_answer == '1':
              self.show_question_8_1 = True
            elif question_line_id.type_answer == '2':
              self.show_question_8_2 = True
        elif question_line_ids and i == 9:
          self.show_question_9 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            print 'question_line_id.type_answer ' + str(question_line_id.type_answer)
            if question_line_id.type_answer == '1':
              self.show_question_9_1 = True
            elif question_line_id.type_answer == '2':
              self.show_question_9_2 = True
        elif question_line_ids and i == 10:
          self.show_question_10 = True
          for i in question_line_ids:
            question_line_id = question_line_obj.browse(self.env.cr, self.env.uid,i)
            print 'question_line_id.type_answer ' + str(question_line_id.type_answer)
            if question_line_id.type_answer == '1':
              self.show_question_10_1 = True
            elif question_line_id.type_answer == '2':
              self.show_question_10_2 = True
      
    def create(self, cr, uid, data, context=None):
        context = dict(context or {})
        print 'Assessment Record Create ----------'
        
        record_id = super(AssessmentRecord, self).create(cr, uid, data, context=context)
        print 'res'
        question_type_obj = self.pool.get('assessment.question.type')
        question_line_obj = self.pool.get('assessment.question.line')
        
        q_type_ids = question_type_obj.search(cr,uid,[('q_active', '=', True)])
        print 'q_type'
        print data
        print record_id
        print 'active'
        print q_type_ids
        q_type_line_ids = question_type_obj.browse(cr,uid,q_type_ids)
        print q_type_line_ids
          
        for q_type_id in q_type_line_ids:
            for question_ids in q_type_id.question_ids:
              print question_ids.id
              record_line_value = {
                                   'question_id':question_ids.id,
                                   'employee_id':data['employee'],
                                   'record_id':record_id, 
                                   'type_id':q_type_id.id,
                                   'type_number':q_type_id.number,
                                   'type_answer':question_ids.type_answer,
                                   }
              print 'here '
              print record_line_value
              question_line_id = question_line_obj.create(cr, uid, record_line_value, context)   
              print question_line_id
              
        return record_id
      
    def write(self, cr, uid, ids,data, context=None):
        print 'Assessment Record Write ----------'
        context = dict(context or {})
        flag = super(AssessmentRecord, self).write(cr, uid, ids,data, context=context)
        print flag
        print context
        print data
        for question_line in data:
          print question_line
          for question in data.get(question_line):
            print question
            if len(question) >= 2:
              print question[1]
              question_line_obj = self.pool['assessment.question.line'].browse(cr, uid, question[1], context=context)
              print 'question_line_obj.question_id ' + str(question_line_obj.question_id)
              print 'question_line_obj.employee_id ' + str(question_line_obj.employee_id)
              question_obj = self.pool['assessment.question'].browse(cr, uid, question_line_obj.question_id.id, context=context)
              print question_obj.is_permanent
              print question_line_obj.employee_id.trial_date_start
              if question_line_obj.employee_id.trial_date_start:
                trial_date_start=datetime.strptime(str(question_line_obj.employee_id.trial_date_start),"%Y-%m-%d")
              else:
                raise ValidationError(question_line_obj.employee_id.name + ' Joining Date Does Not Exit ! ')
              permanent_date = trial_date_start + timedelta(days=90)
              print permanent_date
              if question_obj.is_permanent:
                print question[2]
                contract_id = self.pool['hr.contract'].search(cr, uid, [('employee_id','=', question_line_obj.employee_id.id)], context=context)
                print contract_id
                if question[2] and 'priority' in question[2]:
                  if question[2].get('priority') == '0':
                    print 'WORK'
                    c_id = self.pool['hr.contract'].browse(cr, uid, contract_id, context=context).write({'is_permanent':True,'permanent_date':permanent_date}) 
                    print c_id
                    print 'PASS'
                    
                  elif question[2].get('priority') == '1':
                    c_id = self.pool['hr.contract'].browse(cr, uid, contract_id, context=context).write({'is_permanent':False})
                    print c_id
                    print 'FAIL'
                  else:
                    print 'not permanent'
                else:
                  print 'question 2 False'
                  
        return flag             
              
    @api.multi
    def unlink(self):
        record = self.pool.get('assessment.record').browse(self.env.cr,self.env.uid,self.ids)
        question_line_obj = self.pool.get('assessment.question.line')
        print record         
    
        for rec in record:
          records = question_line_obj.search(self.env.cr,self.env.uid,[('record_id', '=', rec.id)])
          records = question_line_obj.browse(self.env.cr,self.env.uid,records)
          print records
        
          for record_line_ids in records:
              print record_line_ids
              record_line_id = question_line_obj.unlink(self.env.cr,self.env.uid, record_line_ids.id)   
              print 'unlink question lines ...'
              print record_line_id

        return models.Model.unlink(self)

class AssessmentQuestion(models.Model):
    _name = 'assessment.question'
    name = fields.Char('Question', required = True)
    type_answer = fields.Selection(ANSWER_TYPE, "Answer Type")
    is_permanent = fields.Boolean('Is Permanent')
    
class AssessmentQuestionLine(models.Model):
    _name = 'assessment.question.line'
    
    question_id = fields.Many2one('assessment.question','Question')
    type_id = fields.Many2one('assessment.question.type', store = True)
    type_number = fields.Char('Question Type Number')
    type_answer = fields.Selection(ANSWER_TYPE, "Answer Type")
    priority = fields.Selection(AVAILABLE_PRIORITIES, "Appreciation", default='1')
    text = fields.Text("Text")
    record_id = fields.Many2one('assessment.record','Assessment Records')
    employee_id = fields.Many2one('hr.employee',string='Employees')
        
class AssessmentQuestionType(models.Model):
    _name = 'assessment.question.type'
    number = fields.Selection(QUESTION_NUMBER, "Question No.", default='1')
    name = fields.Char('Question Type', required=True)
    q_active = fields.Boolean('Question Active')
    question_ids = fields.Many2many(
                               'assessment.question', # related model
                               'assessment_question_and_type_rel',  # relation table name
                               'type_id', # field for "this" record
                               'question_id', # field for "other" record
                               string='Question')
    
    @api.one
    @api.constrains('number')
    def _check_record_employee(self):
        records = self.env['assessment.question.type'].search([('number','=',self.number)])  
        if len(records) >= 2:
            raise ValidationError('Question ' + self.number + ' is already Have !')


    # If Delete Instead Warning
    @api.multi
    def unlink(self):
        q_types = self.pool.get('assessment.question.type').browse(self.env.cr,self.env.uid,self.ids)
        question_line_obj = self.pool.get('assessment.question.line')

        print q_types

        q_types_id = q_types.id
        records_2 = question_line_obj.search(self.env.cr,self.env.uid,[('type_id', '=', q_types_id)])
        print 'record_2'
        print records_2
        
        if records_2:
          raise ValidationError('This Questions Type are already Used !')
        else:
          return models.Model.unlink(self)

#         for q_types_ids in records_2:
#             print q_types_ids
#             q_line_id = question_line_obj.unlink(self.env.cr,self.env.uid, q_types_ids.id)
#             print 'unlink question lines with question type ...'
#             print q_line_id
         


    
    



