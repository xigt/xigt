Xigt
====

A library for *eXtensible Interlinear Glossed Text*
([IGT](http://en.wikipedia.org/wiki/Interlinear_gloss))

* [Installation and Requirements](#installation-and-requirements)
* [Features](#features)
* [Acknowledgments](#acknowledgments)

Xigt is created with extensibility in mind, offering a core framework
and XML schema (in [RelaxNG](http://relaxng.org/)) ready to be extended
without much trouble. Here is a small example of an IGT encoded in
Xigt's XML format:

```xml
<igt id="i1" lg="spa">
  <tier type="words" id="w">
    <item id="w1">cocinas</item>
  </tier>
  <tier type="morphemes" id="m" segmentation="w">
    <item id="m1" segmentation="w1[0:5]"/>
    <item id="m2" segmentation="w1[5:7]"/>
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

Xigt requires the following:
* [Python3](http://python.org/download/)

For using Xigt's XML format, we recommend you also install:
* A RelaxNG validator for compact schema, like
  [Jing](http://www.thaiopensource.com/relaxng/jing.html)
* The [lxml](http://lxml.de/) XML library for Python

After downloading Xigt, install it with the setup.py command:

```Bash
$ ./setup.py install
```

Note: To remove (uninstall) Xigt, remove its package directory. On a Linux
system, this may somewhere like `/usr/lib/python3.X/site-packages/xigt/`.
There may also be an Egg info file, such as
`/usr/lib/python3.X/site-packages/Xigt-(version)-py3.X.egg-info`.

### Features ###

Xigt has several features that help enable complex alignments, and
these features can be ignored for simpler IGT.

##### Alignment Expressions

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
a1[0:1,2:3]         -> "oe"
a1[1:3]+a2[1:2+0:1] -> "newt"
```

##### Floating Alignments

When more than one item align to the same selection, they are in a floating alignment.
That is, they are ordered (as in the XML), but have no definite subpartitioning among
them. For instance, given the following item:

```xml
<item id="s1">A dog barks.</item>
```

...and the following aligned items all aligned to the same item above:

```xml
<item id="w1" alignment="s1">A</item>
<item id="w2" alignment="s1">dog</item>
<item id="w3" alignment="s1">barks</item>
```

Xigt will maintain the order \["A", "dog", "barks"\] (i.e. not \["dog", "A", "barks"\] and so on),
but does not specify the selections (i.e. character spans) from the aligned item. In other words,
it is understood that **w1**, **w2**, and **w3** are contained by **s1** and in that order, but
there is no explicit character alignments. This is
useful when one does not want to delimit items exactly, or when one cannot delimit the sub-items
(e.g. glosses for portmanteau morphemes).

##### Data Inheritance

Items can provide content, but if they don't, they inherit it from other items using the `content` or `segmentation` reference attributes. The `content` attribute may be used when providing annotation and the annotation content comes from another source (e.g. a standoff annotation). The `segmentation` attribute is useful when merely breaking up sentences into words, words into morphemes, etc., as it accomplishes two things: pulling content from and aligning to a span. The alignment during segmentation is necessary to later find where the content came from.

For example, one can delimit the morphemes of the word in item **w3** above as follows:

```xml
<item id="w3" alignment="s1">barks</item>
...
<item id="m1" segmentation="w3[0:4]"/>
<item id="m2" segmentation="w3[4:5]"/>
```

Items **m1** and **m2** do not provide their own content, so their content is inherited from the specified
spans of **w3**. That is, **m1**'s content is implicitly "bark", and **m2**'s is implicitly "s".
Later items refer to the relative character positions of the inherited content. For example,
referencing "m2[0:1]" is the character "s" (aside: since it's the entire content of **m2**, it's the same
as referencing "m2").

Also note that an item can specify both a `segmentation` attribute and provide content. This is useful when one wants the alignment of the segmentation to show where the content came from, but also want to provide different content. For example, one may use this to clean up OCR results or show the underlying form before phonological processes have occurred.

##### Data Shadowing

When an item **x** provides content, later items referring to **x** can only select alignments to **x**'s
content, and not that of any items **x** refers to. For example, in the following, the content of **y** is
"t", and not "o".

```xml
<item id="w">one</item>
...
<item id="x" segmentation="w">two</item>
...
<item id="y" segmentation="x[0:1]"/>
```

### Acknowledgments

This material is based upon work supported by the National Science Foundation
under Grant No.
[1160274](http://www.nsf.gov/awardsearch/showAward?AWD_ID=1160274).Any opinions,
findings, and conclusions or recommendations expressed in this material are
those of the author(s) and do not necessarily reflect the views of the National
Science Foundation.

Xigt was developed under the AGGREGATION project
(http://depts.washington.edu/uwcl/aggregation/)
