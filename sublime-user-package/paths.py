import sublime
import sublime_plugin

import os

class CopyAbsolutePathCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.set_clipboard(self.view.file_name())
        self.view.window().status_message("Copied!")

class CopyRelativePathCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        root = os.path.commonpath([
            self.view.window().folders()[0],
            self.view.file_name()
        ])

        sublime.set_clipboard(os.path.relpath(self.view.file_name(), start = root))
        self.view.window().status_message("Copied!")
