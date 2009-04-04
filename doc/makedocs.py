#!/usr/bin/python -S
"""
makedocs.py
"""

__author__ = 'Andy Chu'


import glob
import os
import shutil
import sys
import subprocess

if __name__ == '__main__':
  sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), '..'))

from python import jsontemplate
from pan.core import json


def BlogPosts(directory):
  assert directory.endswith('/')

  introducing_dict = {
      'example1':
      open('test-cases/testTableExample-01.html').read(),
      }
  
  posts = []
  for filename in glob.glob(directory + '*.html.jsont'):
    title = filename[len(directory):-len('.html.jsont')].replace('-', ' ')
    outfilename = filename[:-len('.jsont')]
    if 'Introducing' in title:
      dictionary = introducing_dict
    else:
      dictionary = {}
    posts.append(dict(
        filename=filename, title=title, outfilename=outfilename,
        dictionary=dictionary))
  return posts


def main(argv):

  # For now, leave off '-l' 'documentation', 
  argv = ['./jsontemplate_test.py', '-d', 'test-cases']
  subprocess.call(argv)

  shutil.copy('test-cases/testTableExample-01.js.html', 'doc/')

  for post in BlogPosts('doc/'):

    body = jsontemplate.FromFile(
        open(post['filename'])).expand(post['dictionary'])

    dictionary = {
        'title': post['title'],
        'body': body,
        }

    body = jsontemplate.FromFile(
        open('doc/html.jsont')).expand(dictionary)

    open(post['outfilename'], 'w').write(body)

  # Required epydoc to be installed
  # Don't show private variables, and don't assume the docstrings have epydoc
  # markup.
  argv = [
      'epydoc', 'python/jsontemplate.py', '--html', '-v',
      '--docformat=plaintext', '--no-private', '--include-log', '--no-frames',
      '--name', 'JSON Template',
      '-o', 'epydoc']
  subprocess.call(argv)

  print 'Docs generated in epydoc/ and test-cases/ -- now rsync it'


if __name__ == '__main__':
  sys.exit(main(sys.argv))
