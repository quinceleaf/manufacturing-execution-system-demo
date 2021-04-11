class ULIDConverter:
    regex = "[0-9A-Z]{26}"

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)