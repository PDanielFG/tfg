import csv
from django.http import HttpResponse


def queryset_to_csv_response(queryset, fields, filename="data.csv"):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(fields)  # cabecera

    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field)
            row.append(value)
        writer.writerow(row)

    return response
