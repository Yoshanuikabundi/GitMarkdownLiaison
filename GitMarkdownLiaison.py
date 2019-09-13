import sublime
import sublime_plugin
from pathlib import Path
import re
from zlib import adler32

def reverse_dict_lookup(mapping, value):
    for k, v in mapping.items():
        if v == value:
            return k
    raise ValueError('Value not in dict')

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
    pattern1 = re.compile(r'\.\n(\n*)')
    pattern2 = re.compile(r'\. \n')

    def run(self, edit):
        self.find_and_replace_all(edit, self.pattern1, r'. \1')
        self.find_and_replace_all(edit, self.pattern2, r'.\n')


class InsertNewlinesLiaison(GitMarkdownLiaisonCommand):
    pattern1 = re.compile(r'\.(\n+)')
    pattern2 = re.compile(r'\. ([^\n])')

    def run(self, edit):
        self.find_and_replace_all(edit, self.pattern1, r'.\n\1')
        self.find_and_replace_all(edit, self.pattern2, r'.\n\1')



class GitMarkdownLiaisonListener(sublime_plugin.EventListener):
    @classmethod
    def refresh_settings(cls):
        cls.state_file = sublime.load_settings('GML_state.sublime-settings')
        cls._unmodified_views_hashes = cls.state_file.get('hashes', {})
        cls._unmodified_views_filenames = cls.state_file.get('filenames', {})
        cls._views_filenames = set(cls._unmodified_views_filenames.values())

    @classmethod
    def save_settings(cls):
        cls.state_file.set('hashes', cls._unmodified_views_hashes or {})
        cls.state_file.set('filenames', cls._unmodified_views_filenames or {})
        sublime.save_settings('GML_state.sublime-settings')

    @property
    def unmodified_views_hashes(self):
        '''Handle sublime's tardy loading of settings'''
        if self._unmodified_views_hashes is None:
            self.refresh_settings()
        return self._unmodified_views_hashes

    @property
    def unmodified_views_filenames(self):
        '''Handle sublime's tardy loading of settings'''
        if self._unmodified_views_filenames is None:
            self.refresh_settings()
        return self._unmodified_views_filenames

    @property
    def views_filenames(self):
        '''Handle sublime's tardy loading of settings'''
        if self._views_filenames is None:
            self.refresh_settings()
        return self._views_filenames

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
        any problems, I've erred on the side of never unsetting scratch
        unless I'm sure this plugin set it.'''
        if not gml_active_on_view(view):
            return

        view_id = str(view.id())
        view_fn = view.file_name()
        if view_id not in self.unmodified_views_hashes:
            if view_fn in self.views_filenames:
                self.rename_view(view_fn, view_id)
            else:
                return

        if self.unmodified_views_filenames[view_id] != view_fn:
            self.clear_unmodified(view)
            return

        if self.unmodified_views_hashes[view_id] == hash_buffer(view):
            view.set_scratch(True)
        else:
            view.set_scratch(False)

    def rename_view(self, view_fn, new_view_id):
        '''Create new entries in views dicts using existing hashes'''
        key = reverse_dict_lookup(self.unmodified_views_filenames, view_fn)

        mappings = [
            self.unmodified_views_hashes,
            self.unmodified_views_filenames
        ]
        for mapping in mappings:
            mapping[new_view_id] = mapping[key]
        self.save_settings()

    def clear_unmodified(self, view):
        view_id = str(view.id())
        del self.unmodified_views_hashes[view_id]
        del self.unmodified_views_filenames[view_id]
        self.save_settings()

    def set_unmodified(self, view):
        '''Store the hash of the unmodified view after a save/load'''
        view_id = str(view.id())
        if view.is_scratch() and view_id not in self.unmodified_views_hashes:
            return

        self.unmodified_views_hashes[view_id] = hash_buffer(view)
        self.unmodified_views_filenames[view_id] = view.file_name()
        self.save_settings()

        view.set_scratch(True)


GitMarkdownLiaisonListener.refresh_settings()
