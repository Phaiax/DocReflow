# DocReflow

Sublime 3 plugin (tested with Build 3126)

This plugin reorders flow text within comments.

The default keycode is `shift+alt+f shift+alt+f`.

![Example usage](https://raw.githubusercontent.com/Phaiax/DocReflow/master/animated.gif)

It does not work with different types of comments at the same time. So selecting all comments in the example (`/// and //`) would produce rubbish.

Currently works with `#`, `//`, `///`, `--` and `//!`. Multi line comments like `/* */` are not supported.

This plugin is rough, but does it's job well enough. If it doesn't work out, a undo (`ctrl+z`) will revert the changes.