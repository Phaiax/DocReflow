import sublime
import sublime_plugin

class EmptyCommentLine:
    pass


class DocReflowFormatSelectedTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selections = self.view.sel()
        for sel in selections:
            if "comment.block" in self.view.scope_name(sel.a):
                print("DocReflow: Can only reformat line comments")

            if sel.a > sel.b:
                sel = sublime.Region(sel.b, sel.a)

            first_comment_scope = self.view.extract_scope(sel.a)
            _, comment_begin_column = self.view.rowcol(first_comment_scope.a)

            #self.print_region("selection", sel)
            #self.print_region("first_comment_scope", first_comment_scope)

            comment_identifier = self.get_comment_identifier(first_comment_scope)
            if comment_identifier is None:
                print("DocReflow: Unknown comment identifier")
                return

            preexistent_code = []
            comments = []
            lines = self.view.lines(sel)
            edit_region = self.view.full_line(sel)

            for lineregion in lines:
                linetext = self.view.substr(lineregion)
                splitted = linetext.split(comment_identifier, maxsplit=1)
                if len(splitted) == 2:
                    if len(splitted[0].strip()) > 0:
                        # line = "some code; // comment"
                        preexistent_code.append(splitted[0])
                        comments.append(splitted[1].strip())
                    else:
                        if len(splitted[1].strip()) == 0:
                            # line = "    //  "
                            preexistent_code.append("")
                            comments.append(EmptyCommentLine)
                        else:
                            # line = "    // only a comment"
                            # merge with previous comment
                            if len(comments) > 0 and comments[-1] is not None \
                                and comments[-1] is not EmptyCommentLine:
                                prev = comments.pop()
                            else:
                                prev = ""
                                preexistent_code.append("")
                            if prev == "": # can also be the case if popped
                                comments.append(splitted[1].strip())
                            else:
                                comments.append(" ".join([prev, splitted[1].strip()]))
                else:
                    if len(splitted[0].strip()) > 0:
                        # line = "some code, no comment;"
                        preexistent_code.append(splitted[0])
                        comments.append(None)
                    else:
                        # line = "   "
                        preexistent_code.append("")
                        comments.append(None)

            rulers = self.view.settings().get("rulers", [])
            if len(rulers) == 0: rulers = [80]
            max_length = rulers[-1]

            #print(preexistent_code)
            #print(comments)

            # reassemble
            result = []
            comment_column = comment_begin_column
            for code, comment in zip(preexistent_code, comments):
                result.append(code)
                col = len(code)
                if comment is EmptyCommentLine:
                    result.append(" " * comment_column)
                    result.append(comment_identifier)

                elif comment is not None:
                    comment_column = max(comment_begin_column, col)
                    missing_cols = comment_column - col;
                    assert missing_cols >= 0
                    result.append(" " * missing_cols)
                    col += missing_cols
                    result.append(comment_identifier)
                    col += len(comment_identifier)

                    words = comment.split()
                    for w in words:
                        if col + len(w) > max_length:
                            result.append("\n")
                            col = 0
                            result.append(" " * comment_column)
                            col += comment_column
                            result.append(comment_identifier)
                            col += len(comment_identifier)
                        result.append(" ")
                        col += 1
                        result.append(w)
                        col += len(w)

                result.append("\n")

            result = "".join(result)

            self.view.replace(edit, edit_region, result)


    def get_comment_identifier(self, comment_scope):
        comment = self.view.substr(comment_scope)
        if comment.startswith("#"):
            return "#"
        if comment.startswith("--"):
            return "--"
        if comment.startswith("//!"):
            return "//!"
        if comment.startswith("///"):
            return "///"
        if comment.startswith("//"):
            return "//"
        return None

    def print_region(self, name, r):
        ra,ca = self.view.rowcol(r.a)
        rb,cb = self.view.rowcol(r.b)
        l = r.b-r.a
        print("Region {} has {} chars from line {} col {} to line {} col {}".format(name, l, ra+1, ca+1, rb+1, cb+1))
