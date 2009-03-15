#!/usr/bin/python -S
#
# Copyright (C) 2009 Andy Chu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Demonstration of how to write verifiers.

Since the tests are in Python, we of course can just import the Python
implementation of json-template to test it.

This uses the command line tool python/expand.py to demonstrate one way to test implementations in other languages.
"""

__author__ = 'Andy Chu'

import subprocess
import sys

from pan.core import json
from pan.core import records
from pan.test import testy


class ExternalVerifier(testy.StandardVerifier):
  """Verifies template behavior in an external process."""

  def __init__(self, script_path):
    testy.StandardVerifier.__init__(self)
    self.script_path = script_path

  def _RunScript(self, template_str, dictionary):
    data = json.dumps(dictionary)
    # sys.executable necessary on Windows
    argv = [sys.executable, self.script_path, template_str, data]
    print argv
    p = subprocess.Popen(
        argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True)  # for Windows too
    stdout = p.stdout.read()
    stderr = p.stderr.read()
    p.stdout.close()
    p.stderr.close()
    exit_code = p.wait()

    return records.Record(stderr=stderr, stdout=stdout, exit_code=exit_code)

  @staticmethod
  def _MakeTemplateStr(template_def):
    template_str = template_def.args[0]
    options = template_def.kwargs
    
    if options:
      lines = []
      for k, v in options.iteritems():
        lines.append('%s %s\n' % (k.replace('_', '-'), v))
      header = ''.join(lines) + '\n'
    else:
      header = ''

    return header + template_str

  def Expansion(
      self, template_def, dictionary, expected, ignore_whitespace=False):
    """
    Args:
      template_def: ClassDef instance that defines a Template.
    """
    template_str = self._MakeTemplateStr(template_def)
    result = self._RunScript(template_str, dictionary)

    self.Equal(result.exit_code, 0, 'stderr: %r' % result.stderr)
    self.LongStringsEqual(
        result.stdout, expected, ignore_whitespace=ignore_whitespace)

  def EvaluationError(self, exception, template_def, data_dict):
    template_str = self._MakeTemplateStr(template_def)
    result = self._RunScript(template_str, data_dict)

    self.Equal(result.exit_code, 1)
    print exception.__name__
    self.In(exception.__name__, result.stderr)

  def CompilationError(self, exception, *args, **kwargs):
    template_def = testy.ClassDef(*args, **kwargs)
    template_str = self._MakeTemplateStr(template_def)
    result = self._RunScript(template_str, {})
    self.Equal(result.exit_code, 1)
    print exception.__name__
    self.In(exception.__name__, result.stderr)