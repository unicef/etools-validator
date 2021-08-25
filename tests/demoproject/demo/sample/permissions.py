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
                "name": True,
                "description": True,
                "status": True,
                "document": True,
                "others": False,
                "special": True,
            }
        }
