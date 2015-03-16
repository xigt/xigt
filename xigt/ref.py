
import re
from collections import namedtuple


def span(item, idx1, idx2):
    val = item.value()
    if val is None:
        return None
    return val[idx1:idx2]

def targets(ids, igt):
    pass

def get_aligned_tier(tier, algnattr):
    tgt_tier_id = tier.get_attribute(algnattr)
    if tgt_tier_id is None:
        raise XigtAttributeError(
            'Tier {} does not specify an alignment "{}".'
            .format(tgt_tier_id, algnattr)
        )
    tgt_tier = tier.igt.get(tgt_tier_id)
    return tgt_tier

### Alignment Expressions ####################################################

# Module variables
id_re = re.compile(r'[a-zA-Z][-.\w]*')
reflist_re = re.compile(r'^\s*([a-zA-Z][-.\w]*)(\s+[a-zA-Z][-.\w]*)*\s*$')
algnexpr_re = re.compile(r'(([a-zA-Z][\-.\w]*)(\[[^\]]*\])?|\+|,)')
selection_re = re.compile(r'(-?\d+:-?\d+|\+|,)')

delimiters = {
    ',': ' ',
    '+': ''
}

delim1 = ''
delim2 = ' '


def ids(expression):
    alignments = algnexpr_re.findall(expression or '')
    return [item_id for _, item_id, _ in alignments if item_id]


def selections(expression):
    pass

def spans(expression):
    pass


def resolve(expression, container):
    itemgetter = getattr(container, 'get_item', container.get)
    return ''.join(
        '{}{}'.format(
            delimiters.get(delim, ''),
            itemgetter(item_id)
    )


def _enumerate_spans(expression, container):
    

# deprecated methods

def get_aligment_expression_ids(expression):
    return ids(expression)

def get_alignment_expression_spans(expression):
    alignments = algnexpr_re.findall(expression or '')
    spans = list(chain.from_iterable(
        [match] if not item_id else
        [item_id] if not selection else
        [selmatch if ':' not in selmatch else
         tuple([item_id] + list(map(int, selmatch.split(':'))))
         for selmatch in selection_re.findall(selection)
        ]
        for match, item_id, selection in alignments
    ))
    return spans


def resolve_alignment_expression(expression, tier, plus=delim1, comma=delim2):
    alignments = algnexpr_re.findall(expression)
    parts = [plus if match == '+' else
             comma if match == ',' else
             resolve_alignment(tier, item_id, selection)
             for match, item_id, selection in alignments]
    return ''.join(parts)


def resolve_alignment(tier, item_id, selection, plus=delim1, comma=delim2):
    item = tier.get(item_id)
    if item is None:
        warnings.warn(
            'Item "{}" not found in tier "{}"'.format(item_id, tier.id),
            XigtWarning
        )
        return ''
    else:
        if selection == '':
            return item.get_content()
        spans = selection_re.findall(selection)
        parts = [plus if match == '+' else
                 comma if match == ',' else
                 item.span(*map(int, match.split(':')))
                 for match in spans]
        return ''.join(parts)
