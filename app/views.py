from django.http import JsonResponse                        # used to return responses in the application/json format
from django.db import connection                            # using cursor to execute SQL queries
from django.views.decorators.csrf import csrf_exempt

from app.companies_get import get_companies
from app.ov_submissions_get import get_submissions
from app.ov_submissions_post import post_submissions
from app.ov_submissions_delete import delete_submissions

from app.companies_get_v2 import get_companies_v2
from app.ov_submissions_get_v2 import get_submissions_v2
from app.ov_submissions_post_v2 import post_submissions_v2
from app.ov_submissions_delete_v2 import delete_submissions_v2
from app.ov_submissions_put_v2 import put_submissions_v2


# returns the servers uptime
def health(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime;")
        result = cursor.fetchone()
    # replace() gets rid of the unnecessary comma after the day field introduced by django response formatting
    return JsonResponse({"pgsql": {"uptime": str(result[0]).replace(',', '')}})


def unknown(request):
    return JsonResponse({"errors": "Unsupported request method " + request.method}, status=403)


# crossroad function that determines the request method and sends the request to its respective handling function
@csrf_exempt
def submissions(request, path):
    method = request.method
    if method == 'GET':
        return get_submissions(request)
    elif method == 'POST':
        return post_submissions(request)
    elif method == 'DELETE':
        return delete_submissions(path)
    else:
        return unknown(request)  # unwanted behavior


@csrf_exempt
def companies(request):
    if request.method == 'GET':
        return get_companies(request)
    else:
        return unknown(request)


@csrf_exempt
def submissions_v2(request, path):
    method = request.method
    if method == 'GET':
        return get_submissions_v2(request, path)
    elif method == 'POST':
        return post_submissions_v2(request)
    elif method == 'DELETE':
        return delete_submissions_v2(path)
    elif method == 'PUT':
        return put_submissions_v2(request, path)
    else:
        return unknown(request)


@csrf_exempt
def companies_v2(request):
    if request.method == 'GET':
        return get_companies_v2(request)
    else:
        return unknown(request)
