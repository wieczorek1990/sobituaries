from django.http import response


class HttpResponseSeeOther(response.HttpResponseRedirect):
    status_code = 303
