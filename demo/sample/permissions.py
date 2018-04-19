class DemoModelPermissions(object):
    def __init__(self, **kwargs):
        """Placeholder"""

    def get_permissions(self):
        return {
            "edit": {
                "name": "edit",
                "description": "edit",
                "status": "edit",
                "document": "edit",
            }
        }
