# Unit tests for the `xigt.codecs.xigtjson` module

To run this test individually, do this at the command prompt:

    $ python -m doctest tests/test_xigtjson.md

It is also part of the full batch of tests. To run all tests, do this:

    $ ./setup.py test

Note: nothing will be shown if tests pass. You can add a verbose flag
(`-v`) to see all results.

There are four API functions:

* [`xigtjson.load()`](#xigtjson_load) - load from a file
* [`xigtjson.loads()`](#xigtjson_loads) - load from a string
* [`xigtjson.dump()`](#xigtjson_dump) - write to a file
* [`xigtjson.dumps()`](#xigtjson_dumps) - serialize to a string

In order to test the methods that access files, we'll need a
temporary directory to read files from and write files to. Make sure
this is cleaned up [at the end](#cleaning-up).

```python
>>> from os.path import join as pjoin
>>> import tempfile  # for mkdtemp
>>> tmpdir = tempfile.mkdtemp()

```

## Loading the `xigtjson` module

The `xigtjson` module is a library of functions, not a script, so import it:

```python
>>> from xigt.codecs import xigtjson

```

## Loading corpora

First make a test corpus to load:

```python
>>> tmpfile = pjoin(tmpdir, 'tmp.json')
>>> with open(tmpfile, 'w') as f:
...     print('''{
...   "namespaces": { "dc": "http://purl.org/dc/elements/1.1/" },
...   "metadata": [
...     {
...       "metas": [ { "id": "md1", "text": "Some metadata" } ]
...     },
...     {
...       "metas": [
...         {
...           "id": "md2",
...           "children": [
...             {
...               "namespace": "dc",
...               "name": "element",
...               "attributes": { "dc:attr": "val" }
...             },
...             {
...               "name": "dc:subject",
...               "attributes": { "attr": "val" }
...             }
...           ]
...         }
...       ]
...     }
...   ],
...   "igts": [
...     {
...       "id": "igt1",
...       "tiers": [
...         {
...           "id": "p",
...           "type": "phrases",
...           "items": [
...             { "id": "p1", "text": "El perro corre." }
...           ]
...         },
...         {
...           "id": "w",
...           "type": "words",
...           "attributes": { "segmentation": "p" },
...           "items": [
...             { "id": "w1", "attributes": { "segmentation": "p1[0:2]" } },
...             { "id": "w2", "attributes": { "segmentation": "p1[3:8]" } },
...             { "id": "w3", "attributes": { "segmentation": "p1[9:14]" } }
...           ]
...         },
...         {
...           "id": "t",
...           "type": "translations",
...           "attributes": { "alignment": "p" },
...           "items": [
...             {
...               "id": "t1",
...               "attributes": { "alignment": "p1" },
...               "text": "The dog runs."
...             }
...           ]
...         }
...       ]
...     }
...   ]
... }
... ''', file=f)

```

<a name="xigtjson_load" href="#xigtjson_load">#</a>
xigtjson.**load**(_f_, _mode='full'_)

```python
>>> xc = xigtjson.load(tmpfile)
>>> len(xc)
1
>>> len(xc.metadata)
2
>>> xc.metadata[1].metas[0].children[0].namespace
'http://purl.org/dc/elements/1.1/'
>>> xc.metadata[1].metas[0].children[1].namespace
'http://purl.org/dc/elements/1.1/'
>>> xc[0].id
'igt1'
>>> xc[0]['w']['w3'].value()
'corre'

```

<a name="xigtjson_loads" href="#xigtjson_loads">#</a>
xigtjson.**loads**(_s_)

```python
>>> xc = xigtjson.loads(open(tmpfile).read())
>>> xc[0]['w']['w2'].value()
'perro'

```

## Writing corpora

In order to check the output of the JSON serializer, we need to
inspect the re-parsed object, because the actual keys may be in a
different order than expected.

```python
>>> import json

```

First create a corpus object to serialize:

```python
>>> from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta, MetaChild
>>> xc = XigtCorpus(
...   nsmap={'dc': 'http://purl.org/dc/elements/1.1/'},
...   metadata=[
...     Metadata(metas=[Meta(id="md1", text="meta text")]),
...     Metadata(
...       metas=[
...         Meta(id="md2", children=[MetaChild(name='subject', namespace='dc')])
...       ]
...     )
...   ],
...   igts=[
...     Igt(
...       id="igt1",
...       tiers=[
...         Tier(
...           id="p",
...           type="phrases",
...           items=[Item(id="p1", text="La gata duerme.")]
...         ),
...         Tier(
...           id="t",
...           type="translations",
...           alignment="p",
...           items=[Item(id="t1", alignment="p1", text="La gata duerme.")]
...         )
...       ]
...     )
...   ]
... )

```

<a name="xigtjson_dump" href="#xigtjson_dump">#</a>
xigtjson.**dump**(_f_, _xc_, _encoding='utf-8'_, _indent=2_)

```python
>>> tmpfile2 = pjoin(tmpdir, 'tmp2.json')
>>> xigtjson.dump(tmpfile2, xc)
>>> d = json.load(open(tmpfile2))
>>> sorted(d.keys())
['igts', 'metadata', 'namespaces']
>>> sorted(d['metadata'][0]["metas"][0].keys())
['id', 'text']
>>> d['igts'][0]['id']
'igt1'
>>> d['igts'][0]['tiers'][0]['items'][0]['text']
'La gata duerme.'

```

<a name="xigtjson_dumps" href="#xigtjson_dumps">#</a>
xigtjson.**dumps**(_xc_, _encoding='utf-8'_, _indent=2_)

```python
>>> d = json.loads(xigtjson.dumps(xc))
>>> sorted(d.keys())
['igts', 'metadata', 'namespaces']
>>> sorted(d['metadata'][0]["metas"][0].keys())
['id', 'text']
>>> d['igts'][0]['id']
'igt1'
>>> d['igts'][0]['tiers'][0]['items'][0]['text']
'La gata duerme.'

```

## Cleaning up

Clean up the temporary directory:

```python
>>> import shutil
>>> shutil.rmtree(tmpdir)

```
