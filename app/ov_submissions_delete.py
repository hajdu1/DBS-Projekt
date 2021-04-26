from django.db import connection                        # using cursor to execute SQL queries
from django.http import HttpResponse, JsonResponse      # used to return responses in http and json format


# function responsible for handling DELETE requests at /ov/submissions
def delete_submissions(path_id):

    if path_id.isnumeric():

        with connection.cursor() as cursor:
            cursor.execute("""SELECT raw_issue_id, bulletin_issue_id FROM ov.or_podanie_issues WHERE id = %s""",
                           [int(path_id)])
            foreign_id = cursor.fetchone()

            if foreign_id:                          # if given row exists, parse its raw_issue_id and bulletin_issue_id
                podanie_id = int(path_id)
                raw_id = foreign_id[0]
                bulletin_id = foreign_id[1]

                cursor.execute("""SELECT COUNT(*) FROM ov.or_podanie_issues WHERE raw_issue_id = %s;""",
                               [raw_id])
                references = cursor.fetchone()[0]       # counts how many rows reference the same raw issue

                if references == 1:
                    cursor.execute("""SELECT COUNT(*) FROM ov.raw_issues WHERE bulletin_issue_id = %s""",
                                   [bulletin_id])
                    references = cursor.fetchone()[0]   # counts how many rows reference the same bulletin issue

                    if references == 1:
                        cursor.execute("""DELETE FROM ov.bulletin_issues WHERE id = %s""", [bulletin_id])
                    else:
                        cursor.execute("""DELETE FROM ov.raw_issues WHERE id = %s""", [raw_id])

                else:
                    cursor.execute("""DELETE FROM ov.or_podanie_issues WHERE id = %s""", [podanie_id])

                return HttpResponse('', status=204)
    # the requested id is not a number or does not exist in the database
    return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404)
