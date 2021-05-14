# --- DJANGO IMPORTS
from django.db import models


def clone_object_instance(
    *,
    obj: models.Model,
    attrs_to_apply: dict = {},
    exclude_app_labels: list = [],
    exclude_child_models: list = [],
) -> models.Model:
    """

    Create clone of instance, and optionally set new attributes on cloned instance
    Cloned instance relations:
    - many-to-many relations to same objects as original
    - one-to-one and foreign key relations (where original as parent) create new clones of child instances
    - foreign key relations (where original was child) are NOT recreated
    May specifiy apps and/or child models to be excluded from cloning process

    """
    # Create shallow clone of obj
    clone = obj._meta.model.objects.get(pk=obj.pk)
    clone.pk = None

    # Apply specified attributes to clone
    for key, value in attrs_to_apply.items():
        setattr(clone, key, value)

    # Save clone
    clone.save()

    # Follow relations
    fields = clone._meta.get_fields()
    for field in fields:

        # Apply all m2m relations from obj to clone
        if not field.auto_created and field.many_to_many:
            for row in getattr(obj, field.name).all():
                getattr(clone, field.name).add(row)

        # Clone child objs (1:N, 1:1) of original and relate to clone
        if field.auto_created and field.is_relation:
            if field.many_to_many:
                pass
            else:
                attrs_to_apply = {field.remote_field.name: clone}
                children = field.related_model.objects.filter(
                    **{field.remote_field.name: obj}
                )
                for child in children:
                    if child._meta.model_name in exclude_child_models:
                        continue
                    if child._meta.app_label in exclude_app_labels:
                        continue
                    clone_object_instance(
                        obj=child,
                        attrs_to_apply=attrs_to_apply,
                        exclude_child_models=exclude_child_models,
                        exclude_app_labels=exclude_app_labels,
                    )
    return clone


def convert_models_choices_to_list(choices):
    """ Returns list from nested model choices """
    return [choice[0] for choice in choices]


def get_template_context_options(
    model,
    add_available=True,
    edit_available=True,
    bulk_create_available=False,
    edit_via_xlsx=False,
):
    """ Returns parameters for rendering model templates  """
    options = {
        "model": f"{model._meta.verbose_name.title()}",
        "plural": f"{model._meta.verbose_name_plural.title()}",
        "url_list": f"apps.{model._meta.app_label}:{model._meta.model_name}_list",
        "url_detail": f"apps.{model._meta.app_label}:{model._meta.model_name}_detail",
    }

    if add_available:
        options[
            "url_add"
        ] = f"apps.{model._meta.app_label}:{model._meta.model_name}_add"

    if edit_available:
        options[
            "url_edit"
        ] = f"apps.{model._meta.app_label}:{model._meta.model_name}_edit"

    if bulk_create_available:
        options[
            "url_add_bulk"
        ] = f"apps.{model._meta.app_label}:{model._meta.model_name}_add_bulk"

    if edit_via_xlsx:
        options[
            "url_edit_via_xlsx"
        ] = f"apps.{model._meta.app_label}:{model._meta.model_name}_edit_via_xlsx"

    return options


def set_attribute_of_related_objects(parent_obj, attrs={}):
    for link in parent_obj._meta.related_objects:
        if hasattr(parent_obj, link.get_accessor_name()):
            if link.one_to_one:
                object = getattr(parent_obj, link.get_accessor_name())
                for key, value in attrs.items():
                    setattr(object, key, value)
                    object.save()
            else:
                objects = getattr(parent_obj, link.get_accessor_name()).all()
                for object in objects:
                    for key, value in attrs.items():
                        setattr(object, key, value)
                        object.save()