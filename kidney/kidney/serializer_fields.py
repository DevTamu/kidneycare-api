from rest_framework import serializers

class CustomCharField(serializers.CharField):

    def __init__(self, custom_error_name, **kwargs):

        # Call the super first to initialize everything
        super().__init__(**kwargs)
        
        # Override only the 'blank' error message, if custom_error_name is given
        if custom_error_name:
            self.error_messages["blank"] = custom_error_name
            self.error_messages["null"] = custom_error_name

        self.write_only = True
        self.allow_blank = True


class CustomFloatField(serializers.FloatField):

    def __init__(self, custom_error_name, **kwargs):

        # Call the super first to initialize everything
        super().__init__(**kwargs)
        
        # Override only the 'blank' error message, if custom_error_name is given
        if custom_error_name:
            self.error_messages["blank"] = custom_error_name
            self.error_messages["null"] = custom_error_name

        self.write_only = True
        self.allow_blank = True


class CustomIntegerField(serializers.IntegerField):

    def __init__(self, custom_error_name, **kwargs):

        # Call the super first to initialize everything
        super().__init__(**kwargs)
        
        # Override only the 'blank' error message, if custom_error_name is given
        if custom_error_name:
            self.error_messages["blank"] = custom_error_name
            self.error_messages["null"] = custom_error_name

        self.write_only = True
        self.allow_blank = True

