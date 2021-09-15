Xigt
====

[![PyPI Version](https://img.shields.io/pypi/v/xigt.svg)](https://pypi.org/project/Xigt/)
![Python Support](https://img.shields.io/pypi/pyversions/xigt.svg)
[![.github/workflows/checks.yml](https://github.com/xigt/xigt/actions/workflows/checks.yml/badge.svg?branch=develop)](https://github.com/xigt/xigt/actions/workflows/checks.yml)

A framework for *eXtensible Interlinear Glossed Text*
([IGT](http://en.wikipedia.org/wiki/Interlinear_gloss)).

* [Introduction](#introduction)
* [Documentation](https://github.com/xigt/xigt/wiki)
* [Installation and Requirements](#installation-and-requirements)
* [Features](#features)
* [Acknowledgments](#acknowledgments)


### Introduction

The philosophy of Xigt is that IGT data should be
[simple for the common cases](https://github.com/xigt/xigt/wiki/Basic-Schema)
while easily
[scaling up](https://github.com/xigt/xigt/wiki/Schema-Extensions)
to accommodate different kinds of annotations. New
annotations do not need to alter the original data, but instead can be
applied on top of them. Furthermore, Xigt data is meant to be easily
[processed by computers](https://github.com/xigt/xigt/wiki/Tutorials) so
that it's easy to inspect, analyze, and modify IGT data.

The Xigt framework includes a
[data model and XML format](https://github.com/xigt/xigt/wiki/Data-Model)
as well as a Python [API](https://github.com/xigt/xigt/wiki/API-Reference)
for working with Xigt data.

Here is a small example of an IGT encoded in
Xigt's XML format:

```xml
<igt id="i1" lg="spa">
  <tier type="words" id="w">
    <item id="w1">cocinas</item>
  </tier>
  <tier type="morphemes" id="m" segmentation="w">
    <item id="m1" segmentation="w1[0:5]"/>  <!-- selects "cocin" -->
    <item id="m2" segmentation="w1[5:7]"/>  <!-- selects "as" -->
  </tier>
  <tier type="glosses" id="g" alignment="m">
    <item id="g1" alignment="m1">cook</item>
    <item id="g2" alignment="m2">2</item>
    <item id="g3" alignment="m2">SG</item>
    <item id="g4" alignment="m2">PRS</item>
    <item id="g5" alignment="m2">IND</item>
  </tier>
</igt>
```


### Installation and Requirements

The [Xigt API](https://github.com/xigt/xigt/wiki/API-Reference) is
coded in [Python](http://python.org/download/) (targeting Python 3.3+,
but it is tested to work with Python 2.7).

Xigt can be installed via [pip](https://docs.python.org/3/installing/)
(see [PyPI](https://pypi.python.org/pypi/Xigt)):

```bash
pip install xigt
```

(You may need to use `pip3` to install for Python3.).

Alternatively, you can get the latest Xigt from the GitHub repository:

```bash
git clone https://github.com/xigt/xigt.git
```

After the cloning has finished, set up your
[`PYTHONPATH`](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH)
environment variable to point to this directory.

The following extra features have their own requirements:
* The Toolbox importer: get the [toolbox](http://github.com/goodmami/toolbox)
  module
* The ODIN importer: get [odin-utils](https://github.com/xigt/odin-utils)
* The [incr tsdb()] profile exporter: get
  [pyDelphin](https://github.com/goodmami/pydelphin)

For validating Xigt's XML format, I recommend
[Jing](http://www.thaiopensource.com/relaxng/jing.html).

Depending on the importer, you may need to configure a `config.json`
for your particular use case, and point Xigt's import function to it
using the built-in commands. Templates for the respective
configurations are found within the files in `xigt/importers`.

Note: Xigt is primarily developed and tested on Linux. If you are having
trouble installing on Windows, Mac, or some other operating system, please
contact me or file an [issue report](https://github.com/xigt/xigt/issues).


### Features ###

Xigt has several features that help enable complex alignments, and
these features can be ignored for simpler IGT.

##### Alignment Expressions

[Alignment expressions](https://github.com/xigt/xigt/wiki/Alignment-Expressions)
are an expanded referencing system that allow some data to align to more
than one target, and furthermore allows them to select substrings from
the target(s).

Given:

```xml
<item id="a1">one</item>
<item id="a2">two</item>
```

The following alignment expressions will align to the following selections:

```python
a1                  -> "one"
a1,a2               -> "one two"
a1+a2               -> "onetwo"
a1[0:1]             -> "o"
a1[0:1,2:3]         -> "o e"
a1[1:3]+a2[1:2+0:1] -> "newt"
```

Alignment expressions are specified on
[reference attributes](https://github.com/xigt/xigt/wiki/Data-Model#xigt-reference-attributes)
at the item level.

##### Floating Alignments

When more than one item align to the same selection, they are said to be in a
"floating alignment". That is, they are ordered (as in the XML), but have no
definite subpartitioning among them. For instance, given the following phrase
item:

```xml
<tier type="phrases" id="p">
  <item id="p1">A dog barks.</item>
</tier>
```

...and the following word items all aligned to the same phrase item above:

```xml
<tier type="words" id="w" alignment="p">
  <item id="w1" alignment="p1">A</item>
  <item id="w2" alignment="p1">dog</item>
  <item id="w3" alignment="p1">barks</item>
</tier>
```

Xigt will maintain the order \["A", "dog", "barks"\] (i.e. not \["dog", "A",
"barks"\] and so on), but does not specify which substrings each item aligns to.
In other words, it is understood that **w1**, **w2**, and **w3** are contained
by **s1** and in that order, but there is no explicit character alignments. This
is useful when one does not want to delimit items exactly (e.g. when dealing
with noisy data), or when one cannot delimit the sub-items (e.g. glosses for
portmanteau morphemes).

##### Referred Values

In Xigt, the only difference between _primary data_ (e.g. phrases or words) and
_annotations_ (e.g. glosses or translations) is that annotations are aligned to
some other items. The data/annotation-label is called the "value", and this
value can either be explicitly given, or refer to some other source. In the
latter case, an alignment expression (given by the "segmentation" or "content"
reference attribute) is used to select the value.

The benefit of using alignment expressions to select item values is that the
data becomes more linked. For instance, it becomes possible to say that not
only does a morpheme align to some word, but that its value is a particular
substring of that word. A second use for referred values is stand-off
annotation, where the data comes from some external source and one wants to
encode the relationship between the IGT structure and the original data.

For example, in the above example, rather than aligning **w1**--**w3** to **p1**
and then explicitly giving the value, one can "segment" the words from the
phrase:

```xml
<tier type="phrases" id="p">
  <item id="p1">A dog barks.</item>
</tier>
<tier type="words" id="w" segmentation="p">
  <item id="w1" segmentation="p1[0:1]" />  <!-- selects "A" -->
  <item id="w2" segmentation="p1[2:5]" />  <!-- selects "dog" -->
  <item id="w3" segmentation="p1[6:11]" /> <!-- selects "barks -->
</tier>
```

Here, items **w1**, **w2**, and **w3** do not provide their own value, but
instead select it via the alignment expression on their "segmentation"
attribute.

Also note that an item can specify both a "segmentation" or "content" attribute
and explicitly provide a value, in which case the provided value overrides the
selected one, but the link remains. This is useful for cleaning up OCR results
or showing the underlying form before phonological processes have occurred.


### Acknowledgments

This material is based upon work supported by the National Science
Foundation under Grant No.
[1160274](http://www.nsf.gov/awardsearch/showAward?AWD_ID=1160274). Any
opinions, findings, and conclusions or recommendations expressed in this
material are those of the author(s) and do not necessarily reflect the
views of the National Science Foundation.

This project is also partially supported by the Affectedness project,
under the Singapore Ministry of Education Tier 2 grant (grant number
MOE2013-T2-1-016).

Xigt was initially developed under the AGGREGATION project
(http://depts.washington.edu/uwcl/aggregation/)
