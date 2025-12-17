from better_auth.models import User
from sqlalchemy import Column, String
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from better_auth.models import UserDict

class ExtendedUser(User):
    """
    Extended user model with software/hardware background fields
    """
    def __init__(self, **kwargs: "UserDict"):
        super().__init__(**kwargs)
        # Extended fields for software/hardware background
        self.software_level = kwargs.get('software_level', 'beginner')
        self.software_stack = kwargs.get('software_stack', '')
        self.hardware_level = kwargs.get('hardware_level', 'none')
        self.hardware_platforms = kwargs.get('hardware_platforms', '')

    def to_dict(self) -> "UserDict":
        base_dict = super().to_dict()
        base_dict.update({
            'software_level': self.software_level,
            'software_stack': self.software_stack,
            'hardware_level': self.hardware_level,
            'hardware_platforms': self.hardware_platforms
        })
        return base_dict