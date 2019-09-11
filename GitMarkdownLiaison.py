import sublime
import sublime_plugin
from pathlib import Path
from functools import partial

class GitMarkdownLiaisonCommand(sublime_plugin.TextCommand):
    def get_settings(self, setting, default=None):
        '''All settings can be configured in the project file'''
        try:
            project_data = self.view.window().project_data()
            project_settings = project_data['settings']['git_markdown_liaison']
        except (KeyError, AttributeError):
            project_settings = {}

        if setting in project_settings:
            return project_settings[setting]
        else:
            settings = sublime.load_settings('GitMarkdownLiaison.sublime-settings')
            return settings.get(setting, default)

    def is_enabled(self):
        if not self.get_settings("active"):
            return False

        try:
            path = Path(self.view.file_name())
        except TypeError:
            path = Path()

        extension = path.suffix
        allowed_extensions = self.get_settings("extensions")
        if extension in allowed_extensions:
            return True
        else:
            return False

    def is_visible(self):
        return False

    def find_and_replace_all(self, edit, pattern, string, flags=0, selector=None):
        regions = self.view.find_all(pattern, flags=flags)
        for region in regions:
            point = region.begin()
            if selector and not self.view.match_selector(point, selector):
                break
            self.view.replace(edit, region, string)


class RemoveNewlinesLiaison(GitMarkdownLiaisonCommand):
    def run(self, edit):
        find_and_replace_all = partial(
            self.find_and_replace_all,
            edit,
            flags=sublime.LITERAL,
            selector=self.get_settings("sentence_newline_selector")
        )

        find_and_replace_all(r' +\n', '\n', flags=0)
        find_and_replace_all('.\n', '. ')
        find_and_replace_all('. \n', '.\n\n')

        return


class InsertNewlinesLiaison(GitMarkdownLiaisonCommand):
    def run(self, edit):
        self.find_and_replace_all(
            edit,
            '. ',
            '.\n',
            flags=sublime.LITERAL,
            selector=self.get_settings("sentence_newline_selector")
        )
        return


class GitMarkdownLiaisonListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        view.run_command('insert_newlines_liaison')

    def on_post_save(self, view):
        view.run_command('remove_newlines_liaison')

    def on_load(self, view):
        view.run_command('remove_newlines_liaison')

