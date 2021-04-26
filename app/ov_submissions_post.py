import json                                 # used to check if a date is in the iso format
from datetime import datetime               # used to round up the number of pages
from django.db import connection            # used to execute sql commands
from django.http import JsonResponse        # used to return responses in json format


# chcecks for errors in a numeric field from post body
def check_number(content, key):
    errors = []
    if key in content:

        if type(content[key]) is not int:
            errors.append('not_number')

    else:
        errors.append('required')

    return errors


# chcecks for errors in an iso date field from post body
def check_date(content, key):
    errors = []
    if key in content:

        try:
            date = datetime.fromisoformat(content[key].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            errors.append('invalid_range')
            return errors

        if date.year != datetime.now().year:
            errors.append('invalid_range')

    else:
        errors.append('required')

    return errors


# chcecks for errors in a strings field from post body
def check_string(content, key):
    errors = []
    if key in content:

        if not isinstance(content[key], str):
            errors.append('not_string')

    else:
        errors.append('required')

    return errors


# function responsible for handling POST requests at /ov/submissions
def post_submissions(request):
    fields = [                                      # list of fields required for a successful insert into database
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
    try:
        content = json.loads(request.body)                              # loads the post body into a dictionary
    except ValueError:
        return JsonResponse({"errors": []}, status=400)

    # check for input parameter errors for each required parameter
    errors = []
    for item in fields:
        if item == 'cin':
            field_errors = check_number(content, item)
        elif item == 'registration_date':
            field_errors = check_date(content, item)
        else:
            field_errors = check_string(content, item)

        if field_errors:
            errors.append({"field": item, "reasons": field_errors})

    if errors:      # unprocessable request
        return JsonResponse({"errors": errors}, status=422)

    # insert into database
    content.update({        # adds the address line and placeholder value for unknown fields
        "unknown": "-",
        "address_line": content["street"] + ', ' + content["postal_code"] + ' ' + content["city"]})

    # sql to insert the new bulletin issue row
    insert_bulletin = """INSERT INTO ov.bulletin_issues(id, year, number, published_at, created_at, updated_at)
        VALUES (default, %(year)s, (SELECT max(number) FROM ov.bulletin_issues WHERE year = %(year)s) + 1,
        current_date, current_timestamp, current_timestamp) RETURNING id;"""
    # sql to insert the new raw issue row
    insert_raw = """INSERT INTO ov.raw_issues(id, bulletin_issue_id, file_name, content, created_at, updated_at)
        VALUES (default, %(bulletin_issue_id)s, %(unknown)s, %(unknown)s, current_timestamp, current_timestamp) 
        RETURNING id;"""
    # sql to insert the new or podanie issue row
    insert_podanie = """INSERT INTO ov.or_podanie_issues(id, bulletin_issue_id, raw_issue_id, br_mark,
        br_court_code, br_court_name, kind_code, kind_name, cin, registration_date, corporate_body_name, br_section,
        br_insertion, text, created_at, updated_at, address_line, street, postal_code, city) VALUES (default, 
        %(bulletin_issue_id)s, %(raw_issue_id)s, %(unknown)s, %(unknown)s, %(br_court_name)s, %(unknown)s,
        %(kind_name)s, %(cin)s, %(registration_date)s, %(corporate_body_name)s, %(br_section)s, %(br_insertion)s,
        %(text)s, current_timestamp, current_timestamp, %(address_line)s, %(street)s, %(postal_code)s, %(city)s)
        RETURNING id"""

    with connection.cursor() as cursor:
        # create bulletin issue
        cursor.execute(insert_bulletin, {"year": datetime.now().year})
        bulletin_id = cursor.fetchone()[0]

        # create raw issue
        cursor.execute(insert_raw, {"unknown": "-", "bulletin_issue_id": bulletin_id})
        raw_id = cursor.fetchone()[0]

        # adds the new raw id and bulletin id to the parameter dictionary
        content.update({"bulletin_issue_id": bulletin_id, "raw_issue_id": raw_id})

        # create or_podanie_issue
        cursor.execute(insert_podanie, content)
        created_id = cursor.fetchone()[0]

        for key in content.copy():  # delete parameters and values that are not supposed to be displayed in the response
            if key not in fields:
                content.pop(key)

    # merge parameters with the newly created id and return a succesful insert response
    return JsonResponse({"response": {**{"id": created_id}, **content}}, status=201)
