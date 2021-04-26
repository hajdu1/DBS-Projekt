from math import ceil  # used to round up the number of pages
from django.db import connection  # used to execute sql commands
from django.http import JsonResponse  # used to return responses in json format
from app.checks_helpers import *


def get_companies(request):
    # allowed column names
    columns = [
        'cin',
        'name',
        'br_section',
        'address_line',
        'last_update',
        'or_podanie_issues_count',
        'znizenie_imania_issues_count',
        'likvidator_issues_count',
        'konkurz_vyrovnanie_issues_count',
        'konkurz_restrukturalizacia_actors_count'
    ]

    # page number and per page values are checked
    page = get_page(request.GET.get('page'))
    per_page = get_per_page(request.GET.get('per_page'))

    # parameters for the complete SQL query executed via cursor
    cursor_params = {'limit': get_per_page(request.GET.get('per_page')),

                     'offset': (page - 1) * per_page,

                     'order': get_order_companies(request.GET.get('order_by'), request.GET.get('order_type'), columns),

                     'substring_query': get_substring_query(request.GET.get('query')),

                     'last_update_gte': get_date(request.GET.get('last_update_gte')),

                     'last_update_lte': get_date(request.GET.get('last_update_lte'))
                     }

    # prepares the WHERE statement
    where_params = []
    if cursor_params['last_update_gte'] is not None:
        where_params.append('last_update >= %(last_update_gte)s')
    if cursor_params['last_update_lte'] is not None:
        where_params.append('last_update <= %(last_update_lte)s')
    if cursor_params['substring_query'] is not None:
        where_params.append('(name ILIKE %(substring_query)s OR address_line ILIKE %(substring_query)s)')
    where_clause = construct_where_clause(where_params)

    # builds the "items" SQL query to be executed
    sql = """SELECT ov.companies.cin, name, br_section, address_line, last_update, 
    COALESCE(QTY1.q1, 0) as or_podanie_issues_count, COALESCE(QTY2.q2, 0) as znizenie_imania_issues_count, 
    COALESCE(QTY3.q3, 0) as likvidator_issues_count, COALESCE(QTY4.q4, 0) as konkurz_vyrovnanie_issues_count,
    COALESCE(QTY5.q5, 0) as konkurz_restrukturalizacia_actors_count FROM ov.companies
    LEFT JOIN
        (SELECT COUNT(ov.or_podanie_issues.company_id) AS q1, ov.or_podanie_issues.company_id 
        FROM ov.or_podanie_issues GROUP BY ov.or_podanie_issues.company_id) AS QTY1
    ON ov.companies.cin = QTY1.company_id
    LEFT JOIN
        (SELECT COUNT(ov.znizenie_imania_issues.company_id) AS q2, ov.znizenie_imania_issues.company_id 
        FROM ov.znizenie_imania_issues GROUP BY ov.znizenie_imania_issues.company_id) AS QTY2
    ON ov.companies.cin = QTY2.company_id
    LEFT JOIN
        (SELECT COUNT(ov.likvidator_issues.company_id) AS q3, ov.likvidator_issues.company_id 
        FROM ov.likvidator_issues GROUP BY ov.likvidator_issues.company_id) AS QTY3
    ON ov.companies.cin = QTY3.company_id
    LEFT JOIN
        (SELECT COUNT(ov.konkurz_vyrovnanie_issues.company_id) AS q4, ov.konkurz_vyrovnanie_issues.company_id 
        FROM ov.konkurz_vyrovnanie_issues GROUP BY ov.konkurz_vyrovnanie_issues.company_id) AS QTY4
    ON ov.companies.cin = QTY4.company_id
    LEFT JOIN
        (SELECT COUNT(ov.konkurz_restrukturalizacia_actors.company_id) AS q5, 
        ov.konkurz_restrukturalizacia_actors.company_id 
        FROM ov.konkurz_restrukturalizacia_actors GROUP BY ov.konkurz_restrukturalizacia_actors.company_id) AS QTY5
    ON ov.companies.cin = QTY5.company_id"""
    sql += where_clause + cursor_params['order']
    sql += """ OFFSET %(offset)s LIMIT %(limit)s;"""

    # execution part of the pre-built "items" SQL query
    objects = []  # items will be returned in this list
    with connection.cursor() as cursor:
        cursor.execute(sql, cursor_params)
        result = cursor.fetchone()
        while result:
            objects.append(dict(zip(columns, result)))  # zip pairs column names to their respective values using lists
            result = cursor.fetchone()

    # builds and executes the "metadata" SQL query
    sql = """SELECT COUNT(*) FROM ov.companies """ + where_clause + """;"""
    with connection.cursor() as cursor:
        cursor.execute(sql, cursor_params)
        count = cursor.fetchone()[0]
        metadata = {'page': page,
                    'per_page': per_page,
                    'pages': ceil((float(count) / per_page)),
                    'total': count
                    }

    return JsonResponse({"items": objects, "metadata": metadata})
