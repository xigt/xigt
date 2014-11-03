# Xigt Schema Extensions

Xigt may be extended with additional RelaxNG Compact schemata, such as
for [semantic dependencies](dependencies.rnc) or
[syntax trees](syntax.rnc).

While these can be used directly for validation (e.g.
`jing -c dependencies.rnc example.xml`), this only works if there are
no other extensions. If you need more than one extension for your data,
you probably want to copy-paste the relevant parts to your own extension
file (e.g. `my-extension.rnc`) and use that for validation. This is
because RelaxNG extensions are not monotonic---they **redefine** symbols
in the schema, rather than just add information---so a second extension
would overwrite the changes the first extension made.