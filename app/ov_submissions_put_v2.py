import json
from datetime import datetime
from dateutil import parser
from django.http import JsonResponse
from app.models import OrPodanieIssues


def check_number(content, key):
    errors = []
    flag = False
    if key in content:

        if type(content[key]) is not int:
            errors.append('not_number')
        else:
            flag = True

    return errors, flag


def check_date(content, key):
    errors = []
    flag = False
    if key in content:

        try:
            date = parser.parse((content[key]))
        except (ValueError, AttributeError, OverflowError):
            errors.append('invalid_range')
            return errors

        if date.year != datetime.now().year:
            errors.append('invalid_range')
        else:
            flag = True

    return errors, flag


def check_string(content, key):
    errors = []
    flag = False
    if key in content:

        if not isinstance(content[key], str):
            errors.append('not_string')
        else:
            flag = True

    return errors, flag


def check_address(pi, cont):
    if 'street' not in cont:
        cont["street"] = pi.street
    if 'postal_code' not in cont:
        cont["postal_code"] = pi.postal_code
    if 'city' not in cont:
        cont["city"] = pi.city
    return cont


def put_submissions_v2(request, path):
    if path.isnumeric():
        try:
            p = OrPodanieIssues.objects.get(id=int(path))

            fields = [  # list of fields required for a successful insert into database
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
                content = json.loads(request.body)  # loads the post body into a dictionary
            except ValueError:
                return JsonResponse({"errors": []}, status=400)

            # check for input parameter errors for each required parameter
            errors = []
            update_flag = False
            for item in fields:
                if item == 'cin':
                    field_errors, flag = check_number(content, item)
                elif item == 'registration_date':
                    field_errors, flag = check_date(content, item)
                else:
                    field_errors, flag = check_string(content, item)

                if field_errors:
                    errors.append({"field": item, "reasons": field_errors})
                if flag:
                    update_flag = True

            if errors:  # unprocessable request
                return JsonResponse({"errors": errors}, status=422)
            if not update_flag:
                return JsonResponse({"errors": "Nebolo zadané ani jedno z polí na aktualizáciu"}, status=422)

            # update and save or podanie issue
            content = check_address(p, content)
            content.update({"address_line": content["street"] + ', ' + content["postal_code"] + ' ' + content["city"]})
            for key in content:
                if key == 'registration_date':
                    p.registration_date = parser.parse(content["registration_date"]).date()
                else:
                    setattr(p, key, content[key])
            p.updated_at = datetime.now()

            obj = {
                'br_court_name': p.br_court_name,
                'kind_name': p.kind_name,
                'cin': p.cin,
                'registration_date': p.registration_date,
                'corporate_body_name': p.corporate_body_name,
                'br_section': p.br_section,
                'br_insertion': p.br_insertion,
                'text': p.text,
                'street': p.street,
                'postal_code': p.postal_code,
                'city': p.city
            }

            p.save()

            # merge parameters with the newly created id and return a succesful insert response
            return JsonResponse({"response": {**{"id": int(path)}, **obj}}, status=201)

        except OrPodanieIssues.DoesNotExist:
            return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404)

    else:
        return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404)
