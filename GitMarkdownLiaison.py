import sublime
import sublime_plugin
from pathlib import Path
from functools import partial
import re

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

    def find_and_replace_all(self, edit, pattern, repl, count=0, flags=0):
        selector = self.get_settings("sentence_newline_selector")
        regions = self.view.find_by_selector(selector)
        for region in regions:
            text = self.view.substr(region)
            text = re.sub(
                pattern=pattern,
                repl=repl,
                string=text,
                count=count,
                flags=flags
            )
            self.view.replace(edit, region, text)



class RemoveNewlinesLiaison(GitMarkdownLiaisonCommand):
    pattern = re.compile(r'\.\n(\n*)')
    def run(self, edit):
        self.find_and_replace_all(edit, self.pattern, r'. \1')


class InsertNewlinesLiaison(GitMarkdownLiaisonCommand):
    pattern1 = re.compile(r'\.(\n+)')
    pattern2 = re.compile(r'\. ([^\n])')
    def run(self, edit):
        self.find_and_replace_all(edit, self.pattern1, r'.\n\1')
        self.find_and_replace_all(edit, self.pattern2, r'.\n\1')


class GitMarkdownLiaisonListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        view.run_command('insert_newlines_liaison')

    def on_post_save(self, view):
        view.run_command('remove_newlines_liaison')

    def on_load(self, view):
        view.run_command('remove_newlines_liaison')

