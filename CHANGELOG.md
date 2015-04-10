# Change Log

## [Unreleased][unreleased]

### Added

* Meta objects now take a "children" argument, which is for nested
  (non-string) content.
* Unit tests now cover all API classes, methods, and functions for
  xigt.model, xigt.ref, and xigt.query.

### Fixed

* xigtxml now reads <metadata> for Python2 (a map() problem meant that it was
  cleared in Py2 before it could be parsed)
* xigtxml now serializes and deserializes Metadata and Meta elements correctly
* xigt.query.descendants now checks for cycles
* bugs in xigt.ref.{referrers,dereference,dereference_all}

### Changed

* xigtxml now outputs <igt> elements even if they are empty (<igt/>)
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