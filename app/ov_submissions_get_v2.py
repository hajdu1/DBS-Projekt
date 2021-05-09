from math import ceil  # used to round up the number of pages
from django.db.models.functions import Cast
from django.http import JsonResponse  # used to return responses in json format
from app.checks_helpers import *
from django.db.models import *
from app.models import OrPodanieIssues


# function responsible for handling GET requests at v2/ov/submissions
def get_submissions_v2(request, path):
    if path.isnumeric():
        # submissions/id
        try:
            qs = OrPodanieIssues.objects.get(id=int(path))
            obj = {
                'id': qs.id,
                'br_court_name': qs.br_court_name,
                'kind_name': qs.kind_name,
                'cin': qs.cin,
                'registration_date': qs.registration_date,
                'corporate_body_name': qs.corporate_body_name,
                'br_section': qs.br_section,
                'br_insertion': qs.br_insertion,
                'text': qs.text,
                'street': qs.street,
                'postal_code': qs.postal_code,
                'city': qs.city
            }
        except OrPodanieIssues.DoesNotExist:
            return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404)
        return JsonResponse({"response": obj})

    else:
        # submissions with filters, paging, etc.
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

        page = get_page(request.GET.get('page'))
        per_page = get_per_page(request.GET.get('per_page'))

        items_from = (page - 1) * per_page
        items_to = items_from + per_page

        query_params = {
                        'order': get_order_submissions_v2(request.GET.get('order_by'),
                                                          request.GET.get('order_type'), columns),

                        'query': request.GET.get('query'),

                        'date_gte': correct_date(request.GET.get('registration_date_gte')),

                        'date_lte': correct_date(request.GET.get('registration_date_lte'))
                        }

        qs = OrPodanieIssues.objects

        if query_params['date_gte'] is not None:
            qs = qs.filter(registration_date__gte=query_params['date_gte'].date())
        if query_params['date_lte'] is not None:
            qs = qs.filter(registration_date__lte=query_params['date_lte'].date())
        if query_params['query'] is not None:
            if query_params['query'].isnumeric():
                qs = qs.filter(
                    Q(corporate_body_name__icontains=query_params['query']) |
                    Q(city__icontains=query_params['query']) |
                    Q(cin__exact=int(query_params['query'])))
            else:
                qs = qs.annotate(str_cin=Cast('cin', CharField())).filter(
                    Q(corporate_body_name__icontains=query_params['query']) |
                    Q(city__icontains=query_params['query']))

        if query_params['order'] in ['id', '-id']:
            qs = qs.order_by(query_params['order'])
        elif query_params['order'][0] == '-':
            qs = qs.order_by(F(query_params['order'][1:]).desc(nulls_last=True))
        else:
            qs = qs.order_by(F(query_params['order']).asc(nulls_last=True))

        objects = []
        for row in qs[items_from:items_to]:
            objects.append({
                'id': row.id,
                'br_court_name': row.br_court_name,
                'kind_name': row.kind_name,
                'cin': row.cin,
                'registration_date': row.registration_date,
                'corporate_body_name': row.corporate_body_name,
                'br_section': row.br_section,
                'br_insertion': row.br_insertion,
                'text': row.text,
                'street': row.street,
                'postal_code': row.postal_code,
                'city': row.city
            })

        count = qs.count()
        metadata = {'page': page,
                    'per_page': per_page,
                    'pages': ceil((float(count) / per_page)),
                    'total': count
                    }

        # returns the final response containing search results and metadata in json format
        return JsonResponse({"items": objects, "metadata": metadata})
