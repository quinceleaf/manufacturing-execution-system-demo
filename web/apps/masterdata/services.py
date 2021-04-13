# TODO: material_calculate_cost_cumulative()
# TODO: material_calculate_cost_direct()
# TODO: material_calculate_cost_exp()
# TODO: material_calculate_cost_ma3()
# TODO: material_calculate_cost_ma5()
# TODO: material_calculate_cost_ma7()
# TODO: material_calculate_cost_naive()


# TODO: product_calculate_cost_cumulative()
# TODO: product_calculate_cost_direct()
# TODO: product_calculate_cost_exp()
# TODO: product_calculate_cost_ma3()
# TODO: product_calculate_cost_ma5()
# TODO: product_calculate_cost_ma7()
# TODO: product_calculate_cost_naive()


from django.db.models import Model, QuerySet
from django.http import HttpResponse

from collections import deque
import csv
import datetime
import datetime as dt
import decimal
from decimal import Decimal as D
import json
from openpyxl import load_workbook, Workbook
from openpyxl.utils import absolute_coordinate, quote_sheetname
from openpyxl.worksheet.cell_range import CellRange
from openpyxl.worksheet.datavalidation import DataValidation
from tempfile import NamedTemporaryFile
from typing import Tuple

from apps.masterdata import models, selectors
from apps.common.converters import DecimalEncoder
from apps.common.services import clone_object_instance



# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# CONVERSION
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


STANDARD_UNIT_TYPES = ["WEIGHT", "VOLUME", "EACH"]

STANDARD_UNITS = {"WEIGHT": "lb", "VOLUME": "fl oz", "EACH": "each"}

CONVERSION_DICT = {
    # VOLUMES
    "c,c": "1.00000000",
    "c,fl oz": "8.00000000",
    "c,gal": "0.03125000",
    "c,L": "0.24",
    "c,ml": "239.999808000154",
    "c,pt": "0.50000000",
    "c,qt": "0.12500000",
    "c,Tbsp": "16.00000000",
    "c,tsp": "48.00000000",
    "fl oz,c": "0.12500000",
    "fl oz,fl oz": "1.00000000",
    "fl oz,gal": "0.00781250",
    "fl oz,L": "0.0295735",
    "fl oz,ml": "29.5735494174011",
    "fl oz,pt": "0.06250000",
    "fl oz,qt": "0.03125000",
    "fl oz,Tbsp": "2.00000000",
    "fl oz,tsp": "6.00000000",
    "gal,c": "32.00000000",
    "gal,fl oz": "128.00000000",
    "gal,gal": "1.00000000",
    "gal,L": "3.78541",
    "gal,ml": "3785.41253425798",
    "gal,pt": "8.00000000",
    "gal,qt": "4.00000000",
    "gal,Tbsp": "256.00000000",
    "gal,tsp": "768.00000000",
    "L,c": "4.16666666666667",
    "L,fl oz": "33.8140565032884",
    "L,gal": "0.264172176857989",
    "L,L": "1",
    "L,L": "1",
    "L,ml": "0.001",
    "L,ml": "1000",
    "L,pt": "2.11337853145553",
    "L,qt": "1.05668814913674",
    "L,Tbsp": "67.6278843292666",
    "L,tsp": "202.884201812973",
    "ml,c": "0.00416667",
    "ml,fl oz": "0.033814",
    "ml,gal": "0.000264172",
    "ml,L": "0.001",
    "ml,L": "1000",
    "ml,ml": "1",
    "ml,ml": "1",
    "ml,pt": "0.00211338",
    "ml,qt": "0.00105669",
    "ml,Tbsp": "0.067628",
    "ml,tsp": "0.202884",
    "pt,c": "2.00000000",
    "pt,fl oz": "16.00000000",
    "pt,gal": "0.12500000",
    "pt,L": "0.473176",
    "pt,ml": "473.17567119969",
    "pt,pt": "1.00000000",
    "pt,qt": "0.50000000",
    "pt,Tbsp": "32.00000000",
    "pt,tsp": "96.00000000",
    "qt,c": "8.00000000",
    "qt,fl oz": "32.00000000",
    "qt,gal": "0.25000000",
    "qt,L": "0.946353",
    "qt,ml": "946.351342399379",
    "qt,pt": "2.00000000",
    "qt,qt": "1.00000000",
    "qt,Tbsp": "64.00000000",
    "qt,tsp": "192.00000000",
    "Tbsp,c": "0.0625",
    "Tbsp,fl oz": "0.5",
    "Tbsp,gal": "0.00390625",
    "Tbsp,L": "0.0147868",
    "Tbsp,ml": "14.7867747087005",
    "Tbsp,pt": "0.03125",
    "Tbsp,qt": "0.015625",
    "Tbsp,Tbsp": "1",
    "Tbsp,tsp": "3",
    "tsp,c": "0.020833333",
    "tsp,fl oz": "0.166666667",
    "tsp,gal": "0.001302083",
    "tsp,L": "0.00492892",
    "tsp,ml": "4.92892490290018",
    "tsp,pt": "0.010416667",
    "tsp,qt": "0.005208333",
    "tsp,Tbsp": "0.333333333",
    "tsp,tsp": "1",
    # WEIGHTS
    "kg,kg": "1",
    "kg,g": "1000",
    "kg,lb": "2.202643172",
    "kg,oz": "35.24229075",
    "g,kg": "0.001",
    "g,g": "1",
    "g,lb": "0.002202643",
    "g,oz": "0.035242291",
    "lb,kg": "0.454",
    "lb,g": "454",
    "lb,lb": "1",
    "lb,oz": "16",
    "oz,kg": "0.028375",
    "oz,g": "28.375",
    "oz,lb": "0.0625",
    "oz,oz": "1",
}

""" Units are grouped by their system and type, then ordered from smallest to largest """
""" Ladder is referenced to determine the appropriate unit to attempt to convert to for display """
UNIT_LADDER = {
    "METRIC_WEIGHT": ["g", "kg"],
    "METRIC_VOLUME": ["ml", "L"],
    "US_WEIGHT": ["oz", "lb"],
    "US_VOLUME": ["tsp", "Tbsp", "fl oz", "c", "pt", "qt", "gal"],
}


def convert_units(quantity, input_unit_symbol, output_unit_symbol):
    evaluate = f"{input_unit_symbol},{output_unit_symbol}"
    ratio = CONVERSION_DICT[evaluate]
    output_quantity = k = D(ratio) * D(quantity)
    return D(output_quantity).quantize(D("0.001"))


def standardize_units(
    *, quantity: decimal.Decimal, unit: models.UnitMeasurement
) -> Tuple[decimal.Decimal, models.UnitMeasurement]:
    """ given a quantity & unit for a measurement, convert to the unit specified as standard by user for that unit_type """
    if unit.unit_type not in STANDARD_UNIT_TYPES:
        return (quantity, unit)

    if unit.unit_type == "EACH":
        standardized_quantity = quantity
        standardized_unit = models.UnitMeasurement.objects.get(symbol="ea")
    else:
        if unit.unit_type == "WEIGHT":
            # check for default set by tenant
            if models.Settings.default_unit_weight:
                standardized_unit = models.Settings.default_unit_weight
                # else default to lbs
                standardized_unit = models.UnitMeasurement.objects.get(symbol="lb")
        else:
            # check for default set by tenant
            if models.Settings.default_unit_volume:
                standardized_unit = models.Settings.default_unit_volume
                # else default to fl oz
                standardized_unit = models.UnitMeasurement.objects.get(symbol="fl oz")
        standardized_quantity = convert_units(
            D(quantity),
            unit.symbol,
            standardized_unit.symbol,
        )

    return (standardized_quantity, standardized_unit)


def adjust_units_for_display(quantity, unit):
    """
    Scales quantities/units as appropriate for more convenient measurement
    so that a scaled BOM doesn't present a line specifying 160 tsp of item, for example

    if unit_type == EACHES: continue, non-applicable

    for WEIGHT and VOLUME, have metric and US customary ladders
    lookup which a unit belongs to, then scale it up/down ladder
    """
    from apps.masterdata.models import UnitMeasurement

    """ return immediately if not a scalable unit type """
    SCALABLE_UNITS = ["WEIGHT", "VOLUME"]
    if unit.unit_type not in SCALABLE_UNITS:
        return quantity, unit

    """ return immediately if not unit included in the ladders """
    if unit.symbol not in UNIT_LADDER.get(f"{unit.unit_system}_{unit.unit_type}", None):
        return quantity, unit

    ladder_branch = UNIT_LADDER[f"{unit.unit_system}_{unit.unit_type}"]
    current_quantity = D(quantity)
    current_unit = unit
    seeking = True

    """ success condition:
    if current_unit.display_quantity_smallest <=current_quantity <= current_unit.display_quantity_largest
    """

    while seeking:

        if (
            current_unit.display_quantity_smallest
            <= current_quantity
            <= current_unit.display_quantity_largest
        ):
            """ success condition met """
            break

        current_rank = ladder_branch.index(current_unit.symbol)

        if (
            current_quantity > current_unit.display_quantity_largest
            and current_rank != len(ladder_branch) - 1
        ):
            output_unit_symbol = ladder_branch[current_rank + 1]
        elif (
            current_quantity < current_unit.display_quantity_smallest
            and current_rank != 0
        ):
            output_unit_symbol = ladder_branch[current_rank - 1]
        else:
            return round(current_quantity, 3), current_unit

        current_quantity = convert_units(
            current_quantity, current_unit.symbol, output_unit_symbol
        )
        current_unit = UnitMeasurement.objects.get(symbol=output_unit_symbol)

    return round(current_quantity, 3), current_unit



# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# MATERIAL
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


# def material_get_assigned_cost(*, material: models.Material) -> str:
#     if self.costs.exists():
#         if self.unit_type == "WEIGHT":
#             return f"{self.costs.latest().unit_cost_weight}"
#         elif self.unit_type == "VOLUME":
#             return f"{self.costs.latest().unit_cost_volume}"
#         elif self.unit_type == "EACH":
#             return f"{self.costs.latest().unit_cost_each}"
#         else:
#             return f"{D(0.00)}"
#     else:
#         return "No costs entered yet"


def import_xlsx(
    *,
    model: Model,
    file: bin,
) -> dict:
    wb = load_workbook(filename=file.file)
    ws = wb.active

    # parse xlsx
    row_count = ws.max_row
    column_count = ws.max_column

    header = [cell.value for cell in ws[1]]

    objects = []
    for row in list(ws.rows)[1:]:
        temp = {}
        for key, cell in zip(header, row):
            temp[key] = cell.value
        objects.append(temp)

    # compare with database
    updates = []
    creates = []
    no_changes = []

    for item in objects:
        if item["id"] is None:
            creates.append(item)
        else:
            qs = model.objects.all()
            if qs.filter(**item).exists():
                no_changes.append(item)
            else:
                updates.append(item)

    data = {"updates": updates, "creates": creates, "no_changes": no_changes}

    return data


def export_as_xlsx_with_choices_validation(
    *,
    model: Model,
    queryset: QuerySet,
    fields_to_export: list,
    fields_to_validate: list,
    filename: str = "default",
) -> HttpResponse:
    DATA_ROW_RANGE = (2, 1048576)  # upper bound of rows in XLSX document

    # check that fields_to_validate is subset of fields_to_export
    if not set(fields_to_validate).issubset(set(fields_to_export)):
        return

    # define workbook
    wb = Workbook()

    # define data sheet
    data_sheet = wb.active
    data_sheet.title = model._meta.verbose_name_plural.title()

    # define columns and write header row
    columns = fields_to_export
    # columns = [
    #     model._meta.get_field(field_name).verbose_name
    #     for field_name in fields_to_export
    # ]
    row_number = 1
    for column_number, column_title in enumerate(columns, 1):
        cell = data_sheet.cell(row=row_number, column=column_number)
        cell.value = column_title

    # for each item in queryset, write row
    for obj in queryset:
        row_number += 1
        row = [getattr(obj, field_name) for field_name in fields_to_export]

        for column_number, cell_value in enumerate(row, 1):
            cell = data_sheet.cell(row=row_number, column=column_number)
            cell.value = cell_value

    # as user will be editing/adding to this sheet and uploading later,
    # apply validation to fields with choices defined

    # create sheet to hold values to validate against
    validation_sheet = wb.create_sheet(title=f"Validation - DO NOT MODIFY")
    max_row = 1

    cell = validation_sheet.cell(row=max_row, column=1)
    cell.value = "DO NOT MODIFY THIS SHEET"
    max_row += 1
    cell = validation_sheet.cell(row=max_row, column=1)
    cell.value = " "
    max_row += 1

    for field in fields_to_validate:

        # define columns in data sheet to apply validation to for this field
        field_column = fields_to_export.index(field) + 1
        cells_to_validate_range = CellRange(
            min_col=field_column,
            min_row=DATA_ROW_RANGE[0],
            max_col=field_column,
            max_row=DATA_ROW_RANGE[1],
        )

        # choices = [choice[0] for choice in model._meta.get_field(field).choices]
        # for each item in choices, write row on validation_sheet
        field_value_column_number = 1
        display_value_column_number = 2

        cell = validation_sheet.cell(row=max_row, column=field_value_column_number)
        cell.value = f"{model._meta.get_field(field).verbose_name}"
        max_row += 1

        initial_row_for_current_field = max_row
        max_row_for_current_field = max_row

        for choice in model._meta.get_field(field).choices:
            # choice field value
            cell = validation_sheet.cell(
                row=max_row_for_current_field, column=field_value_column_number
            )
            cell.value = choice[0]
            # choice display value
            cell = validation_sheet.cell(
                row=max_row_for_current_field, column=display_value_column_number
            )
            cell.value = choice[1]
            max_row_for_current_field += 1
            max_row += 1

        cell = validation_sheet.cell(row=max_row + 1, column=field_value_column_number)
        cell.value = f" "
        max_row += 1

        valid_values_range = CellRange(
            min_col=field_value_column_number,
            min_row=initial_row_for_current_field,
            max_col=field_value_column_number,
            max_row=max_row_for_current_field - 1,
        )
        valid_values_range_absolute = absolute_coordinate(valid_values_range.coord)

        dv = DataValidation(
            type="list",
            formula1=f"{quote_sheetname(validation_sheet.title)}!{valid_values_range_absolute}",
            allow_blank=True,
            error="Your entry is not an permitted choice",
            errorTitle="Invalid Entry",
        )
        dv.add(cells_to_validate_range)
        data_sheet.add_data_validation(dv)

    wb.active = data_sheet
    validation_sheet.protection.sheet = True
    validation_sheet.protection.enable()

    # wb.save(filename)

    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        stream = tmp.read()

    response = HttpResponse(
        content=stream,
        content_type="application/ms-excel",
    )
    response[
        "Content-Disposition"
    ] = f'attachment; filename={filename}-{dt.datetime.now().strftime("%Y%m%d%H%M")}.xlsx'

    return response


# def export_as_xlsx_with_choices_validation(
#     *,
#     model: Model,
#     queryset: QuerySet,
#     fields_to_export: list,
#     fields_to_validate: list,
#     filename: str = "default",
# ) -> HttpResponse:
#     DATA_ROW_RANGE = (2, 1048576)  # upper bound of rows in XLSX document

#     # check that fields_to_validate is subset of fields_to_export
#     if set(fields_to_validate).issubset(set(fields_to_export)):
#         pass
#     else:
#         return

#     # define workbook
#     wb = Workbook()

#     # define data sheet
#     data_sheet = wb.active
#     data_sheet.title = model._meta.verbose_name_plural.title()

#     # define columns and write header row
#     columns = [
#         model._meta.get_field(field_name).verbose_name
#         for field_name in fields_to_export
#     ]
#     row_number = 1
#     for column_number, column_title in enumerate(columns, 1):
#         cell = data_sheet.cell(row=row_number, column=column_number)
#         cell.value = column_title

#     # for each item in queryset, write row
#     for obj in queryset:
#         row_number += 1
#         row = [getattr(obj, field_name) for field_name in fields_to_export]

#         for column_number, cell_value in enumerate(row, 1):
#             cell = data_sheet.cell(row=row_number, column=column_number)
#             cell.value = cell_value

#     # as user will be editing/adding to this sheet and uploading later,
#     # apply validation to fields with choices defined
#     for field in fields_to_validate:

#         # define columns in data sheet to apply validation to for this field
#         field_column = fields_to_export.index(field) + 1

#         cells_to_validate_range = CellRange(
#             min_col=field_column,
#             min_row=DATA_ROW_RANGE[0],
#             max_col=field_column,
#             max_row=DATA_ROW_RANGE[1],
#         )

#         # create sheet to hold values to validate against
#         validation_sheet = wb.create_sheet(title=f"Validation {field}")
#         validation_sheet_name = f"Validation {field}"

#         choices = [choice[0] for choice in model._meta.get_field(field).choices]

#         # for each item in choices, write row on validation_sheet
#         cell = validation_sheet.cell(row=1, column=1)
#         cell.value = "DO NOT MODIFY THIS SHEET"

#         validation_row_number = 2
#         column_number = 1
#         for choice in choices:
#             cell = validation_sheet.cell(
#                 row=validation_row_number, column=column_number
#             )
#             cell.value = choice
#             validation_row_number += 1

#         valid_values_range = CellRange(
#             min_col=column_number,
#             min_row=2,
#             max_col=column_number,
#             max_row=validation_row_number,
#         )
#         valid_values_range_absolute = absolute_coordinate(valid_values_range.coord)

#         dv = DataValidation(
#             type="list",
#             formula1=f"{quote_sheetname(validation_sheet_name)}!{valid_values_range_absolute}",
#             allow_blank=True,
#             error="Your entry is not an permitted choice",
#             errorTitle="Invalid Entry",
#         )
#         dv.add(cells_to_validate_range)
#         data_sheet.add_data_validation(dv)

#     wb.save(filename)
#     return




def export_as_csv(
    *, queryset: QuerySet, fields: list, filename: str = "default"
) -> HttpResponse:
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename={}.csv".format(filename)
    writer = csv.writer(response)

    writer.writerow(fields)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in fields])

    return response


def export_as_xlsx(
    *, queryset: QuerySet[models.Material], fields_to_export: list, filename: str
) -> HttpResponse:
    pass


def export_as_pdf(
    *, queryset: QuerySet[models.Material], fields_to_export: list, filename: str
) -> HttpResponse:
    pass


def import_as_csv(
    *, queryset: QuerySet[models.Material], fields_to_export: list, filename: str
) -> HttpResponse:
    pass


def import_as_xlsx(
    *, queryset: QuerySet[models.Material], fields_to_export: list, filename: str
) -> HttpResponse:
    pass



# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# PRODUCT
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––



def product_flatten_BOM_version_history(*, product: models.Product) -> None:
    """ For use when duplicating products. New product should retain only most recent approved BOM, or draft BOM if only BOM available """
    """ Since ostensibly duplicating to make edits, new product BOM will begin in DRAFT state to permit editing """

    # if no BOMs, return
    if product.bills_of_materials.count() == 0:
        return

    # if single BOM, set as DRAFT and retain
    if product.bills_of_materials.count() == 1:
        bom = (
            product.bills_of_materials.get()
        )  # retrieves regardless of state, unlike get_bill_of_materials()
        bom.state = "DRAFT"
        bom.save()
        return

    # if multiple BOMs, keep latest approved, set as DRAFT and discard others
    if product.bills_of_materials.count() > 1:
        bom = product.get_bill_of_materials()
        bom.version = 1
        bom.state = "DRAFT"
        bom.save()

        discards = product.bills_of_materials.exclude(id=bom.id)
        discards.delete()
        return


def product_duplicate(*, product: models.Product) -> models.Product:
    """
    Duplicate product and selected relations
    (BillOfMaterials, ProductCredenceAttribute).
    DO NOT duplicate OrderLines (Sales)
    """

    product_dupl = clone_object_instance(
        obj=product, exclude_child_models=["orderline"]
    )

    # product_dupl = product
    # product_dupl.id = None
    product_dupl.name = f"{product.name} DUPLICATE"
    product_dupl.save()

    # for bill_of_materials in product_dupl.bill_of_materials.all():

    # # Follow relations
    # fields = product_dupl._meta.get_fields()
    # for field in fields:

    #     # Clone child objs (1:N, 1:1) of original and relate to product_dupl
    #     if field.auto_created and field.is_relation:
    #         if field.many_to_many:
    #             pass
    #         else:
    #             attrs = {field.remote_field.name: product_dupl}
    #             children = field.related_model.objects.filter(
    #                 **{field.remote_field.name: obj}
    #             )
    #             for child in children:
    #                 product_dupl_object_instance(child, attrs)
    # return product_dupl

    product_flatten_BOM_version_history(product=product_dupl)

    return product_dupl



# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# RESOURCE
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––



# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# TEAM
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


