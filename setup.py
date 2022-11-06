#!/usr/bin/env python

from setuptools import setup

if __name__ == "__main__":
    setup(
      # name='disposable_email',
      # version='0.0.5',
      install_requires=[
        'python-guerrillamail',
        'mailslurp_client',
        'rich',
        'polling'
        'dropbox_utils'
      ]
    )