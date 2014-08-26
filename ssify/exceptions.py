class SsifyError(BaseException):
    pass


class SsifyWarning(Warning):
    pass


class UndeclaredSsiVarsError(SsifyError):
    def __init__(self, request, ssi_vars):
        super(UndeclaredSsiVarsError, self).__init__(request, ssi_vars)

    def __str__(self):
        request = self.args[0]
        view = request.resolver_match.func
        return "The view '%s.%s' at '%s' is marked as `ssi_included`, "\
            "but it uses ssi variables not declared in `get_ssi_vars` "\
            "argument: %s. " % (
                view.__module__, view.__name__, request.path,
                repr(self.args[1]))


class UnusedSsiVarsWarning(SsifyWarning):
    def __init__(self, request, ssi_vars):
        super(UnusedSsiVarsWarning, self).__init__(request, ssi_vars)

    def __str__(self):
        request = self.args[0]
        view = request.resolver_match.func
        return "The `ssi_included` view '%s.%s' at '%s' declares "\
            "using SSI variables %s but it looks like they're not "\
            "really used. " % (
                view.__module__, view.__name__, request.path, self.args[1])


class UndeclaredSsiRefError(SsifyError):
    def __init__(self, request, var, ref_name):
        super(UndeclaredSsiRefError, self).__init__(request, var, ref_name)

    def __str__(self):
        request = self.args[0]
        view = request.resolver_match.func
        return "Error while rendering ssi_included view '%s.%s' at '%s': "\
            "SSI variable %s references variable %s, which doesn't match "\
            "any variable declared in `get_ssi_vars`. " % (
                view.__module__, view.__name__, request.path,
                repr(self.args[1]), self.args[2])


class NoLangFieldError(SsifyError):
    def __init__(self, request):
        super(NoLangFieldError, self).__init__(request)

    def __str__(self):
        request = self.args[0]
        view = request.resolver_match.func
        return "The view '%s.%s' at '%s' is marked as `ssi_included` "\
            "with use_lang=True, but its URL match doesn't provide "\
            "a 'lang' keyword argument for language. " % (
            view.__module__, view.__name__, request.path)


class SsiVarsDependencyCycleError(SsifyError):
    def __init__(self, ssi_vars):
        super(SsiVarsDependencyCycleError, self).__init__(ssi_vars)

    def __str__(self):
        return "Dependency cycle in SSI variables: %s." % self.args[0]
