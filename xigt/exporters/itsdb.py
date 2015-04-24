
import logging
from os.path import isfile, join as pjoin
from os import environ

try:
    from delphin import itsdb
except ImportError:
    raise ImportError(
        'Could not import pyDelphin module. Get it from here:\n'
        '  https://github.com/goodmami/pydelphin'
    )

DEFAULT_CELLS = [
    # i-input is a string of either the first phrase (preferred) or all words
    ('i-input',
     'next(igt.select(type="phrases"), [""])[0] or '
     '" ".join(item.get_content() '
     '         for item in next(igt.select(type="words"),[]))'),
    #('i-wf', '0 if igt.get_meta("judgment") else 1'),
]

def xigt_export(xc, outpath, config=None):
    config = prepare_config(config)
    if not config.get('relations') or not isfile(config['relations']):
        logging.error('Relations file required for [incr tsdb()] export.')
        return
    itsdb.make_skeleton(
        outpath,
        config['relations'],
        export_corpus(xc, config)
    )

def prepare_config(config):
    if config is None:
        config = {}
    config.setdefault('i-id_start', 0)
    config.setdefault('i-id_skip', 10)
    # attempt to find default Relations file
    if 'relations' not in config and 'LOGONROOT' in environ:
        rel_path = pjoin(
            environ['LOGONROOT'],
            'lingo/lkb/src/tsdb/skeletons/english/Relations'
        )
        if isfile(rel_path):
            logging.info('Attempting to get relations file from {}'
                         .format(rel_path))
            config['relations'] = rel_path
    # evaluate lambda expressions now, since they won't change
    config.setdefault('cells', DEFAULT_CELLS)
    config['cells'] = [(key, lambda igt: eval(mapper))
                       for key, mapper in config['cells']]
    return config

def export_corpus(xc, config):
    id_start = config['i-id_start']
    id_skip = config['i-id_skip']
    for i, igt in enumerate(xc):
        config['__i-id_current__'] = id_start + (i * id_skip)
        logging.debug('Exporting {}'.format(str(igt.id)))
        x = export_igt(igt, config)
        yield x

def export_igt(igt, config):
    row = {'i-id': config['__i-id_current__']}
    for cell_map in config['cells']:
        key, mapper = cell_map
        try:
            row[key] = mapper(igt)
        except SyntaxError:
            logging.error('Malformed cell mapper expression for {}'
                          .format(key))
            raise
    return row