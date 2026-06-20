def requiere_active(func):
    def wrapper(self, *args, **kwargs):
        if self.is_active: 
            return func(self, *args, **kwargs)
    return wrapper