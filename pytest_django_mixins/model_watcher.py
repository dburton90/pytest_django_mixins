from django.db.models import Manager
from django.db.models.base import ModelBase
from django.db.models.manager import ManagerDescriptor
from django.db.models.signals import post_delete, post_save


class ModelWatcher:
    created = None
    deleted = None
    updated = None
    watched_models = None
    NOT_SUPPORTED_METHODS = ['update', 'bulk_create', '_update']

    def __init__(self):
        self._mocked_methods = {}

    def _mock_forbidden_methods(self, model_class):
        """
        This method override all Managers's methods, which does not call pre/post signals:
        - update
        - bulk_create
        - _update
        :param queryset_class:
        """
        mocked_methods = {}
        for manager in self._get_model_managers(model_class):
            mocked_methods[manager.name] = {}
            for method in self.NOT_SUPPORTED_METHODS:

                def not_implemented_error(*args, **kwargs):
                    raise NotImplementedError("You can't access method {} in {} class with {} manager, when you are"
                                              "using ModelWatcherMixin".format(method, model_class, manager.name))

                old_method = getattr(manager, method)
                mocked_methods[manager.name][method] = old_method
                setattr(manager, method, not_implemented_error)
        self._mocked_methods[model_class] = mocked_methods

    def _unmock_forbidden_methods(self, model_class):
        for manager_name, methods in self._mocked_methods.pop(model_class, {}).items():
            manager = getattr(model_class, manager_name)
            for method_name, method in methods.items():
                setattr(manager, method_name, method)

    def _get_model_managers(self, model_class):
        for name, obj in vars(model_class).items():
            if isinstance(obj, Manager):
                yield obj
            elif isinstance(obj, ManagerDescriptor):
                yield getattr(model_class, name)

    def set_watcher(self, model):
        """
        set listeners to model's signals and save all instance of model to 'updated', 'created', 'deleted' lists
        When the watcher is active, you can't use methods like 'update', 'bulk_create', and '_updated' on
        model's managers. It will raise NotImplementedError, because these methods does not trigger signals.

        :param model: Model class
        :return:
        """
        watched_models = self.watched_models or set()
        if model in watched_models:
            return

        created = self.created or {}
        deleted = self.deleted or {}
        updated = self.updated or {}

        created[model] = []
        deleted[model] = []
        updated[model] = []

        def receiver_save(sender, **kwargs):
            if kwargs.get('created'):
                created[model].append(kwargs.get('instance'))
            else:
                updated[model].append(kwargs.get('instance'))

        def receiver_delete(sender, **kwargs):
            deleted[model].append(kwargs.get('instance'))

        post_save.connect(receiver_save, sender=model, weak=False)
        post_delete.connect(receiver_delete, sender=model, weak=False)
        watched_models.add(model)

        setattr(self, 'created', created)
        setattr(self, 'deleted', deleted)
        setattr(self, 'updated', updated)
        setattr(self, 'watched_models', watched_models)
        self._mock_forbidden_methods(model)

    def clean_watchers(self, *models):
        created = self.created or {}
        deleted = self.deleted or {}
        updated = self.updated or {}

        for model in models or created:
            created[model] = []

        for model in models or deleted:
            deleted[model] = []

        for model in models or updated:
            updated[model] = []

        setattr(self, 'created', created)
        setattr(self, 'deleted', deleted)
        setattr(self, 'updated', updated)

    def unset_watchers(self, *models):
        """
        unset signals, and set back Manager's original methods.
        :param models:
        :return:
        """
        watched_models = getattr(self, 'watched_models', set())
        for model in models or watched_models.copy():
            if model in watched_models:
                watched_models.remove(model)
                post_save.disconnect(model)
                post_delete.disconnect(model)
                self._unmock_forbidden_methods(model)

    def updated_count(self, selected_models=None, exclude=None):
        """
        return count of all changes
        :param models:
        :param exclude:
        :return:
        """
        selected_models = self._get_filtered_models(selected_models, exclude)
        return sum((len(self.updated[m]) for m in selected_models))

    def deleted_count(self, selected_models=None, exclude=None):
        selected_models = self._get_filtered_models(selected_models, exclude)
        return sum((len(self.deleted[m]) for m in selected_models))

    def created_count(self, selected_models=None, exclude=None):
        selected_models = self._get_filtered_models(selected_models, exclude)
        return sum((len(self.created[m]) for m in selected_models))

    def _get_filtered_models(self, selected_models, exclude):
        assert not (selected_models and exclude), "you can't set both models and exclude"
        if isinstance(selected_models, ModelBase):
            selected_models = [selected_models]
        if exclude:
            selected_models = (m for m in self.watched_models if m not in exclude)
        elif selected_models is None:
            selected_models = self.watched_models
        return selected_models

    def updated_unique(self, selected_model=None):
        """ :returns list of unique updated instances """
        return list({inst.pk: inst for inst in self.updated[selected_model]}.values())
