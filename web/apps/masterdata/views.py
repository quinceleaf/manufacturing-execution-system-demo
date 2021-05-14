# ––– DJANGO IMPORTS
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import add_message
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    UpdateView,
    TemplateView,
)


# ––– PYTHON UTILITY IMPORTS
from decimal import Decimal as D


# ––– THIRD-PARTY IMPORTS
from admin_auto_filters.views import AutocompleteJsonView
from formtools.wizard.views import SessionWizardView


# ––– APPLICATION IMPORTS
from apps.common import views as common_views, services as common_services
from apps.masterdata import filters, forms, models, selectors, services


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# INDEX
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        return context

    def get(self, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# AUTOCOMPLETES (FOR ADMIN)
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class MaterialFilterSearchView(AutocompleteJsonView):
    def get_queryset(self):
        qs = models.Material.objects.all().order_by("name")
        return qs


class ProductFilterSearchView(AutocompleteJsonView):
    def get_queryset(self):
        qs = models.Product.objects.all().order_by("name")
        return qs


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# BILL OF MATERIALS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def cost_bill_of_materials(bill_of_materials):
    seq = services.generate_cost_sequence(bill_of_materials)
    cost_lookup, cost_table = services.calculate_cost_sequence(seq)
    return cost_lookup, cost_table


class BillOfMaterialsDetailView(LoginRequiredMixin, TemplateView):
    context_object_name = "data"
    model = models.BillOfMaterials
    template_name = "bill_of_materials_detail.html"
    # template_name = "reports/bill_of_materials_pdf_full.html"

    def get_context_data(self, *args, **kwargs):
        context = super(BillOfMaterialsDetailView, self).get_context_data(
            *args, **kwargs
        )

        self.object = self.model.objects.get(id=self.kwargs["pk"])
        context["data"] = self.object
        context["options"] = common_services.get_template_context_options(self.model)

        context["teams"] = models.Team.objects.all()

        # Costing
        if self.object.costs.exists():
            latest_cost = self.object.costs.latest()
            cost_table = json.loads(latest_cost.cost_table)
            cost_drivers = [
                item for item in cost_table[-1]["lines"] if item["cost_driver"]
            ]
            context["cost_drivers"] = sorted(
                cost_drivers, key=lambda i: i["extension"], reverse=True
            )
            context["batch_cost"] = latest_cost.total_cost
            context["cost_table"] = cost_table

        # Scaling
        context["scaling_form"] = forms.BillOfMaterialsScaleForm(
            bill_of_materials=self.object
        )
        context["view_type"] = "standard"

        return context

    def get(self, *args, **kwargs):
        # self.object = None
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = models.BillOfMaterials.objects.get(id=self.kwargs["pk"])
        print(self.request.POST)

        if "delete_form" in self.request.POST:
            object_id = self.request.POST.get("object_to_delete")
            object_type = self.request.POST.get("object_type_to_delete")

            if object_type == "characteristics":
                obj = models.BillOfMaterialsCharacteristics.objects.get(id=object_id)
                obj.delete()

            if object_type == "note":
                obj = models.BillOfMaterialsNote.objects.get(id=object_id)
                obj.delete()

            if object_type == "procedure":
                obj = models.BillOfMaterialsProcedure.objects.get(id=object_id)
                obj.delete()

        if "scaling_form" in self.request.POST:
            print("Storing session")
            services.store_scaling_variables_in_session(self.request)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if "scaling_form" in self.request.POST:
            return reverse_lazy(
                "masterdata:billofmaterials_scale", kwargs={"pk": self.object.id}
            )
        else:
            return reverse_lazy(
                "masterdata:billofmaterials_detail", kwargs={"pk": self.object.id}
            )


class BillOfMaterialsScaleView(LoginRequiredMixin, TemplateView):
    context_object_name = "data"
    model = models.BillOfMaterials
    template_name = "bill_of_materials_scale.html"

    def get_context_data(self, *args, **kwargs):
        context = super(BillOfMaterialsScaleView, self).get_context_data(
            *args, **kwargs
        )

        self.object = self.model.objects.get(id=self.kwargs["pk"])
        context["data"] = self.object
        context["options"] = common_services.get_template_context_options(self.model)

        # retrieve scaling parameters from session
        scale_type = self.request.session.get("scale_type", None)
        if scale_type is None or scale_type not in ["MULTIPLE", "YIELD", "LIMIT"]:
            print("INCORRECT SCALE_TYPE")
            add_message(
                self.request,
                messages.ERROR,
                f"Unable to determine scaling parameters",
            )
            return self.get_success_url()

        # scale by multiple
        if scale_type == "MULTIPLE":
            scaling_factor = self.request.session["scaling_factor"]
            (
                scaled_lines,
                scaled_resources,
                scaled_yield,
            ) = services.scale_bill_of_materials_by_multiple(
                self.object, scaling_factor
            )
            scaling_description = f"Scaled {'up' if D(scaling_factor) > 1 else 'down'} to <strong>{scaling_factor}<em>x</em></strong> standard batch"

        # scale by yield
        if scale_type == "YIELD":
            quantity = D(self.request.session["quantity"])
            unit = models.UnitMeasurement.objects.get(id=self.request.session["unit"])

            (
                scaled_lines,
                scaled_resources,
                scaled_yield,
                scaling_factor,
            ) = services.scale_bill_of_materials_by_yield(self.object, quantity, unit)
            scaling_description = f"Scaled {'up' if scaling_factor > 1 else 'down'} to produce <strong>{quantity} {unit.symbol} {self.object.yields.yield_noun or ''} {self.object.yields.note_each or '' if unit.unit_type == 'EACH' else ''}</strong> ({scaling_factor}<em>x</em> standard batch)"

        # scale by limiting line
        if scale_type == "LIMIT":
            quantity = D(self.request.session["quantity"])
            unit = models.UnitMeasurement.objects.get(id=self.request.session["unit"])
            line = models.BillOfMaterialsLine.objects.get(
                item_id=self.request.session["line"]
            )

            (
                scaled_lines,
                scaled_resources,
                scaled_yield,
                scaling_factor,
            ) = services.scale_bill_of_materials_by_limit(
                self.object, quantity, unit, line
            )
            scaling_description = f"Scaled {'up' if scaling_factor > 1 else 'down'} to use <strong>{round(quantity,0) if line.unit.symbol in ['g', 'ml'] else round(quantity, 3)} {unit.symbol} {line.item.name.title()}</strong> ({scaling_factor}<em>x</em> standard batch)"

        context["scaling_description"] = scaling_description
        context["scaled_lines"] = scaled_lines
        context["scaled_resources"] = scaled_resources
        context["scaled_yield"] = scaled_yield
        context["view_type"] = "scaled"

        return context

    def get(self, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = models.BillOfMaterials.objects.get(id=self.kwargs["pk"])
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:billofmaterials_detail", kwargs={"pk": self.object.id}
        )


def export_bill_of_materials_as_pdf(request, **kwargs):
    base_url = request.build_absolute_uri()

    bill_of_materials_id = kwargs["pk"]
    view_type = kwargs["view_type"]
    report_type = kwargs["report_type"]

    organization = "CaterChain.io"

    # Retrieve scaling parameters from session
    scale_type = request.session.get("scale_type", None)
    scaling_factor = request.session.get("scaling_factor", None)
    quantity = request.session.get("quantity", D(0))

    unit_id = request.session.get("unit", None)
    if unit_id:
        unit = models.UnitMeasurement.objects.get(id=unit_id)
    else:
        unit = None

    item_id = request.session.get("line", None)
    if item_id:
        line = models.BillOfMaterialsLine.objects.get(item_id=item_id)
    else:
        line = None

    response = services.generate_pdf_for_bill_of_materials(
        base_url=base_url,
        bill_of_materials_id=bill_of_materials_id,
        report_type=report_type,
        view_type=view_type,
        organization=organization,
        scale_type=scale_type,
        scaling_factor=scaling_factor,
        quantity=quantity,
        unit=unit,
        line=line,
    )
    # response = pdf_data[0]

    return response


# class BillOfMaterialsPDFStandardView(LoginRequiredMixin, TemplateView):
#     context_object_name = "data"
#     model = models.BillOfMaterials
#     template_name = "bill_of_materials_pdf.html"

#     def get_context_data(self, *args, **kwargs):
#         context = super(BillOfMaterialsPDFView, self).get_context_data(*args, **kwargs)

#         self.object = self.model.objects.get(id=self.kwargs["pk"])
#         context["data"] = self.object
#         context["options"] = common_services.get_template_context_options(self.model)

#         cost_lookup, cost_table = cost_bill_of_materials(self.object)
#         context["batch_cost"] = cost_lookup[self.kwargs["pk"]]
#         context["cost_table"] = cost_table

#         cost_drivers = [item for item in cost_table[-1]["lines"] if item["cost_driver"]]
#         context["cost_drivers"] = sorted(
#             cost_drivers, key=lambda i: i["extension"], reverse=True
#         )

#         context["teams"] = models.Team.objects.all()

#         return context

#     def get(self, *args, **kwargs):
#         # self.object = None
#         return self.render_to_response(self.get_context_data())


class BillOfMaterialsFilterView(common_views.GenericFilteredListView):
    model = models.BillOfMaterials
    # template_name = "bill_of_materials_list.html"
    template_name = "generic/generic_list_with_filter.html"
    add_available = False
    edit_available = False
    bulk_create_available = False
    filterset_class = filters.BillOfMaterialsFilterSimple

    def get_context_data(self, **kwargs):
        context = super(BillOfMaterialsFilterView, self).get_context_data(**kwargs)
        return context


FORMS = [
    # ("base", forms.BillOfMaterialsForm),
    ("lines", forms.BillOfMaterialsLineFormSet),
    ("procedure", forms.BillOfMaterialsProcedureForm),
    ("yields", forms.BillOfMaterialsYieldForm),
    ("resources", forms.BillOfMaterialsResourceForm),
    ("characteristics", forms.BillOfMaterialsCharacteristicsForm),
    ("notes", forms.BillOfMaterialsNoteForm),
]

TEMPLATES = {
    # "base": "wizard/wizard_base.html",
    "lines": "wizard/wizard_lines.html",
    "procedure": "wizard/wizard_procedure.html",
    "yields": "wizard/wizard_yields.html",
    "resources": "wizard/wizard_resources.html",
    "characteristics": "wizard/wizard_characteristics.html",
    "notes": "wizard/wizard_notes.html",
}


class BillOfMaterialsWizardCreateView(LoginRequiredMixin, SessionWizardView):
    form_list = FORMS

    instance = None
    instance_dict = None

    def done(self, form_list, **kwargs):
        form_data = [form.cleaned_data for form in form_list]

        # BillOfMaterials
        # product = models.Product.objects.get(id=self.kwargs["pk"])
        product = selectors.product_detail(product_id=self.kwargs["pk"])
        # self.object = models.BillOfMaterials.objects.create(
        #     product=product,
        #     team=form_data[4]["team"],
        # )
        self.object = services.bill_of_materials_create(
            product=product, team=form_data[4]["team"]
        )

        # BillOfMaterialsLine(s)
        for line in form_data[0]:
            if line["DELETE"]:
                continue
            services.bill_of_materials_line_create(
                sequence=line["sequence"],
                quantity=line["quantity"],
                unit=line["unit"],
                item=line["item"],
                note=line["note"],
                bill_of_materials=self.object,
            )

            # models.BillOfMaterialsLine.objects.create(
            #     sequence=line["sequence"],
            #     quantity=line["quantity"],
            #     unit=line["unit"],
            #     item=line["item"],
            #     note=line["note"],
            #     bill_of_materials=self.object,
            # )

        # BillOfMaterialsProcedure
        if form_data[1]["procedure"] == "" or form_data[1]["procedure"] is None:
            pass
        else:
            # models.BillOfMaterialsProcedure.objects.create(
            #     language=form_data[1]["language"],
            #     procedure=form_data[1]["procedure"],
            #     bill_of_materials=self.object,
            # )
            services.bill_of_materials_procedure_create(
                language=form_data[1]["language"],
                procedure=form_data[1]["procedure"],
                bill_of_materials=self.object,
            )

        # BillOfMaterialsYield(s)
        # models.BillOfMaterialsYield.objects.create(
        #     quantity_weight=form_data[2]["quantity_weight"],
        #     unit_weight=form_data[2]["unit_weight"],
        #     quantity_volume=form_data[2]["quantity_volume"],
        #     unit_volume=form_data[2]["unit_volume"],
        #     quantity_each=form_data[2]["quantity_each"],
        #     unit_each=form_data[2]["unit_each"],
        #     note_each=form_data[2]["note_each"],
        #     scale_multiple_smallest=form_data[2]["scale_multiple_smallest"],
        #     scale_multiple_largest=form_data[2]["scale_multiple_largest"],
        #     bill_of_materials=self.object,
        # )
        services.bill_of_materials_yield_create(
            quantity_weight=form_data[2]["quantity_weight"],
            unit_weight=form_data[2]["unit_weight"],
            quantity_volume=form_data[2]["quantity_volume"],
            unit_volume=form_data[2]["unit_volume"],
            quantity_each=form_data[2]["quantity_each"],
            unit_each=form_data[2]["unit_each"],
            note_each=form_data[2]["note_each"],
            scale_multiple_smallest=form_data[2]["scale_multiple_smallest"],
            scale_multiple_largest=form_data[2]["scale_multiple_largest"],
            bill_of_materials=self.object,
        )

        # BillOfMaterialsResource(s)
        for line in form_data[3]:
            if line["DELETE"]:
                continue
            # models.BillOfMaterialsResource.objects.create(
            #     sequence=line["sequence"],
            #     capacity_required=line["capacity_required"],
            #     resource=line["resource"],
            #     note=line["note"],
            #     bill_of_materials=self.object,
            # )
            services.bill_of_materials_resource_create(
                sequence=line["sequence"],
                capacity_required=line["capacity_required"],
                changeover_required=line.get("changeover_required", 0),
                resource=line["resource"],
                note=line["note"],
                bill_of_materials=self.object,
            )

        # BillOfMaterialsCharacteristics
        # models.BillOfMaterialsCharacteristics.objects.create(
        #     leadtime=form_data[4]["leadtime"],
        #     temperature_preparation=form_data[4]["temperature_preparation"],
        #     temperature_storage=form_data[4]["temperature_storage"],
        #     temperature_service=form_data[4]["temperature_service"],
        #     note_production=form_data[4]["note_production"],
        #     total_active_time=form_data[4]["total_active_time"],
        #     total_inactive_time=form_data[4]["total_inactive_time"],
        #     staff_count=form_data[4]["staff_count"],
        #     note_labor=form_data[4]["note_labor"],
        #     bill_of_materials=self.object,
        # )
        services.bill_of_materials_characteristics_create(
            leadtime=form_data[4]["leadtime"],
            temperature_preparation=form_data[4]["temperature_preparation"],
            temperature_storage=form_data[4]["temperature_storage"],
            temperature_service=form_data[4]["temperature_service"],
            note_production=form_data[4]["note_production"],
            total_active_time=form_data[4]["total_active_time"],
            total_inactive_time=form_data[4]["total_inactive_time"],
            staff_count=form_data[4]["staff_count"],
            note_labor=form_data[4]["note_labor"],
            bill_of_materials=self.object,
        )

        # BillOfMaterialsNote
        # models.BillOfMaterialsNote.objects.create(
        #     note=form_data[5]["note"],
        #     bill_of_materials=self.object,
        # )
        if form_data[5]["note"] == "" or form_data[5]["note"] is None:
            pass
        else:
            services.bill_of_materials_note_create(
                note=form_data[5]["note"],
                bill_of_materials=self.object,
            )

        add_message(
            self.request,
            messages.SUCCESS,
            f"<strong>{self.object}</strong> added",
        )

        return HttpResponseRedirect(
            reverse_lazy(
                "masterdata:billofmaterials_detail", kwargs={"pk": self.object.id}
            )
        )

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        options = {}
        options["parent_object"] = models.Product.objects.get(id=self.kwargs["pk"])
        options["model"] = "Bill of Materials"
        context["options"] = options
        return context

    def get_form_kwargs(self, step, **kwargs):
        kwargs = super(BillOfMaterialsWizardCreateView, self).get_form_kwargs(step)
        if step == "base":
            kwargs["product"] = models.Product.objects.get(id=self.kwargs["pk"])
        return kwargs

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]


def change_bill_of_materials_team(request, **kwargs):

    pk = kwargs.get("pk", None)
    team = kwargs.get("team", None)
    if pk and team:
        recipe = models.BillOfMaterials.objects.get(id=pk)
        team = models.Team.objects.get(slug=team)
        recipe.team = team
        recipe.save()

    referer = request.META.get("HTTP_REFERER")
    return HttpResponseRedirect(referer)


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# BILL OF MATERIALS - COMPONENTS
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

""" For BOM components, parent object (BOM) is added to context options for correct url path rendering """


class BillOfMaterialsCharacteristicsCreateView(LoginRequiredMixin, CreateView):
    model = models.BillOfMaterialsCharacteristics
    form = forms.BillOfMaterialsCharacteristicsForm
    template_name = "bill_of_materials_characteristics_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        options["parent_object"] = models.BillOfMaterials.objects.get(
            id=self.kwargs["pk"]
        )
        options["model"] = "Characteristics"
        options["plural"] = "Characteristics"
        form = self.form()

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        bill_of_materials_id = self.kwargs["pk"]
        self.object.bill_of_materials_id = bill_of_materials_id
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"Characteristics added to {self.bill_of_materials}",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:billofmaterials_detail", kwargs={"pk": self.kwargs["pk"]}
        )


class BillOfMaterialsCharacteristicsUpdateView(LoginRequiredMixin, UpdateView):
    model = models.BillOfMaterialsCharacteristics
    form = forms.BillOfMaterialsCharacteristicsForm
    template_name = "bill_of_materials_characteristics_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])

        """ Override options to get correct options for BOM not child """
        options = common_services.get_template_context_options(self.model)
        options["parent_object"] = self.object.bill_of_materials
        options["model"] = "Characteristics"
        options["plural"] = "Characteristics"

        form = self.form(instance=self.object)
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST, instance=self.object)
        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"Characteristics updated for <strong>{self.object.bill_of_materials}</strong>",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:billofmaterials_detail",
            kwargs={"pk": self.object.bill_of_materials.id},
        )


class BillOfMaterialsLineUpdateView(LoginRequiredMixin, UpdateView):
    model = models.BillOfMaterials
    form_class = forms.BillOfMaterialsLineFormSet
    template_name = "bill_of_materials_lines_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        data = self.object
        options = common_services.get_template_context_options(self.model)
        options["parent_object"] = models.BillOfMaterials.objects.get(
            id=self.kwargs["pk"]
        )
        options["model"] = "Materials"
        options["plural"] = "Materials"

        formset = self.form_class(
            instance=self.object,
            queryset=models.BillOfMaterialsLine.objects.filter(
                bill_of_materials=self.object
            ),
            prefix="lines",
        )
        return self.render_to_response(
            self.get_context_data(
                options=options,
                data=data,
                formset=formset,
            )
        )

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        data = self.object
        options = common_services.get_template_context_options(self.model)

        formset = self.form_class(
            self.request.POST,
            instance=self.object,
            queryset=models.BillOfMaterialsLine.objects.filter(
                bill_of_materials=self.object
            ),
            prefix="lines",
        )
        if formset.is_valid():
            return self.form_valid(options, data, formset)
        else:
            return self.form_invalid(options, data, formset)

    def form_valid(self, options, data, formset):
        self.object = self.model.objects.get(id=self.kwargs["pk"])

        # lines = formset.save(commit=False)
        # for line in lines:
        #     line.bill_of_materials = self.object
        #     line.save()
        # for deleted_line in formset.deleted_objects:
        #     deleted_line.delete()

        lines = formset.save(commit=False)
        for line in lines:
            # line.bill_of_materials = self.object
            services.bill_of_materials_line_update_standardize(
                bill_of_materials_line=line, quantity=line.quantity, unit=line.unit
            )
            # line.save()
        for deleted_line in formset.deleted_objects:
            deleted_line.delete()

        add_message(
            self.request,
            messages.SUCCESS,
            f"Materials updated for <strong>{self.object}</strong>",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, data, formset):
        return self.render_to_response(
            self.get_context_data(
                options=options,
                data=data,
                formset=formset,
            )
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:billofmaterials_detail", kwargs={"pk": self.object.id}
        )


class BillOfMaterialsNoteCreateView(LoginRequiredMixin, CreateView):
    model = models.BillOfMaterialsNote
    form = forms.BillOfMaterialsNoteForm
    template_name = "bill_of_materials_generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        options["parent_object"] = models.BillOfMaterials.objects.get(
            id=self.kwargs["pk"]
        )
        options["model"] = "Note"
        options["plural"] = "Notes"
        form = self.form()

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        bill_of_materials_id = self.kwargs["pk"]
        self.object.bill_of_materials_id = bill_of_materials_id
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"Note added to {self.object.bill_of_materials}",
        )

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:billofmaterials_detail", kwargs={"pk": self.kwargs["pk"]}
        )


class BillOfMaterialsNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = models.BillOfMaterialsNote
    form = forms.BillOfMaterialsNoteForm
    template_name = "bill_of_materials_generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        options["parent_object"] = self.object.bill_of_materials
        options["model"] = "Note"
        options["plural"] = "Notes"
        form = self.form(instance=self.object)

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST, instance=self.object)
        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"Note updated for <strong>{self.object.bill_of_materials}</strong>",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:billofmaterials_detail",
            kwargs={"pk": self.object.bill_of_materials.id},
        )


class BillOfMaterialsProcedureCreateView(LoginRequiredMixin, CreateView):
    model = models.BillOfMaterialsProcedure
    form = forms.BillOfMaterialsProcedureForm
    template_name = "bill_of_materials_procedure_mutate.html"
    # template_name = "bill_of_materials_generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        language = self.kwargs.get("language", None)

        """ Override options to get correct options for BOM not child """
        options = common_services.get_template_context_options(self.model)
        options["parent_object"] = models.BillOfMaterials.objects.get(
            id=self.kwargs["pk"]
        )
        options["model"] = "Procedure"
        options["plural"] = "Procedures"
        form = self.form(instance=self.object, language=language)

        return self.render_to_response(
            self.get_context_data(language=language, options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        language = self.kwargs.get("language", None)
        options = common_services.get_template_context_options(self.model)
        options["parent_object"] = models.BillOfMaterials.objects.get(
            id=self.kwargs["pk"]
        )
        options["model"] = "Procedure"
        options["plural"] = "Procedures"
        form = self.form(self.request.POST, instance=self.object)
        if form.is_valid():
            return self.form_valid(language, options, form)
        else:
            return self.form_invalid(language, options, form)

    def form_valid(self, language, options, form):
        self.object = form.save(commit=False)
        bill_of_materials = models.BillOfMaterials.objects.get(id=self.kwargs["pk"])
        self.object.bill_of_materials = bill_of_materials
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"Procedure ({self.object.get_language_display()}) added to <strong>{self.object.bill_of_materials}</strong>",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, language, options, form):
        return self.render_to_response(
            self.get_context_data(language=language, options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:billofmaterials_detail",
            kwargs={"pk": self.object.bill_of_materials.id},
        )


class BillOfMaterialsProcedureUpdateView(LoginRequiredMixin, UpdateView):
    model = models.BillOfMaterialsProcedure
    form = forms.BillOfMaterialsProcedureForm
    template_name = "bill_of_materials_procedure_mutate.html"
    # template_name = "bill_of_materials_generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        language = self.object.language
        options = common_services.get_template_context_options(self.model)
        options["parent_object"] = self.object.bill_of_materials
        options["model"] = "Procedure"
        options["plural"] = "Procedures"
        form = self.form(instance=self.object, language=language)
        return self.render_to_response(
            self.get_context_data(language=language, options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        language = self.object.language
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST, instance=self.object)
        if form.is_valid():
            return self.form_valid(language, options, form)
        else:
            return self.form_invalid(language, options, form)

    def form_valid(self, language, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"Procedure ({self.object.get_language_display()}) updated for <strong>{self.object.bill_of_materials}</strong>",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, language, options, form):
        return self.render_to_response(
            self.get_context_data(language=language, options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:billofmaterials_detail",
            kwargs={"pk": self.object.bill_of_materials.id},
        )


class BillOfMaterialsResourceUpdateView(LoginRequiredMixin, UpdateView):
    model = models.BillOfMaterials
    form_class = forms.BillOfMaterialsResourceFormSet
    template_name = "bill_of_materials_resources_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        data = self.object
        options = common_services.get_template_context_options(self.model)
        options["parent_object"] = models.BillOfMaterials.objects.get(
            id=self.kwargs["pk"]
        )
        options["model"] = "Resources"
        options["plural"] = "Resources"

        formset = self.form_class(
            instance=self.object,
            queryset=models.BillOfMaterialsResource.objects.filter(
                bill_of_materials=self.object
            ),
            prefix="lines",
        )
        return self.render_to_response(
            self.get_context_data(
                options=options,
                data=data,
                formset=formset,
            )
        )

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        data = self.object
        options = common_services.get_template_context_options(self.model)

        formset = self.form_class(
            self.request.POST,
            instance=self.object,
            queryset=models.BillOfMaterialsResource.objects.filter(
                bill_of_materials=self.object
            ),
            prefix="lines",
        )
        if formset.is_valid():
            return self.form_valid(options, data, formset)
        else:
            return self.form_invalid(options, data, formset)

    def form_valid(self, options, data, formset):
        self.object = self.model.objects.get(id=self.kwargs["pk"])

        lines = formset.save(commit=False)
        for line in lines:
            line.bill_of_materials = self.object
            line.save()
        for deleted_line in formset.deleted_objects:
            deleted_line.delete()

        add_message(
            self.request,
            messages.SUCCESS,
            f"Materials updated for <strong>{self.object}</strong>",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, data, formset):
        return self.render_to_response(
            self.get_context_data(
                options=options,
                data=data,
                formset=formset,
            )
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:billofmaterials_detail", kwargs={"pk": self.object.id}
        )


class BillOfMaterialsYieldCreateView(LoginRequiredMixin, CreateView):
    model = models.BillOfMaterialsYield
    form = forms.BillOfMaterialsYieldForm
    template_name = "bill_of_materials_yields_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        options["parent_object"] = models.BillOfMaterials.objects.get(
            id=self.kwargs["pk"]
        )
        options["model"] = "Yield"
        options["plural"] = "Yields"
        form = self.form(instance=self.object)

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST, instance=self.object)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        bill_of_materials_id = self.kwargs["pk"]
        self.object = form.save(commit=False)
        self.object.bill_of_materials_id = bill_of_materials_id
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"Yield added to <strong>{self.object.bill_of_materials}</strong>",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:billofmaterials_detail",
            kwargs={"pk": self.object.bill_of_materials.id},
        )


class BillOfMaterialsYieldUpdateView(LoginRequiredMixin, UpdateView):
    model = models.BillOfMaterialsYield
    form = forms.BillOfMaterialsYieldForm
    template_name = "bill_of_materials_yields_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        options["parent_object"] = self.object.bill_of_materials
        options["model"] = "Yield"
        options["plural"] = "Yields"
        form = self.form(instance=self.object)

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST, instance=self.object)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"Yield updated for <strong>{self.object.bill_of_materials}</strong>",
        )

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:billofmaterials_detail",
            kwargs={"pk": self.object.bill_of_materials.id},
        )


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MATERIAL
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def load_material_valid_units(request):
    item_id = request.GET.get("item")
    item = models.Item.objects.get(id=item_id)
    units = models.UnitMeasurement.objects.filter(unit_type=item.unit_type)
    return render(
        request,
        "components/dropdown_material_unit_options.html",
        {"units": units},
    )


class MaterialDetailView(LoginRequiredMixin, TemplateView):
    context_object_name = "data"
    model = models.Material
    form = forms.MaterialForm
    template_name = "material_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(MaterialDetailView, self).get_context_data(*args, **kwargs)
        obj = self.model.objects.get(id=self.kwargs["pk"])
        context["data"] = obj
        context["form"] = self.form(instance=obj)
        context["options"] = common_services.get_template_context_options(self.model)

        ###
        related_data = []

        # Assigned cost
        related_data.append(
            {
                "label": "Current Assigned Cost",
                "value": obj.get_assigned_cost(),
            }
        )

        # Characteristics

        # Inventory

        context["related_data"] = related_data
        ###

        return context

    def get(self, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())


class MaterialFilterView(common_views.GenericFilteredListView):
    model = models.Material
    bulk_create_available = True
    filterset_class = filters.MaterialFilterSimple

    def get_context_data(self, **kwargs):
        context = super(MaterialFilterView, self).get_context_data(**kwargs)
        return context


class MaterialCreateView(LoginRequiredMixin, CreateView):
    model = models.Material
    form = forms.MaterialForm
    template_name = "generic/generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form()

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"{self.model._meta.verbose_name.title()} <strong>{self.object}</strong> added",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )


class MaterialBulkCreateView(LoginRequiredMixin, CreateView):
    model = models.Material
    form = forms.MaterialBulkForm
    template_name = "generic/generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form()

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)

        objects_list = form.cleaned_data["name_bulk"].split("\r\n")
        for name in objects_list:
            # object = form.save(commit=False)
            self.object.id = None
            self.object.name = name.strip()
            self.object._state.adding = True
            self.object.save()

        add_message(
            self.request,
            messages.SUCCESS,
            f"{len(objects_list)} {self.model._meta.verbose_name_plural.title()} added",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy("masterdata:material_list")


class MaterialUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Material
    form = forms.MaterialForm
    template_name = "generic/generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        form = self.form(instance=self.object)

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST, instance=self.object)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"{self.model._meta.verbose_name.title()} <strong>{self.object}</strong> updated",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )


class MaterialCostCreateView(LoginRequiredMixin, CreateView):
    model = models.MaterialCost
    form = forms.MaterialCostForm
    template_name = "generic/generic_child_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        parent_object = models.Material.objects.get(id=self.kwargs["pk"])
        options["parent_object"] = parent_object
        form = self.form(material=parent_object)

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.item_id = self.kwargs["pk"]
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"Cost updated for <strong>{self.object.item.name}</strong>",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:material_detail", kwargs={"pk": self.object.item_id}
        )


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PRODUCT
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class ProductDetailView(LoginRequiredMixin, TemplateView):
    context_object_name = "data"
    model = models.Product
    form = forms.ProductForm
    template_name = "product_detail/product_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)

        obj = self.model.objects.get(id=self.kwargs["pk"])

        context["data"] = obj
        context["form"] = self.form(instance=obj)
        context["options"] = common_services.get_template_context_options(self.model)
        context["settings"] = models.Settings.objects.get()

        return context

    def get(self, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = models.Product.objects.get(id=self.kwargs["pk"])
        print(self.request.POST)

        if "delete_form" in self.request.POST:
            product_to_be_deleted = self.object.name
            self.object.delete()

            add_message(
                self.request,
                messages.SUCCESS,
                f"Product <strong>{product_to_be_deleted}</strong> deleted",
            )

        if "archive_form" in self.request.POST:
            self.object.archive = True
            self.object.save()

            add_message(
                self.request,
                messages.SUCCESS,
                f"Product <strong>{self.object.name}</strong> archived",
            )

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("masterdata:product_list")


class ProductFilterView(common_views.GenericFilteredListView):
    model = models.Product
    template_name = "generic/generic_list_with_filter.html"
    bulk_create_available = True
    filterset_class = filters.ProductFilterSimple

    def get_context_data(self, **kwargs):
        context = super(ProductFilterView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return self.model.objects.filter(archive=False)


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = models.Product
    form = forms.ProductForm
    template_name = "generic/generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form()

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"{self.model._meta.verbose_name.title()} <strong>{self.object}</strong> added",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        # override get_success_url as for Product get_absolute_url
        # redirects instead to Material url using Product id, which throws
        # unclear cause but perhaps due to fact that both are proxy models?
        # TODO: resolve Product get_absolute_url
        return reverse_lazy("masterdata:product_detail", kwargs={"pk": self.object.id})


class ProductBulkCreateView(LoginRequiredMixin, CreateView):
    model = models.Product
    form = forms.ProductBulkForm
    template_name = "generic/generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form()

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)

        objects_list = form.cleaned_data["name_bulk"].split("\r\n")
        for name in objects_list:
            # object = form.save(commit=False)
            self.object.id = None
            self.object.name = name.strip()
            self.object._state.adding = True
            self.object.save()

        add_message(
            self.request,
            messages.SUCCESS,
            f"{len(objects_list)} {self.model._meta.verbose_name_plural.title()} added",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        # override get_success_url as for Product get_absolute_url
        # redirects instead to Material url using Product id, which throws
        # unclear cause but perhaps due to fact that both are proxy models?
        # TODO: resolve Product get_absolute_url
        return reverse_lazy("masterdata:product_list")


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Product
    template_name = "generic/generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = models.Product.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        form = forms.ProductForm(instance=self.object)
        print(options)

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = models.Product.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        form = forms.ProductForm(self.request.POST, instance=self.object)
        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"{self.model._meta.verbose_name.title()} <strong>{self.object}</strong> updated",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy("masterdata:product_detail", kwargs={"pk": self.object.id})


@login_required
def duplicate_product(request, **kwargs):
    if request.user.has_perm("Workflow (BOM)"):
        pk = kwargs.get("pk", None)
        if pk:
            product = models.Product.objects.get(id=pk)

        new_product_instance = services.product_duplicate(product=product)

        add_message(
            request,
            messages.SUCCESS,
            f"<strong>{new_product_instance}</strong> created",
        )
        return HttpResponseRedirect(
            reverse("masterdata:product_detail", kwargs={"pk": new_product_instance.id})
        )
    else:
        add_message(
            request,
            messages.ERROR,
            f"Permission denied",
        )
        referer = request.META.get("HTTP_REFERER")
        return HttpResponseRedirect(referer)


@login_required
def generate_product_version(request, **kwargs):

    if request.user.has_perm("Workflow (BOM)"):
        pk = kwargs.get("pk", None)
        if pk:
            bill_of_materials = models.BillOfMaterials.objects.get(id=pk)

        new_bom_object = clone_object_instance(
            bill_of_materials,
            attrs={"version": bill_of_materials.version + 1, "state": "DRAFT"},
        )
        set_attribute_of_related_objects(
            new_bom_object, attrs={"version": bill_of_materials.version + 1}
        )
        bill_of_materials.supersede(by=request.user)

        add_message(
            request,
            messages.SUCCESS,
            f"Bill of Materials <strong>{bill_of_materials.product.name}</strong> version <strong>{new_bom_object.version}</strong> generated",
        )
        return HttpResponseRedirect(
            reverse(
                "masterdata:billofmaterials_detail", kwargs={"pk": new_bom_object.id}
            )
        )
    else:
        add_message(
            request,
            messages.ERROR,
            f"Permission denied",
        )
        referer = request.META.get("HTTP_REFERER")
        return HttpResponseRedirect(referer)


def change_product_status(request, **kwargs):

    status_methods = {
        "DRAFT": "set_draft",
        "AWAITING": "submit_for_approval",
        "APPROVED": "approve",
        "RETURNED": "return_for_revision",
        "SUPERSEDED": "supersede",
        "INACTIVE": "set_inactive",
    }

    pk = kwargs.get("pk", None)
    target_status = kwargs.get("status", None)
    if pk and target_status:
        product = models.Product.objects.get(id=pk)
        prior_status = product.status.get_state_display()

        method = status_methods.get(target_status, None)
        if method and hasattr(product.status, method):
            getattr(product.status, method)(by=request.user)
        product.status.save()

        if target_status == "APPROVED":
            services.generate_bom_tree(root_bom=product.bill_of_materials)

            if product.version != 1:
                # Prior version is now superseded
                prior_version = models.Product.objects.get(
                    version_key=product.version_key,
                    version=product.version - 1,
                )
                prior_version.supersede(by=request.user)
                prior_version.save()

        add_message(
            request,
            messages.SUCCESS,
            f"Status of <strong>{product}</strong> changed to <strong>{product.status.get_state_display()}</strong>",
        )

    referer = request.META.get("HTTP_REFERER")
    return HttpResponseRedirect(referer)


# Characteristics


class ProductCharacteristicsUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Product
    form = forms.ProductCharacteristicsForm
    template_name = "generic/generic_child_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"]).characteristics
        options = common_services.get_template_context_options(self.model)
        options["parent_object"] = models.Product.objects.get(id=self.kwargs["pk"])
        form = self.form(instance=self.object)

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"]).characteristics
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST, instance=self.object)
        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"Characteristics updated for <strong>{self.object}</strong> updated",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:product_detail", kwargs={"pk": self.object.item_id}
        )


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# RESOURCE
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class ResourceDetailView(LoginRequiredMixin, TemplateView):
    context_object_name = "data"
    model = models.Resource
    form = forms.ResourceForm
    template_name = "generic/generic_detail.html"
    # template_name = "materials/material_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ResourceDetailView, self).get_context_data(*args, **kwargs)
        obj = self.model.objects.get(id=self.kwargs["pk"])
        context["data"] = obj
        context["form"] = self.form(instance=obj)
        context["options"] = common_services.get_template_context_options(self.model)
        return context

    def get(self, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())


class ResourceFilterView(common_views.GenericFilteredListView):
    model = models.Resource
    template_name = "generic/generic_list_with_filter.html"
    bulk_create_available = True
    filterset_class = filters.ResourceFilterSimple

    def get_context_data(self, **kwargs):
        context = super(ResourceFilterView, self).get_context_data(**kwargs)
        return context


class ResourceCreateView(LoginRequiredMixin, CreateView):
    model = models.Resource
    form = forms.ResourceForm
    template_name = "generic/generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form()

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"{self.model._meta.verbose_name.title()} <strong>{self.object}</strong> added",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )


class ResourceBulkCreateView(LoginRequiredMixin, CreateView):
    model = models.Resource
    form = forms.ResourceBulkForm
    template_name = "generic/generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form()

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)

        objects_list = form.cleaned_data["name_bulk"].split("\r\n")
        for name in objects_list:
            # object = form.save(commit=False)
            self.object.id = None
            self.object.name = name.strip()
            self.object._state.adding = True
            self.object.save()

        add_message(
            self.request,
            messages.SUCCESS,
            f"{len(objects_list)} {self.model._meta.verbose_name_plural.title()} added",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy("masterdata:resource_list")


class ResourceUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Resource
    form = forms.ResourceForm
    template_name = "generic/generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        form = self.form(instance=self.object)

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST, instance=self.object)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"{self.model._meta.verbose_name.title()} <strong>{self.object}</strong> updated",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# TEAM
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class TeamDetailView(LoginRequiredMixin, TemplateView):
    context_object_name = "data"
    model = models.Team
    form = forms.TeamForm
    template_name = "generic/generic_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(TeamDetailView, self).get_context_data(*args, **kwargs)
        obj = self.model.objects.get(id=self.kwargs["pk"])
        context["data"] = obj
        context["form"] = self.form(instance=obj)
        context["options"] = common_services.get_template_context_options(self.model)

        return context

    def get(self, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())


class TeamFilterView(common_views.GenericFilteredListView):
    model = models.Team
    template_name = "generic/generic_list_with_filter.html"
    bulk_create_available = True
    filterset_class = filters.TeamFilterSimple

    def get_context_data(self, **kwargs):
        context = super(TeamFilterView, self).get_context_data(**kwargs)
        return context


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = models.Team
    form = forms.TeamForm
    template_name = "generic/generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form()

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"{self.model._meta.verbose_name.title()} <strong>{self.object}</strong> added",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )


class TeamBulkCreateView(LoginRequiredMixin, CreateView):
    model = models.Team
    form = forms.TeamBulkForm
    template_name = "generic/generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form()

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)

        objects_list = form.cleaned_data["name_bulk"].split("\r\n")
        for name in objects_list:
            # object = form.save(commit=False)
            self.object.id = None
            self.object.name = name.strip()
            self.object._state.adding = True
            self.object.save()

        add_message(
            self.request,
            messages.SUCCESS,
            f"{len(objects_list)} {self.model._meta.verbose_name_plural.title()} added",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def get_success_url(self):
        return reverse_lazy("masterdata:team_list")


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Team
    form = forms.TeamForm
    template_name = "generic/generic_mutate.html"

    def get(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        form = self.form(instance=self.object)

        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.model.objects.get(id=self.kwargs["pk"])
        options = common_services.get_template_context_options(self.model)
        form = self.form(self.request.POST, instance=self.object)

        if form.is_valid():
            return self.form_valid(options, form)
        else:
            return self.form_invalid(options, form)

    def form_valid(self, options, form):
        self.object = form.save(commit=False)
        self.object.save()
        add_message(
            self.request,
            messages.SUCCESS,
            f"{self.model._meta.verbose_name.title()} <strong>{self.object}</strong> updated",
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, options, form):
        return self.render_to_response(
            self.get_context_data(options=options, form=form)
        )


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# UNIT MEASUREMENT
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class UnitMeasurementDetailView(LoginRequiredMixin, TemplateView):
    context_object_name = "data"
    model = models.UnitMeasurement
    form = forms.UnitMeasurementForm
    template_name = "generic/generic_detail.html"
    edit_available = False
    delete_permitted = False

    def get_context_data(self, *args, **kwargs):
        context = super(UnitMeasurementDetailView, self).get_context_data(
            *args, **kwargs
        )
        obj = self.model.objects.get(id=self.kwargs["pk"])
        context["data"] = obj
        context["form"] = self.form(instance=obj)
        context["options"] = common_services.get_template_context_options(
            self.model, self.edit_available, self.delete_permitted
        )

        return context

    def get(self, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())


class UnitMeasurementFilterView(common_views.GenericFilteredListView):
    model = models.UnitMeasurement
    template_name = "generic/generic_list_with_filter.html"
    add_available = False
    edit_available = False
    delete_permitted = False
    bulk_create_available = False
    advanced_search_available = False
    filterset_class = filters.UnitMeasurementFilterSimple

    def get_context_data(self, **kwargs):
        context = super(UnitMeasurementFilterView, self).get_context_data(**kwargs)
        return context


# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# UTILITY
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


class UtilityListView(LoginRequiredMixin, TemplateView):
    context_object_name = "data"
    template_name = "utility_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UtilityListView, self).get_context_data(*args, **kwargs)
        return context

    def get(self, *args, **kwargs):
        self.object = None
        return self.render_to_response(self.get_context_data())


def handle_uploaded_file(*, file: bin) -> list:
    print("passed file:", file)


class UtilityOfflineUpdateView(LoginRequiredMixin, TemplateView):
    context_object_name = "data"
    template_name = "utility_offline_update.html"
    model_class = {
        "MATERIAL": models.Material,
        "MATERIAL_COSTS": models.MaterialCost,
        "PRODUCT": models.Product,
        "RESOURCE": models.Resource,
    }

    def get_context_data(self, *args, **kwargs):
        context = super(UtilityOfflineUpdateView, self).get_context_data(
            *args, **kwargs
        )
        return context

    def get(self, request, *args, **kwargs):
        export_form = forms.UtilityBulkEditExportForm()
        import_form = forms.UtilityBulkEditImportForm()

        return self.render_to_response(
            self.get_context_data(import_form=import_form, export_form=export_form)
        )

    def post(self, request, *args, **kwargs):
        if "export_form" in self.request.POST:
            action = "export"
            export_form = forms.UtilityBulkEditExportForm(self.request.POST)
            import_form = forms.UtilityBulkEditImportForm()
        else:
            action = "import"
            export_form = forms.UtilityBulkEditExportForm()
            import_form = forms.UtilityBulkEditImportForm(
                self.request.POST, self.request.FILES
            )

        if action == "export" and export_form.is_valid():
            form = export_form
            return self.form_valid(form, action)
        elif action == "import" and import_form.is_valid():
            form = import_form
            return self.form_valid(form, action)
        else:
            return self.form_invalid(import_form=import_form, export_form=export_form)

    def form_valid(self, form, action):
        if action == "export":
            format = form.cleaned_data.get("export_format")
            model = form.cleaned_data.get("export_model")

            if format == "CSV":

                qs = self.model_class[model].objects.all()
                fields = ["id", "name", "category"]
                response = services.export_as_csv(
                    queryset=qs,
                    fields=fields,
                    filename=f"editing-{model}-{timezone.localdate()}",
                )
            if format == "XLSX":

                qs = self.model_class[model].objects.all()
                filename = f"export-{self.model_class[model]._meta.verbose_name_plural.title()}"
                response = services.export_as_xlsx_with_choices_validation(
                    model=self.model_class[model],
                    queryset=qs,
                    fields_to_export=["id", "name", "category", "unit_type"],
                    fields_to_validate=["category", "unit_type"],
                    filename=filename,
                )

            format_display = dict(form.fields["export_format"].choices)[format]
            model_display = dict(form.fields["export_model"].choices)[model]

            add_message(
                self.request,
                messages.SUCCESS,
                f"<strong>{model_display}</strong> exported as <strong>{format_display}</strong> file",
            )

            return response

        if action == "import":
            format = form.cleaned_data.get("import_format")
            format_display = dict(form.fields["import_format"].choices)[format]
            model = form.cleaned_data.get("import_model")
            model_display = dict(form.fields["import_model"].choices)[model]

            if format == "CSV":
                response = services.import_csv(model=self.model_class[model])
            if format == "XLSX":
                data = services.import_xlsx(
                    model=self.model_class[model],
                    file=self.request.FILES["import_file"],
                )

            add_message(
                self.request,
                messages.SUCCESS,
                f"File uploaded and processed",
            )

            self.request.session["bulk_edit_model"] = model
            self.request.session["bulk_edit_data_to_preview"] = data

            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, import_form, export_form):
        return self.render_to_response(
            self.get_context_data(import_form=import_form, export_form=export_form)
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:utility_bulk_edit_confirm_changes",
        )


class UtilityOfflineUpdateConfirmChangesView(LoginRequiredMixin, TemplateView):
    context_object_name = "data"
    template_name = "utility_offline_update_confirm_changes.html"
    model_class = {
        "MATERIAL": models.Material,
        "MATERIAL_COSTS": models.MaterialCost,
        "PRODUCT": models.Product,
        "RESOURCE": models.Resource,
    }

    def get_context_data(self, *args, **kwargs):
        context = super(UtilityOfflineUpdateConfirmChangesView, self).get_context_data(
            *args, **kwargs
        )

        model = self.request.session.get("bulk_edit_model")
        data = self.request.session.get("bulk_edit_data_to_preview")

        context["model"] = self.model_class[model]._meta.verbose_name_plural.title()
        context["total_count"] = (
            len(data["updates"]) + len(data["creates"]) + len(data["no_changes"])
        )
        context["update_count"] = len(data["updates"])
        context["create_count"] = len(data["creates"])
        context["no_change_count"] = len(data["no_changes"])
        context["data"] = data
        return context

    def get(self, request, *args, **kwargs):
        form = forms.UtilityBulkEditConfirmChangesForm()

        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = forms.UtilityBulkEditConfirmChangesForm(self.request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form=form)

    def form_valid(self, form):

        model = self.request.session.get("bulk_edit_model")
        data = self.request.session.get("bulk_edit_data_to_preview")

        # updates
        for obj in data["updates"]:
            instance, created = models.Material.objects.update_or_create(
                id=obj["id"], defaults=obj
            )
            # updated = models.Material.objects.update_or_create(**obj)

        # additions
        for obj in data["creates"]:
            created = models.Material.objects.create(**obj)

        add_message(
            self.request,
            messages.SUCCESS,
            f"{len(data['updates'])} {self.model_class[model]._meta.verbose_name_plural.title()} updated and {len(data['creates'])} {self.model_class[model]._meta.verbose_name_plural.title()} added",
        )

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy("masterdata:index")


class UtilityBulkUpdateCharacteristicsView(common_views.GenericFilteredListView):
    model = models.Material
    template_name = "utility_bulk_update_characteristics.html"
    filterset_class = filters.MaterialCharacteristicsBulkEditFilterAdvanced

    def get_context_data(self, **kwargs):
        context = super(UtilityBulkUpdateCharacteristicsView, self).get_context_data(
            **kwargs
        )

        return context

    def get_queryset(self):
        queryset = models.Material.objects.filter(
            Q(characteristics__contains_crustacea=None)
            | Q(characteristics__contains_dairy=None)
            | Q(characteristics__contains_egg=None)
            | Q(characteristics__contains_fish=None)
            | Q(characteristics__contains_peanut=None)
            | Q(characteristics__contains_sesame=None)
            | Q(characteristics__contains_soy=None)
            | Q(characteristics__contains_treenut=None)
            | Q(characteristics__contains_wheat=None)
            | Q(characteristics__contains_alcohol=None)
            | Q(characteristics__contains_gelatin=None)
            | Q(characteristics__contains_honey=None)
            | Q(characteristics__contains_meat=None)
        )
        return queryset

    # def get(self, request, *args, **kwargs):
    #     action_form = forms.UtilityBulkUpdateCharacteristicsForm()
    #     object_list = self.get_queryset()
    #     return self.render_to_response(
    #         self.get_context_data(action_form=action_form, object_list=object_list)
    #     )

    # def post(self, request, *args, **kwargs):

    #     action_form = forms.UtilityBulkUpdateCharacteristicsForm(self.request.POST)

    #     if action_form.is_valid():
    #         form = action_form
    #         return self.form_valid(form)
    #     else:
    #         return self.form_invalid(form=form)

    # def form_valid(self, form):
    #     pass

    #     add_message(
    #         self.request,
    #         messages.SUCCESS,
    #         f"<strong>{model_display}</strong> exported as <strong>{format_display}</strong> file",
    #     )

    #     return HttpResponseRedirect(self.get_success_url())

    # def form_invalid(self, form):
    #     return self.render_to_response(self.get_context_data(form=form))

    # def get_success_url(self):
    #     return reverse_lazy(
    #         "masterdata:utility_bulk_edit_characteristics_confirm_changes",
    #     )


class UtilityBulkUpdateCharacteristicsConfirmChangesView(
    LoginRequiredMixin, TemplateView
):
    context_object_name = "data"
    template_name = "utility_bulk_editing.html"
    model_class = {
        "MATERIAL": models.Material,
        "MATERIAL_COSTS": models.MaterialCost,
        "PRODUCT": models.Product,
        "RESOURCE": models.Resource,
    }

    def get_context_data(self, *args, **kwargs):
        context = super(
            UtilityBulkUpdateCharacteristicsConfirmChangesView, self
        ).get_context_data(*args, **kwargs)
        return context

    def get(self, request, *args, **kwargs):
        export_form = forms.UtilityBulkEditExportForm()
        import_form = forms.UtilityBulkEditImportForm()

        return self.render_to_response(
            self.get_context_data(import_form=import_form, export_form=export_form)
        )

    def post(self, request, *args, **kwargs):
        if "export_form" in self.request.POST:
            action = "export"
            export_form = forms.UtilityBulkEditExportForm(self.request.POST)
            import_form = forms.UtilityBulkEditImportForm()
        else:
            action = "import"
            export_form = forms.UtilityBulkEditExportForm()
            import_form = forms.UtilityBulkEditImportForm(
                self.request.POST, self.request.FILES
            )

        if action == "export" and export_form.is_valid():
            form = export_form
            return self.form_valid(form, action)
        elif action == "import" and import_form.is_valid():
            form = import_form
            return self.form_valid(form, action)
        else:
            return self.form_invalid(import_form=import_form, export_form=export_form)

    def form_valid(self, form, action):
        if action == "export":
            format = form.cleaned_data.get("export_format")
            model = form.cleaned_data.get("export_model")

            if format == "CSV":

                qs = self.model_class[model].objects.all()
                fields = ["id", "name", "category"]
                response = services.export_as_csv(
                    queryset=qs,
                    fields=fields,
                    filename=f"editing-{model}-{timezone.localdate()}",
                )
            if format == "XLSX":

                qs = self.model_class[model].objects.all()
                filename = f"export-{self.model_class[model]._meta.verbose_name_plural.title()}"
                response = services.export_as_xlsx_with_choices_validation(
                    model=self.model_class[model],
                    queryset=qs,
                    fields_to_export=["id", "name", "category", "unit_type"],
                    fields_to_validate=["category", "unit_type"],
                    filename=filename,
                )

            format_display = dict(form.fields["export_format"].choices)[format]
            model_display = dict(form.fields["export_model"].choices)[model]

            add_message(
                self.request,
                messages.SUCCESS,
                f"<strong>{model_display}</strong> exported as <strong>{format_display}</strong> file",
            )

            return response

        if action == "import":
            format = form.cleaned_data.get("import_format")
            format_display = dict(form.fields["import_format"].choices)[format]
            model = form.cleaned_data.get("import_model")
            model_display = dict(form.fields["import_model"].choices)[model]

            if format == "CSV":
                response = services.import_csv(model=self.model_class[model])
            if format == "XLSX":
                data = services.import_xlsx(
                    model=self.model_class[model],
                    file=self.request.FILES["import_file"],
                )

            add_message(
                self.request,
                messages.SUCCESS,
                f"File uploaded and processed",
            )

            self.request.session["bulk_edit_model"] = model
            self.request.session["bulk_edit_data_to_preview"] = data

            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, import_form, export_form):
        return self.render_to_response(
            self.get_context_data(import_form=import_form, export_form=export_form)
        )

    def get_success_url(self):
        return reverse_lazy(
            "masterdata:utility_bulk_edit_confirm_changes",
        )
