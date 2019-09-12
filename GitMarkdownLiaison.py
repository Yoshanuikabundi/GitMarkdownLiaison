import sublime
import sublime_plugin
from pathlib import Path
import re
from zlib import adler32

def hash_buffer(view):
    '''Deterministic hash of the text in the buffer underlying a view'''
    whole_buffer_region = sublime.Region(0, view.size())
    text = view.substr(whole_buffer_region)
    text_bytes = bytes(text, 'UTF-8')
    return str(adler32(text_bytes) & 0xffffffff)

def get_settings(view, setting, default=None):
    '''Get a setting from the project file if available'''
    try:
        project_data = view.window().project_data()
        project_settings = project_data['settings']['git_markdown_liaison']
    except (KeyError, AttributeError):
        project_settings = {}

    if setting in project_settings:
        return project_settings[setting]
    else:
        settings = sublime.load_settings('GitMarkdownLiaison.sublime-settings')
        return settings.get(setting, default)

def gml_active_on_view(view):
    '''True if GitMarkdownLiaison should be active on view'''
    if not get_settings(view, "active"):
        return False

    try:
        path = Path(view.file_name())
    except TypeError:
        path = Path()

    extension = path.suffix
    allowed_extensions = get_settings(view, "extensions")
    if extension in allowed_extensions:
        return True
    else:
        return False


class GitMarkdownLiaisonCommand(sublime_plugin.TextCommand):
    '''Base class for commands in this module'''
    def get_settings(self, *args, **kwargs):
        return get_settings(self.view, *args, **kwargs)

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
    state_file = sublime.load_settings('GML_state.sublime-settings')
    _unmodified_views_hashes = state_file.get('views', {})

    @property
    def unmodified_views_hashes(self):
        '''Handle sublime's tardy loading of settings'''
        if self._unmodified_views_hashes is None:
            self.__class__.state_file = sublime.load_settings(
                'GML_state.sublime-settings'
            )
            self.__class__._unmodified_views_hashes = self.state_file.get(
                'views',
                {}
            )
        return self._unmodified_views_hashes

    def on_pre_save(self, view):
        if not gml_active_on_view(view):
            return

        cmd = get_settings(
            view,
            'to_disk_command',
            default='insert_newlines_liaison'
        )
        view.run_command(cmd)

    def on_post_save(self, view):
        if not gml_active_on_view(view):
            return

        cmd = get_settings(
            view,
            'from_disk_command',
            default='remove_newlines_liaison'
        )
        view.run_command(cmd)
        self.set_unmodified(view)

    def on_load(self, view):
        if not gml_active_on_view(view):
            return

        cmd = get_settings(
            view,
            'from_disk_command',
            default='remove_newlines_liaison'
        )
        view.run_command(cmd)
        self.set_unmodified(view)

    def on_modified(self, view):
        '''Set scratch on if nothing's changed since saving

        Makes the buffer return clean when it should be clean, and dirty
        when it should be dirty, so Sublime knows when the file has been
        changed since last save.

        Note: This is hacky, and co-opts setting the scratch setting for
        buffers. Hopefully I've included enough checks that it won't cause
        any problems.'''
        if not gml_active_on_view(view):
            return

        view_id = str(view.id())
        if view_id not in self.unmodified_views_hashes:
            return

        if self.unmodified_views_hashes[view_id] == hash_buffer(view):
            view.set_scratch(True)
        else:
            view.set_scratch(False)

    def on_close(self, view):
        '''Clean up the state when a view closes'''
        if gml_active_on_view(view):
            view_id = str(view.id())
            del self.unmodified_views_hashes[view_id]
            self.state_file.set('views', self.unmodified_views_hashes)
            sublime.save_settings('GML_state.sublime-settings')

    def set_unmodified(self, view):
        '''Store the hash of the unmodified view after a save/load'''
        view_id = str(view.id())
        if view.is_scratch() and view_id not in self.unmodified_views_hashes:
            return

        self.unmodified_views_hashes[view_id] = hash_buffer(view)
        self.state_file.set('views', self.unmodified_views_hashes)
        sublime.save_settings('GML_state.sublime-settings')

        view.set_scratch(True)
