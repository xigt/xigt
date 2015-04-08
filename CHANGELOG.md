# Change Log

## [Unreleased][unreleased]

### Changed

* rename get_aligment_expression_ids() to get_alignment_expression_ids()
  This function was deprecated, but somewhere along the lines it got renamed.
  This just fixes the rename.

## [v1.0rc1] - 2015.04.07

### Added

* xigt.query : advanced queries of the data
  - xigt.query.ancestors()
  - xigt.query.descendants()
* more extensive unit tests (but still not full coverage)

### Changed

* xigt.core is split into:
  - xigt.model : data model classes
  - xigt.mixins : common parent classes for data model classes
  - xigt.ref : functions for reference attribute resolution and interpretation
  - xigt.consts : any constants or literals

### Deprecated

* get_aligned_tier()
    see ref.dereference()
* get_aligment_expression_ids()
    see ref.ids()
* get_alignment_expression_spans()
    see ref.spans()
* resolve_alignment_expression()
    see ref.resolve()
* resolve_alignment()
    see ref.dereference()
* Item.get_content()
    see Item.value()
* Metadata.text
    see Metadata.metas
* XigtContainerMixin.add()
    see XigtContainerMixin.append()
* XigtContainerMixin.add_list()
    see XigtContainerMixin.extend()

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