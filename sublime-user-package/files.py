import sublime
import sublime_plugin

import os

class DeleteFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        os.remove(self.view.file_name())
        self.view.close()
