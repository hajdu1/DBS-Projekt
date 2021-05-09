import json
from datetime import datetime
from dateutil import parser
from django.db.models import Max
from django.http import JsonResponse
from app.ov_submissions_post import check_number, check_date, check_string
from app.models import BulletinIssues, RawIssues, OrPodanieIssues


def post_submissions_v2(request):
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
    for item in fields:
        if item == 'cin':
            field_errors = check_number(content, item)
        elif item == 'registration_date':
            field_errors = check_date(content, item)
        else:
            field_errors = check_string(content, item)

        if field_errors:
            errors.append({"field": item, "reasons": field_errors})

    if errors:  # unprocessable request
        return JsonResponse({"errors": errors}, status=422)

    # insert into database
    content.update({  # adds the address line and placeholder value for unknown fields
        "unknown": "-",
        "address_line": content["street"] + ', ' + content["postal_code"] + ' ' + content["city"]})

    # create and save bulletin issue
    b_issue_number = BulletinIssues.objects.filter(year=datetime.now().year).aggregate(Max('number'))["number__max"] + 1
    b = BulletinIssues(year=datetime.now().year, number=b_issue_number, published_at=datetime.now(),
                       created_at=datetime.now(), updated_at=datetime.now())
    b.save()
    # create and save raw issue
    r = RawIssues(bulletin_issue_id=b.id, file_name=content["unknown"], content=content["unknown"],
                  created_at=datetime.now(), updated_at=datetime.now())
    r.save()
    # create and save or podanie issue
    content["registration_date"] = parser.parse(content["registration_date"]).date()
    p = OrPodanieIssues(bulletin_issue_id=b.id, raw_issue_id=r.id, br_mark=content["unknown"],
                        br_court_code=content["unknown"], br_court_name=content["br_court_name"],
                        kind_code=content["unknown"], kind_name=content["kind_name"], cin=content["cin"],
                        registration_date=content["registration_date"],
                        corporate_body_name=content["corporate_body_name"], br_section=content["br_section"],
                        br_insertion=content["br_insertion"], text=content["text"], created_at=datetime.now(),
                        updated_at=datetime.now(), address_line=content["address_line"], street=content["street"],
                        postal_code=content["postal_code"], city=content["city"])
    p.save()

    # delete parameters and values that are not supposed to be displayed in the response
    for key in content.copy():
        if key not in fields:
            content.pop(key)

    # merge parameters with the newly created id and return a succesful insert response
    return JsonResponse({"response": {**{"id": p.id}, **content}}, status=201)
