def clone_object_instance(obj, attrs={}, exclude_child_models=[]):
    # Create shallow clone of obj
    clone = obj._meta.model.objects.get(pk=obj.pk)
    clone.pk = None

    # Apply specified attributes to clone
    for key, value in attrs.items():
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
                attrs = {field.remote_field.name: clone}
                children = field.related_model.objects.filter(
                    **{field.remote_field.name: obj}
                )
                for child in children:
                    if child._meta.model_name in exclude_child_models:
                        continue
                    clone_object_instance(child, attrs)
    return clone


def convert_models_choices_to_list(choices):
    """ Returns list from nested model choices """
    return [choice[0] for choice in choices]


def get_list_display_session_options(
    request, model, filter_by="ALL", order_by_field="name", page_size=10
):
    """ Returns list display options from session, or defaults if not yet set """
    return (
        request.session.get(
            f"display_filter_{model._meta.verbose_name.title()}", filter_by
        ),
        request.session.get(
            f"display_order_{model._meta.verbose_name.title()}", order_by_field
        ),
        request.session.get(
            f"display_page_size_{model._meta.verbose_name.title()}", page_size
        ),
    )


def get_list_filter_options(
    filter_by_value,
    filter_by_field,
    filter_by_field_choices,
    filter_by_field_valid_choices,
):
    """ Returns filter labels and values for rendering filter dropdown """
    # print(f"filter_by_value: {filter_by_value}")
    # print(f"filter_by_field: {filter_by_field}")
    # print(f"filter_by_field_choices: {filter_by_field_choices}")
    # print(f"filter_by_field_valid_choices: {filter_by_field_valid_choices}")

    filter_options = {}

    filter_options["field"] = filter_by_field
    filter_options["value"] = filter_by_value

    filter_options["labels"] = [
        {"label": choice[0], "display": choice[1]}
        for choice in filter_by_field_choices
        if (choice[0] in filter_by_field_valid_choices and choice[0] != filter_by_value)
    ]

    if filter_by_value == "ALL":
        filter_options["display_text"] = "None"
    else:
        filter_options["labels"].insert(0, {"label": "ALL", "display": "View All"})
        filter_options["display_text"] = [
            choice[1]
            for choice in filter_by_field_choices
            if choice[0] == filter_by_value
        ][0]
    # print("filter_options:", filter_options)
    return filter_options


def get_page_context_options(model, bulk_create_available=False, edit_via_xlsx=False):
    """ Returns parameters for rendering model templates  """
    options = {
        "model": f"{model._meta.verbose_name.title()}",
        "plural": f"{model._meta.verbose_name_plural.title()}",
        "url_add": f"apps.{model._meta.app_label}:{model._meta.model_name}_add",
        "url_list": f"apps.{model._meta.app_label}:{model._meta.model_name}_list",
        "url_detail": f"apps.{model._meta.app_label}:{model._meta.model_name}_detail",
        "url_edit": f"apps.{model._meta.app_label}:{model._meta.model_name}_edit",
    }
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