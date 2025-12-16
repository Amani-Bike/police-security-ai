from pydantic import BaseModel, validator
from typing import Optional


class PoliceSignupRequest(BaseModel):
    username: str
    identifier: str  # Either email or phone number
    password: str
    full_name: Optional[str] = None
    badge_id: Optional[str] = None
    age: Optional[int] = None
    district: Optional[str] = None

    @validator('identifier')
    def validate_identifier(cls, v):
        import re
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, v):
            return v
        
        # Validate phone number format
        # Remove spaces, dashes, and parentheses
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', v)
        phone_pattern = r'^(\+\d{1,3})?\d{10,15}$'
        if re.match(phone_pattern, cleaned_phone) and len(cleaned_phone) <= 15:
            return v
        
        raise ValueError('Identifier must be a valid email or phone number')