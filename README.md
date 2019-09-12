# GitMarkdownLiaison

A Sublime Text package that assists in version control of Markdown text files by quietly inserting linebreaks after every sentence.

## But why?

Git is a bit of a pain to use with files that mostly contain prose. Git works on a line-by-line basis, but English ideas work sentence-by-sentence. If you soft-wrap your text, then Git records a single character change as a change to the entire paragraph. If you hard-wrap, then adding or removing a word can do the same thing. If you insert a new line after every sentence Git copes pretty well, but then you have to cope with editing a really ugly file.

GitMarkdownLiaison solves this by doing a sentence-wrap behind the scenes. Whenever a file is loaded, GitMarkdownLiaison removes single linebreaks at the end of sentences so that Sublime's soft wrapping can make paragraphs look beautiful. When a file is saved, GitMarkdownLiaison inserts newlines after every sentence, saves to disk, and then removes the linebreaks again in the buffer. Your files are stored on disk with hard single linebreaks after every sentence, but to you they look nicely soft-wrapped.

## Configuration

GitMarkdownLiaison can be configured via the `GitMarkdownLiaison.sublime-settings` file, accessible through the `Preferences -> Package Settings -> GitMarkdownLiaison` menu. It can also be configured in your project file:

```json
{
    "settings":
    {
        "git_markdown_liaison": {
            // Filename extensions to operate on (if active)
            "extensions": [
                ".md"
            ],
            // Whether the plugin is active for this project
            "active": true,

            // Commands to run on the view to transform the text before and after saving
            "to_disk_command": "insert_newlines_liaison",
            "from_disk_command": "remove_newlines_liaison",

            // Selector in which newlines will be inserted/removed 
            // (if active and with appropriate filename extension)
            "sentence_newline_selector": "text.html.markdown meta.paragraph.markdown",
        },
    }
}
```

Note that the `settings` and `git_markdown_liaison` sections are only for when configuration is happening in a project file.

 - `active`: Master control switch for GitMarkdownLiaison. If this is False, as it is by default, nothing will happen. I set it as False, and then enable it for individual projects where I want it.
 - `extensions`: A list of filename extensions for which to enable GitMarkdownLiaison
 - `sentence_newline_selector`: The Sublime selector for the scopes where the newline manipulation should happen. By default, it just happens in Markdown paragraphs. Note that this is referred to only in the liaison commands, and will not apply to any other commands used with the following two options.
 - `to_disk_command` and `from_disk_command`: Commands to run on either side of saving or loading a file. `to_disk_command` is run before every save, and `from_disk_command` is run after every save and load. The plugin will take care of making sure the edits are transparent to Sublime. It will also ensure that they are only run in the appropriate files with respect to extension and activity, but **not** with respect to the selector.

 Between these last four options, you can probably make this work for whatever you like.

## Known Issues

I still haven't completely cracked maintaining the scratch setting on the buffers. If a file insists that it hasn't been changed since you saved it, no matter how much you change it, try putting:
```python
sublime.active_window().active_view().set_scratch(False)
```
into the console (Ctrl+`) and saving.
