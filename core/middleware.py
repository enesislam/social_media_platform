class UserLoggedMiddleWare:
    def __init__(self,get_response) -> None:
        self.get_response = get_response

    def __call__(self,request):
        return self.get_response(request)