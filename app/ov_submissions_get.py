from math import ceil  # used to round up the number of pages
from django.db import connection  # used to execute sql commands
from django.http import JsonResponse  # used to return responses in json format
from app.checks_helpers import *


# function responsible for handling GET requests at /ov/submissions
def get_submissions(request):
    # allowed column names
    columns = [
        'id',
        'br_court_name',
        'kind_name',
        'cin',
        'registration_date',
        'corporate_body_name',
        'br_section',
        'br_insertion',
        'text',
        'street',
        'postal_code',
        'city'
    ]

    # page number and per page values are checked
    page = get_page(request.GET.get('page'))
    per_page = get_per_page(request.GET.get('per_page'))

    # parameters for the complete SQL query executed via cursor
    cursor_params = {'limit': get_per_page(request.GET.get('per_page')),

                     'offset': (page - 1) * per_page,

                     'order': get_order_by_sumbissions(request.GET.get('order_by'), columns)
                              + ' ' + get_order_type_submissions(request.GET.get('order_type')),

                     'query': get_query(request.GET.get('query')),

                     'substring_query': get_substring_query(request.GET.get('query')),

                     'date_gte': correct_date(request.GET.get('registration_date_gte')),

                     'date_lte': correct_date(request.GET.get('registration_date_lte'))
                     }

    # prepares the WHERE statement
    where_params = []
    if cursor_params['date_gte'] is not None:
        where_params.append('registration_date >= %(date_gte)s')
    if cursor_params['date_lte'] is not None:
        where_params.append('registration_date <= %(date_lte)s')
    if cursor_params['query'] is not None:
        where_params.append('(corporate_body_name ILIKE %(substring_query)s OR CAST (cin AS VARCHAR) ILIKE'
                            ' %(query)s OR city ILIKE %(substring_query)s)')
    where_clause = construct_where_clause(where_params)

    # builds the "items" SQL query to be executed
    sql = """SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name, 
    br_section, br_insertion, text, street, postal_code, city FROM ov.or_podanie_issues"""
    sql += where_clause
    sql += """ ORDER BY """ + cursor_params['order'] + """ OFFSET %(offset)s LIMIT %(limit)s;"""

    # execution part of the pre-built "items" SQL query
    objects = []  # items will be returned in this list
    with connection.cursor() as cursor:
        cursor.execute(sql, cursor_params)
        result = cursor.fetchone()
        while result:
            objects.append(dict(zip(columns, result)))  # zip pairs column names to their respective values using lists
            result = cursor.fetchone()

    # builds and executes the "metadata" SQL query
    sql = """SELECT COUNT(*) FROM ov.or_podanie_issues """ + where_clause + """;"""
    with connection.cursor() as cursor:
        cursor.execute(sql, cursor_params)
        count = cursor.fetchone()[0]
        metadata = {'page': page,
                    'per_page': per_page,
                    'pages': ceil((float(count) / per_page)),
                    'total': count
                    }

    # returns the final response containing search results and metadata in json format
    return JsonResponse({"items": objects, "metadata": metadata})
