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
            "extensions": [
                ".md"
            ],

            "active": true,
        },
    }
}
```


 - `extensions`: A list of filename extensions for which to enable GitMarkdownLiaison
 - `active`: Master control switch for GitMarkdownLiaison. If this is False, as it is by default, nothing will happen. I set it as False, and then enable it for individual projects where I want it.
 - `sentence_newline_selector`: The Sublime selector for the scopes where the newline manipulation should happen. By default, it just happens in Markdown paragraphs. Between this option and the `extensions` option, you can probably make this work for whatever text markup format you like.

## Known Issues

This plugin modifies the buffer after every save or load, meaning that every Markdown file it touches always reads as having unsaved changes. That's pretty annoying. It's also not the fastest thing ever.
