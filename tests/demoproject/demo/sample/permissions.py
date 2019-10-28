def pend_permission(instance, user):
    if user is not None:
        return True
    return False


class DemoModelPermissions:
    def __init__(self, **kwargs):
        """Placeholder"""

    def get_permissions(self):
        return {
            "edit": {
                "name": "edit",
                "description": "edit",
                "status": "edit",
                "document": "edit",
                "others": "view",
            }
        }
