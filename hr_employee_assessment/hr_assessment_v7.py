from openerp import fields, models, api

class AssessmentQuestionLine(models.Model):
    _name = 'assessment.question.line'

    def _get_location_change(self, cr, uid, ids, context=None):
        return self.pool.get('stock.inventory.line').search(cr, uid, [('location_id', 'in', ids)], context=context)
