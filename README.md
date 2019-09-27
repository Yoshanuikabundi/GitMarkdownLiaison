# GitMarkdownLiaison

A Sublime Text package that assists in version control of Markdown text files by quietly inserting linebreaks after every sentence.

## But why?

Git is a bit of a pain to use with files that mostly contain prose.
Git works on a line-by-line basis, but English ideas work sentence-by-sentence.
If you soft-wrap your text, then Git records a single character change as a change to the entire paragraph.
If you hard-wrap, then adding or removing a word can do the same thing.
If you insert a new line after every sentence Git copes pretty well, but then you have to cope with editing a really ugly file.

GitMarkdownLiaison solves this by doing a sentence-wrap behind the scenes.
Whenever a file is loaded, GitMarkdownLiaison removes single linebreaks at the end of sentences so that Sublime's soft wrapping can make paragraphs look beautiful.
When a file is saved, GitMarkdownLiaison inserts newlines after every sentence, saves to disk, and then removes the linebreaks again in the buffer.
Your files are stored on disk with hard single linebreaks after every sentence, but to you they look nicely soft-wrapped.

This file has been written with GitMarkdownLiaison.
Did you like it?

## Configuration

GitMarkdownLiaison can be configured via the `GitMarkdownLiaison.sublime-settings` file, accessible through the `Preferences -> Package Settings -> GitMarkdownLiaison` menu.
It can also be configured in your project file:

```javascript
{
    "settings":
    {
        "git_markdown_liaison": {
            // Extensions to operate on
            // In this project, I only want GML to run on .md files,
            // though by default it also runs on .markdown files
            "extensions": [
                ".md"
            ],
            // Whether the plugin is active - set false by default so you can enable it in specific projects
            "active": true,

            // Selector in which newlines will be inserted/removed
            // I don't want to insert newlines in lists, so I changed
            // the second scope in this selector
            "sentence_newline_selector": "text.html.markdown meta.paragraph.markdown",

            //// Python-style regex
            // Be sure to escape backslashes!
            // I've kept the defaults here - newlines are inserted in
            // place of any single space between a full stop and a
            // capital letter, and the remover does the opposite.
            // These two strings determine how to remove lines
            "remove_lines_find_re": "(\\.)\\n([A-Z])",
            "remove_lines_replace": "\\1 \\2",
            // These two strings determine how to insert lines
            "insert_lines_find_re": "(\\.) ([A-Z])",
            "insert_lines_replace": "\\1\\n\\2"
        },
    }
}
```

Note that the `settings` and `git_markdown_liaison` sections are only for when configuration is happening in a project file.
An example of both the settings and project files are included.

 - `active`: Master control switch for GitMarkdownLiaison.
If this is False, as it is by default, nothing will happen.
I set it as False, and then enable it for individual projects where I want it.

 - `extensions`: A list of filename extensions for which to enable GitMarkdownLiaison

 - `sentence_newline_selector`: The Sublime selector for the scopes where the newline manipulation should happen.
By default, it just happens in Markdown paragraphs.

 - `remove_lines_find_re`, `remove_lines_replace`, `insert_lines_find_re` and `insert_lines_replace`: Regex find and replace to run to insert and remove lines.
Python's [`re`](https://docs.python.org/3.3/library/re.html) package is used if you want more documentation.
Only runs on regions that match the selector.

 Between these last six options, you can probably make this work for whatever you like.

## Known Issues

If a file insists that it hasn't been changed since you saved it, no matter how much you change it, try putting:
```python
sublime.active_window().active_view().set_scratch(False)
```
into the console (Ctrl+`) and saving.
This shouldn't happen but who knows.
Also I make no claims with regard to speed, though my computer seems to cope.
