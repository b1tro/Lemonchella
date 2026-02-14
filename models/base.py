import datetime as dt
from beanie import Document, before_event, ValidateOnSave, Update
from beanie import Document, Insert
from pydantic.fields import Field


class TimestampedDocument(Document):
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))
    """datetime: Date when document was created."""
    updated_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))
    """datetime: Date when document was updated."""
    
    @before_event(ValidateOnSave, Update)
    def update_updated_at(self):
        self.updated_at = dt.datetime.now(dt.timezone.utc)
    
    @before_event(Insert)
    def create_created_at(self):
        self.created_at = dt.datetime.now(dt.timezone.utc)