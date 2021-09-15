# Change Log

## [v1.1.1] - 2021.09.14

This release fixes some alignment issues with Toolbox and updates the
supported Python versions to those currently supported upstream. Users
still on Python 2.7 should pin their version of Xigt to v1.1.0.

### Changed

* The Toolbox importer can now try to get sub-segment alignment.

* The Toolbox importer decodes files keeping multi-byte characters in
  their byte position, to aid with alignment (see #48)

### Compatibility

* Python2.7 through 3.5 support is removed, Python 3.6 through 3.9
  support is added.


## [v1.1.0] - 2016.01.13

This minor version change fixes a number of bugs from [v1.0] and
introduces some new features, including XigtPath and the XigtJSON
format. This version is also the first version hosted under the
Xigt organization on Github: https://github.com/xigt/xigt

### Added

* xigt.xigtpath - an XPath-like query language that is aware of Xigt
  references and structure.
* xigt.codecs.xigtjson - a JSON serialization format for the Xigt
  data model (useful for Xigt-based web apps)
* Igt.sort_tiers() for sorting tiers based on their reference dependencies
* `xigt sort` command for sorting IGTs or tiers in a corpus
* `xigt partition` command for (re)grouping IGTs on some criterion
* Markdown tests for `xigtxml` and `xigtjson`

### Fixed

* xigt.importers.toolbox and xigt.exporters.itsdb now work with Python2
* xigt.importers.toolbox now works better with undeclared tiers
* xigtxml now throws a (decipherable) error if the given object is not an
  instance of XigtCorpus (see #31)

### Changed

* The ODIN and Abkhaz example XML files have been updated to the most
  current conventions.
* The schemata for Xigt and the examples have been updated. The schema should
  now be a little easier to extend, as well. The xigt-igt.rnc and
  xigt-corpus.rnc files have been added to make it easier to customize
  higher-level things, and all default subtyping has been moved to
  xigt-default.rnc. Extensions can now build on extensions, so the ODIN and
  Abkhaz examples build on top of default-xigt.rnc rather than xigt.rnc.
* The xigt.sh script now uses `python` instead of `python3`
* XigtContainerMixin.select()
  - Now allows any model attributes (`id`, `type`, etc.) to be selection
    criteria. This was done to allow non-modeled attributes on things
    like MetaChild objects.
  - If the `namespace` attribute is used, its value will be replaced
    with the appropriately mapped namespace via `nsmap`, if a mapping
    exists.
* xigt.importers.toolbox
  - the config schema has changed: see comments at the top of
    [xigt/importers/toolbox.py]
  - phrase tiers can be created from words tiers
* Unit tests have been converted to pytest

### Removed

* xigt.importers.odin functions for cleaning and normalization
* `xigt process` command (see `xigt partition` under **Added**)

### Compatibility

* Python3.2 support is removed (Xigt still supports Python versions
  2.7, 3.3, 3.4, and 3.5)

## [v1.0] - 2015.04.24

### Added

* Meta objects now take a "children" argument, which is for nested
  (non-string) content.
* The MetaChild class is added to structurally model such children of Meta.
* Namespace support is added to aid with XML serialization and querying of
  in-memory objects.
* Unit tests now cover all API classes, methods, and functions for
  xigt.model, xigt.ref, and xigt.query.
* xigt.importers.odin is added for pulling ODIN-style IGTs into Xigt and
  doing some cleanup. It doesn't infer structure, though (for that, see
  https://bitbucket.org/ryageo/intent)

### Fixed

* A handful of Python3 code in scripts was preventing them from running with
  Python2. Now I think everything works in both Py3 and Py2 (update: two
  optional modules, `xigt.importers.toolbox` and `xigt.exporters.itsdb`,
  did not work with Py2, but they don't interfere with the other parts
  of Xigt, and this issue is fixed in a recent commit).
* xigtxml now reads <metadata> for Python2 (a map() problem meant that it was
  cleared in Py2 before it could be parsed)
* xigtxml now serializes and deserializes Metadata and Meta elements correctly
* xigt.query.descendants now checks for cycles
* bugs fixed in xigt.ref.{referrers,dereference,dereference_all}

### Changed

* rename get_aligment_expression_ids() to get_alignment_expression_ids()
  This function was deprecated, but somewhere along the lines it got renamed.
  This just fixes the rename.
* All containers now restrict the type of object contained
* Metadata are now contained by a standalone XigtContainerMixin
* XigtContainerMixin can now take a "container" attribute which determines
  the _parent of the contained objects (to help with the Metadata case)

## [v1.0rc1] - 2015.04.07

### Added

* xigt.query : advanced queries of the data
  - [xigt.query.ancestors()](../../wiki/Queries#ancestors)
  - [xigt.query.descendants()](../../wiki/Queries#descendants)
* more extensive unit tests (but still not full coverage)

### Changed

* xigt.core is split into:
  - xigt.model : data model classes
  - xigt.mixins : common parent classes for data model classes
  - xigt.ref : functions for reference attribute resolution and interpretation
  - xigt.consts : any constants or literals

### Deprecated

* get_aligned_tier()
  &mdash; see [ref.dereference()](../../wiki/References#dereference)
* get_aligment_expression_ids()
  &mdash; see [ref.ids()](../../wiki/References#ids)
* get_alignment_expression_spans()
  &mdash; see [ref.spans()](../../wiki/References#spans)
* resolve_alignment_expression()
  &mdash; see [ref.resolve()](../../wiki/References#resolve)
* resolve_alignment()
  &mdash; see [ref.dereference()](../../wiki/References#dereference)
* Item.get_content()
  &mdash; see [Item.value()](../../wiki/Data-Structures#Item_value)
* Metadata.text
  &mdash; see [Metadata.metas](../../wiki/Data-Structures#Metadata_metas)
* XigtContainerMixin.add()
  &mdash; see [XigtContainerMixin.append()](../../wiki/Data-Structures#Container_append)
* XigtContainerMixin.add_list()
  &mdash; see [XigtContainerMixin.extend()](../../wiki/Data-Structures#Container_extend)

### Removed

* codecs.xigttxt

## [v0.9] - 2015.03.20

Xigt didn't have any versioned releases prior to 0.9, although setup.py
reported a version of 0.1 for some time. This version is a precursor to a 1.0
release. Since there are no prior releases, there aren't any "changes" to
report here.


[unreleased]: https://github.com/xigt/xigt/tree/develop
[v0.9]: https://github.com/xigt/xigt/releases/tag/v0.9
[v1.0rc1]: https://github.com/xigt/xigt/releases/tag/v1.0rc1
[v1.0]: https://github.com/xigt/xigt/releases/tag/v1.0
[v1.1.0]: https://github.com/xigt/xigt/releases/tag/v1.1.0
[v1.1.1]: https://github.com/xigt/xigt/releases/tag/v1.1.1
