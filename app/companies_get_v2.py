from math import ceil
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.db.models import Q, OuterRef, Subquery, Count, F
from app.models import Companies, OrPodanieIssues, ZnizenieImaniaIssues, LikvidatorIssues, KonkurzVyrovnanieIssues, \
    KonkurzRestrukturalizaciaActors
from app.checks_helpers import *


def get_companies_v2(request):
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

    page = get_page(request.GET.get('page'))
    per_page = get_per_page(request.GET.get('per_page'))

    items_from = (page - 1) * per_page
    items_to = items_from + per_page

    query_params = {
        'order': get_order_companies_v2(request.GET.get('order_by'),
                                        request.GET.get('order_type'), columns),

        'query': request.GET.get('query'),

        'last_update_gte': correct_date(request.GET.get('last_update_gte')),

        'last_update_lte': correct_date(request.GET.get('last_update_lte'))
    }

    qs = Companies.objects.all()

    if query_params['last_update_gte'] is not None:
        qs = qs.filter(last_update__gte=query_params['last_update_gte'])
    if query_params['last_update_lte'] is not None:
        qs = qs.filter(last_update__lte=query_params['last_update_lte'])
    if query_params['query'] is not None:
        qs = qs.filter(Q(name__icontains=query_params['query']) | Q(address_line__icontains=query_params['query']))
    # add count fields via subqueries
    qs = qs.annotate(or_podanie_issues_count=Coalesce(Subquery(OrPodanieIssues.objects.filter(
        company_id=OuterRef('cin')).values('company_id').annotate(count=Count('company_id')).values('count')), 0))
    qs = qs.annotate(znizenie_imania_issues_count=Coalesce(Subquery(ZnizenieImaniaIssues.objects.filter(
        company_id=OuterRef('cin')).values('company_id').annotate(count=Count('company_id')).values('count')), 0))
    qs = qs.annotate(likvidator_issues_count=Coalesce(Subquery(LikvidatorIssues.objects.filter(
        company_id=OuterRef('cin')).values('company_id').annotate(count=Count('company_id')).values('count')), 0))
    qs = qs.annotate(konkurz_vyrovnanie_issues_count=Coalesce(Subquery(KonkurzVyrovnanieIssues.objects.filter(
        company_id=OuterRef('cin')).values('company_id').annotate(count=Count('company_id')).values('count')), 0))
    qs = qs.annotate(konkurz_restrukturalizacia_actors_count=Coalesce(Subquery(
        KonkurzRestrukturalizaciaActors.objects.filter(company_id=OuterRef('cin')).values('company_id').annotate(
            count=Count('company_id')).values('count')), 0))

    if query_params['order'] is not None:
        if query_params['order'] in ['cin', '-cin']:
            qs = qs.order_by(query_params['order'])
        elif query_params['order'][0] == '-':
            qs = qs.order_by(F(query_params['order'][1:]).desc(nulls_last=True))
        else:
            qs = qs.order_by(F(query_params['order']).asc(nulls_last=True))

    objects = []
    for row in qs[items_from:items_to]:
        objects.append({
            'cin': row.cin,
            'name': row.name,
            'br_section': row.br_section,
            'address_line': row.address_line,
            'last_update': row.last_update,
            'or_podanie_issues_count': row.or_podanie_issues_count,
            'znizenie_imania_issues_count': row.znizenie_imania_issues_count,
            'likvidator_issues_count': row.likvidator_issues_count,
            'konkurz_vyrovnanie_issues_count': row.konkurz_vyrovnanie_issues_count,
            'konkurz_restrukturalizacia_actors_count': row.konkurz_restrukturalizacia_actors_count
        })

    count = qs.count()
    metadata = {'page': page,
                'per_page': per_page,
                'pages': ceil((float(count) / per_page)),
                'total': count
                }

    return JsonResponse({"items": objects, "metadata": metadata})
