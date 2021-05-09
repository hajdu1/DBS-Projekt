from django.http import JsonResponse, HttpResponse
from app.models import OrPodanieIssues, BulletinIssues, RawIssues


def delete_submissions_v2(path_id):
    if path_id.isnumeric():

        try:
            row = OrPodanieIssues.objects.get(id=int(path_id))

            if OrPodanieIssues.objects.filter(raw_issue_id=row.raw_issue_id).count() == 1:
                if RawIssues.objects.filter(bulletin_issue_id=row.bulletin_issue_id).count() == 1:
                    BulletinIssues.objects.filter(id=row.bulletin_issue_id).delete()
                else:
                    RawIssues.objects.filter(id=row.raw_issue_id).delete()
            else:
                row.delete()

            return HttpResponse('', status=204)

        except OrPodanieIssues.DoesNotExist:
            return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404)

    # the requested id is not a number
    return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404)
