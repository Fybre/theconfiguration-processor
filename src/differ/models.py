"""Data models for configuration diff results."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FieldChange:
    """Represents a change to a single field/property."""
    field_name: str
    old_value: Any
    new_value: Any
    change_type: str  # 'added', 'removed', 'modified'

    @property
    def display_old_value(self) -> str:
        """Format old value for display."""
        return self._format_value(self.old_value)

    @property
    def display_new_value(self) -> str:
        """Format new value for display."""
        return self._format_value(self.new_value)

    def _format_value(self, value: Any) -> str:
        """Format a value for human-readable display."""
        if value is None:
            return "(none)"
        if isinstance(value, bool):
            return "Yes" if value else "No"
        if isinstance(value, list):
            if len(value) == 0:
                return "(empty list)"
            if len(value) <= 3:
                return ", ".join(str(v) for v in value)
            return f"{len(value)} items"
        if isinstance(value, str) and len(value) > 100:
            return value[:100] + "..."
        return str(value)


@dataclass
class ObjectChange:
    """Represents a change to an object (category, workflow, etc.)."""
    object_type: str      # 'Category', 'Workflow', 'Role', etc.
    object_name: str      # Display name of the object
    object_id: str        # GUID or unique identifier
    change_type: str      # 'added', 'removed', 'modified'
    field_changes: List[FieldChange] = field(default_factory=list)
    nested_changes: List['ObjectChange'] = field(default_factory=list)

    # Additional context for display
    extra_info: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        """Check if there are any actual changes."""
        return len(self.field_changes) > 0 or len(self.nested_changes) > 0

    @property
    def total_changes(self) -> int:
        """Count total number of changes including nested."""
        count = len(self.field_changes)
        for nested in self.nested_changes:
            count += 1  # The nested object itself
            if nested.change_type == 'modified':
                count += nested.total_changes
        return count

    def get_nested_by_type(self, change_type: str) -> List['ObjectChange']:
        """Get nested changes of a specific type."""
        return [n for n in self.nested_changes if n.change_type == change_type]

    @property
    def nested_added(self) -> List['ObjectChange']:
        return self.get_nested_by_type('added')

    @property
    def nested_removed(self) -> List['ObjectChange']:
        return self.get_nested_by_type('removed')

    @property
    def nested_modified(self) -> List['ObjectChange']:
        return self.get_nested_by_type('modified')


@dataclass
class DiffSummary:
    """Summary statistics for a single object type."""
    added: int = 0
    removed: int = 0
    modified: int = 0

    @property
    def total(self) -> int:
        return self.added + self.removed + self.modified

    @property
    def has_changes(self) -> bool:
        return self.total > 0


@dataclass
class DiffResult:
    """Complete result of comparing two configurations."""
    file_a_name: str
    file_b_name: str
    changes: List[ObjectChange] = field(default_factory=list)

    # Summary by object type
    _summary: Optional[Dict[str, DiffSummary]] = field(default=None, repr=False)

    @property
    def summary(self) -> Dict[str, DiffSummary]:
        """Get summary statistics by object type."""
        if self._summary is None:
            self._summary = self._compute_summary()
        return self._summary

    def _compute_summary(self) -> Dict[str, DiffSummary]:
        """Compute summary statistics from changes."""
        result: Dict[str, DiffSummary] = {}

        for change in self.changes:
            obj_type = change.object_type
            if obj_type not in result:
                result[obj_type] = DiffSummary()

            if change.change_type == 'added':
                result[obj_type].added += 1
            elif change.change_type == 'removed':
                result[obj_type].removed += 1
            elif change.change_type == 'modified':
                result[obj_type].modified += 1

        return result

    @property
    def has_changes(self) -> bool:
        """Check if there are any differences."""
        return len(self.changes) > 0

    @property
    def total_changes(self) -> int:
        """Total number of changed objects."""
        return len(self.changes)

    def get_changes_by_type(self, object_type: str) -> List[ObjectChange]:
        """Get all changes for a specific object type."""
        return [c for c in self.changes if c.object_type == object_type]

    def get_changes_by_change_type(self, change_type: str) -> List[ObjectChange]:
        """Get all changes of a specific change type (added/removed/modified)."""
        return [c for c in self.changes if c.change_type == change_type]

    @property
    def object_types_with_changes(self) -> List[str]:
        """Get list of object types that have changes, in display order."""
        # Define preferred display order
        order = [
            'Category', 'CaseDefinition', 'Workflow', 'Role', 'User', 'Group',
            'Folder', 'EForm', 'Query', 'Dictionary', 'TreeView', 'Counter',
            'DataType', 'Stamp', 'RetentionPolicy', 'RoleAssignment'
        ]

        types_with_changes = set(c.object_type for c in self.changes)

        # Return in order, with any unknown types at the end
        result = [t for t in order if t in types_with_changes]
        result.extend(sorted(types_with_changes - set(order)))

        return result
