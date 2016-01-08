# Unit tests for the `xigt.codecs.xigtxml` module

To run this test individually, do this at the command prompt:

    $ python -m doctest tests/test_xigtxml.md

It is also part of the full batch of tests. To run all tests, do this:

    $ ./setup.py test

Note: nothing will be shown if tests pass. You can add a verbose flag
(`-v`) to see all results.

There are four API functions:

* [`xigtxml.load()`](#xigtxml_load) - load from a file
* [`xigtxml.loads()`](#xigtxml_loads) - load from a string
* [`xigtxml.dump()`](#xigtxml_dump) - write to a file
* [`xigtxml.dumps()`](#xigtxml_dumps) - serialize to a string

In order to test the methods that access files, we'll need a
temporary directory to read files from and write files to. Make sure
this is cleaned up [at the end](#cleaning-up).

```python
>>> from os.path import join as pjoin
>>> import tempfile  # for mkdtemp
>>> tmpdir = tempfile.mkdtemp()

```

## Loading the `xigtxml` module

The `xigtxml` module is a library of functions, not a script, so import it:

```python
>>> from xigt.codecs import xigtxml

```

## Loading corpora

First make a test corpus to load:

```python
>>> tmpfile = pjoin(tmpdir, 'tmp.xml')
>>> with open(tmpfile, 'w') as f:
...     print('''<xigt-corpus>
...   <metadata><meta id="md1">Some metadata</meta></metadata>
...   <metadata><meta id="md2"><element attr="val" /></meta></metadata>
...   <igt id="igt1">
...     <tier id="p" type="phrases">
...       <item id="p1">El perro corre.</item>
...     </tier>
...     <tier id="w" type="words" segmentation="p">
...       <item id="w1" segmentation="p1[0:2]" />
...       <item id="w2" segmentation="p1[3:8]" />
...       <item id="w3" segmentation="p1[9:14]" />
...     </tier>
...     <tier id="t" type="translations" alignment="p">
...       <item id="t1" alignment="p1">The dog runs.</item>
...     </tier>
...   </igt>
... </xigt-corpus>
... ''', file=f)

```

<a name="xigtxml_load" href="#xigtxml_load">#</a>
xigtxml.**load**(_f_, _mode='full'_)

```python
>>> xc = xigtxml.load(tmpfile)
>>> len(xc)
1
>>> len(xc.metadata)
2
>>> xc[0].id
'igt1'
>>> xc[0]['w']['w3'].value()
'corre'

```

<a name="xigtxml_loads" href="#xigtxml_loads">#</a>
xigtxml.**loads**(_s_)

```python
>>> xc = xigtxml.loads(open(tmpfile).read())
>>> xc[0]['w']['w2'].value()
'perro'

```

## Writing corpora

First create a corpus object to serialize:

```python
>>> from xigt import XigtCorpus, Igt, Tier, Item, Metadata, Meta
>>> xc = XigtCorpus(
...   metadata=[Metadata(metas=[Meta(id="md1", text="meta text")])],
...   igts=[
...     Igt(
...       id="igt1",
...       tiers=[
...         Tier(
...           id="p",
...           type="phrases",
...           items=[Item(id="p1", text="La gata duerme.")]
...         )
...       ]
...     )
...   ]
... )

```

<a name="xigtxml_dump" href="#xigtxml_dump">#</a>
xigtxml.**dump**(_f_, _xc_, _encoding='utf-8'_, _indent=2_)

```python
>>> tmpfile2 = pjoin(tmpdir, 'tmp2.xml')
>>> xigtxml.dump(tmpfile2, xc)
>>> print(open(tmpfile2).read())
<xigt-corpus>
  <metadata>
    <meta id="md1">meta text</meta>
  </metadata>
  <igt id="igt1">
    <tier id="p" type="phrases">
      <item id="p1">La gata duerme.</item>
    </tier>
  </igt>
</xigt-corpus>
<BLANKLINE>

```

<a name="xigtxml_dumps" href="#xigtxml_dumps">#</a>
xigtxml.**dumps**(_xc_, _encoding='utf-8'_, _indent=2_)

```python
>>> print(xigtxml.dumps(xc))
<xigt-corpus>
  <metadata>
    <meta id="md1">meta text</meta>
  </metadata>
  <igt id="igt1">
    <tier id="p" type="phrases">
      <item id="p1">La gata duerme.</item>
    </tier>
  </igt>
</xigt-corpus>
<BLANKLINE>

```

## Cleaning up

Clean up the temporary directory:

```python
>>> import shutil
>>> shutil.rmtree(tmpdir)

```
