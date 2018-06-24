"""All pytest-django fixtures"""

from __future__ import with_statement


import pytest

from pytest_django_mixins.model_watcher import ModelWatcher


@pytest.yield_fixture(scope='function')
def django_model_watcher():
    """
    Watch changes (create, update, delete) of specific model(s), and provide access to every change.

    usecase:

        django_model_watcher.set_watcher(ModelClass)

        django_model_watcher.created[ModelClass] -> list of created instances of ModelClass
        django_model_watcher.updated[ModelClass] -> list of updated instances of ModelClass
        django_model_watcher.deleted[ModelClass] -> list of deleted instances of ModelClass

        django_model_watcher.clean_watchers() -> clear all lists of changes

    WARNING:
    When you set watcher for class ModelClass, you can't use 'update', 'bulk_create' and '_update' methods on
    ModelClass managers. If you try ModelClass.objects.update(name='new_name') you get NotImplementedError exception.
    If you want to use these methods again, you need manually unset watcher: django_model_watcher.unset_watcher(ModelClassg

    :return: ModelWatcher()
    """
    watcher = ModelWatcher()
    yield watcher
    watcher.unset_watchers(*watcher.watched_models)
