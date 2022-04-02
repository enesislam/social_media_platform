from django.shortcuts import redirect



def if_user_logged(function):
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        else:
            return function(request, *args, **kwargs)
    return wrap