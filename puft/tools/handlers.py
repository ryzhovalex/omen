from puft.errors.error import Error


def handle_wildcard_error(err: Error):
    return err.expose()


def handle_wildcard_builtin_error(err: Exception):
    return {"error": {
        "name": err.__class__.__name__,
        "message": "; ".join(err.args)
    }}
