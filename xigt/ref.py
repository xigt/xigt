
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

Span = namedtuple('Span', ('delimiter', 'id', 'start', 'end'))
Selection = namedtuple('Selection', ('id', 'spans'))

# Module variables
id_re = re.compile(r'[a-zA-Z][-.\w]*')
reflist_re = re.compile(r'^\s*([a-zA-Z][-.\w]*)(\s+[a-zA-Z][-.\w]*)*\s*$')
algnexpr_re = re.compile(r'(([a-zA-Z][\-.\w]*)(\[[^\]]*\])?|\+|,)')
selection_re = re.compile(r'(-?\d+:-?\d+|\+|,)')
span_re = re.compile(r'([^-.:\d])?(-?[.\d]+):(-?[.\d]+)')
robust_ref_re = re.compile(
    r'(^|.+?)'  # anything not an id (maybe space, maybe a delimiter)
    r'($|[a-zA-Z][\-.\w]*)'  # id
    r'(?:$|\[((?:[^-.:\d]?-?[.\d]+:-?[.\d]+)+)\])?'  # range
)

delimiters = {
    ',': ' ',
    '+': ''
}

delim1 = ''
delim2 = ' '


# string-only operations

def expand(expression):
    """
    Expand a reference expression to individual spans.
    Also works on space-separated ID lists, although the space character
    will be considered a delimiter.

    >>> expand('a1')
    'a1'
    >>> expand('a1[3:5]')
    'a1[3:5]'
    >>> expand('a1[3:5+6:7]')
    'a1[3:5]+a1[6:7]'
    >>> expand('a1 a2  a3')
    'a1 a2  a3'

    """
    tokens = []
    for (pre, _id, _range) in robust_ref_re.findall(expression):
        if not _range:
            tokens.append('{}{}'.format(pre, _id))
        else:
            tokens.append(pre)
            tokens.extend(
                '{}{}[{}:{}]'.format(delim, _id, start, end)
                for delim, start, end in span_re.findall(_range)
            )
    return ''.join(tokens)


def compress(expression):
    """
    Compress a reference expression to group spans on the same id.
    Also works on space-separated ID lists, although the space character
    will be considered a delimiter.

    >>> compress('a1')
    'a1'
    >>> compress('a1[3:5]')
    'a1[3:5]'
    >>> compress('a1[3:5+6:7]')
    'a1[3:5+6:7]'
    >>> compress('a1[3:5]+a1[6:7]')
    'a1[3:5+6:7]'
    >>> compress('a1 a2  a3')
    'a1 a2  a3'

    """
    tokens = []
    selection = []
    last_id = None
    for (pre, _id, _range) in robust_ref_re.findall(expression):
        if not _id:
            tokens.append(pre)
        elif _range and _id == last_id:
            selection.extend('{}{}'.format(pre, _range))
        else:
            tokens.append(''.join(selection + [']']))
            tokens.append(pre)
            selection = ['{}[{}'.format(_id, _range)]
            last_id = _id
    tokens.append(''.join(selection))
    return ''.join(tokens)



def selection_split(expression, keep_delimiters=True):
    """
    Split the expression into individual selection expressions. The
    delimiters will be kept as separate items if keep_delimters=True.
    Also works on space-separated ID lists, although the space character
    will be considered a delimiter.

    >>> selection_split('a1')
    ['a1']
    >>> selection_split('a1[3:5]')
    ['a1[3:5]']
    >>> selection_split('a1[3:5+6:7]')
    ['a1[3:5+6:7]']
    >>> selection_split('a1[3:5+6:7]+a2[1:4]')
    ['a1[3:5+6:7]', '+', 'a2[1:4]']
    >>> selection_split('a1[3:5+6:7]+a2[1:4]', keep_delimiters=False)
    ['a1[3:5+6:7]', 'a2[1:4]']
    >>> selection_split('a1 a2  a3')
    ['a1', ' ', 'a2', ' ', ' ', 'a3']

    """
    pass


def span_split(expression, keep_delimiters=True):
    """
    Split the expression into individual span expressions. The
    delimiters will be kept as separate items if keep_delimters=True.
    Also works on space-separated ID lists, although the space character
    will be considered a delimiter.

    >>> span_split('a1')
    ['a1']
    >>> span_split('a1[3:5]')
    ['a1[3:5]']
    >>> span_split('a1[3:5+6:7]')
    ['a1[3:5]', '+', 'a1[6:7]']
    >>> span_split('a1[3:5+6:7]', keep_delimiters=False)
    ['a1[3:5]', 'a1[6:7]']
    >>> span_split('a1[3:5+6:7]+a2[1:4]')
    ['a1[3:5]', '+', 'a1[6:7]', '+', 'a2[1:4]']
    >>> span_split('a1 a2  a3')
    ['a1', ' ', 'a2', ' ', ' ', 'a3']

    """
    pass

def ids(expression):
    """
    Return the list of ids in the expression.

    >>> ids('a1')
    ['a1']
    >>> ids('a1[3:5]')
    ['a1']
    >>> ids('a1[3:5+6:7]+a2[1:4]')
    ['a1', 'a2']
    >>> ids('a1 a2  a3')
    ['a1', 'a2', 'a3']

    """

    alignments = algnexpr_re.findall(expression or '')
    return [item_id for _, item_id, _ in alignments if item_id]

# operations with interpretation



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
    )


def _enumerate_spans(expression, container):
    pass

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
