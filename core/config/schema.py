from drf_yasg.inspectors import SwaggerAutoSchema


def get_auto_schema_class_by_tags(tags):
    class AutoSchema(SwaggerAutoSchema):
        def get_tags(self, operation_keys):
            return tags

    return AutoSchema
