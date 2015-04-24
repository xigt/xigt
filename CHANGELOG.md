# Change Log

## [Unreleased][unreleased]

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
  Python2. Now I think everything works in both Py3 and Py2.
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


[unreleased]: https://github.com/goodmami/xigt/tree/develop
[v0.9]: https://github.com/goodmami/xigt/releases/tag/v0.9
[v1.0rc1]: https://github.com/goodmami/xigt/releases/tag/v1.0rc1
[v1.0]: https://github.com/goodmami/xigt/releases/tag/v1.0