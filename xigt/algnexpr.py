import re

algnexpr_re = re.compile(r'(([a-zA-Z][\-.\w]*)(\[[^\]]*\])?|\+|,)')
selection_re = re.compile(r'(-?\d+:-?\d+|\+|,)')
class AlignmentExpression(object):
    plus_delimiter  = ''
    comma_delimiter = ' '

    def __init__(self, expr, tier):
        self.expr = expr
        self.alignments = algnexpr_re.findall(self.expr)
        self.tier = tier

    def resolve(self,
                plus_delimiter=plus_delimiter,
                comma_delimiter=comma_delimiter):
        parts = [plus_delimiter if match == '+' else
                 comma_delimiter if match == ',' else
                 self.resolve_alignment(item_id, selection)
                 for match, item_id, selection in self.alignments]
        return ''.join(parts)

    def resolve_alignment(self, item_id, selection,
                          plus_delimiter=plus_delimiter,
                          comma_delimiter=comma_delimiter):
        item = self.tier[item_id]
        if selection == '':
            return item.content
        spans = selection_re.findall(selection)
        parts = [plus_delimiter if match == '+' else
                 comma_delimiter if match == ',' else
                 item.span(*map(int, match.split(':')))
                 for match in spans]
        return ''.join(parts)
