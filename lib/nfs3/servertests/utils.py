def assert_raises(exc_class, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except exc_class as e:
        return e
    except Exception as e:
        raise AssertionError("{} raised - when {} was expected".format(e, exc_class))
    else:
        raise AssertionError("{} not raised".format(exc_class))
