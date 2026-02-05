"""Data models for Therefore configuration elements."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import re

from .constants import ObjectType, UserType


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


@dataclass
class Field:
    """Represents a category field."""
    field_no: int
    field_id: str = ""
    col_name: str = ""
    caption: str = ""
    type_no: int = 0
    type_name: str = ""
    length: int = 0
    width: int = 0
    height: int = 0
    pos_x: int = 0
    pos_y: int = 0
    tab_order_pos: int = 0
    disp_order_pos: int = 0
    index_type: int = 0
    index_type_name: str = ""
    is_mandatory: bool = False
    default_value: str = ""
    regex_pattern: str = ""
    regex_help: str = ""
    counter_no: Optional[int] = None
    counter_mode: int = 0
    dictionary_no: Optional[int] = None
    data_type_no: Optional[int] = None
    id: str = ""


@dataclass
class Category:
    """Represents a document category."""
    category_no: int
    name: str = ""
    title: str = ""
    description: str = ""
    width: int = 0
    height: int = 0
    folder_no: Optional[int] = None
    fulltext_mode: int = 0
    fulltext_mode_name: str = ""
    checkin_mode: int = 0
    checkin_mode_name: str = ""
    auto_append_mode: int = 0
    auto_append_mode_name: str = ""
    empty_doc_mode: int = 0
    cover_mode: int = 0
    version: int = 0
    id: str = ""
    fields: List[Field] = field(default_factory=list)
    sub_categories: List["Category"] = field(default_factory=list)
    belongs_to_case_def: Optional[int] = None  # CaseDefNo this category belongs to
    sub_category_field_no: Optional[int] = None  # Field used for sub-category security
    workflow_process_no: Optional[int] = None  # Linked workflow


@dataclass
class CaseDefinition:
    """Represents a case definition (case management)."""
    case_def_no: int
    name: str = ""
    title: str = ""
    description: str = ""
    width: int = 0
    height: int = 0
    folder_no: Optional[int] = None
    checkin_mode: int = 0
    checkin_mode_name: str = ""
    auto_append_mode: int = 0
    auto_append_mode_name: str = ""
    empty_doc_mode: int = 0
    cover_mode: int = 0
    version: int = 0
    id: str = ""
    case_def_id: str = ""  # String identifier
    datatype_no: Optional[int] = None  # Reference to datatype for case data
    fields: List[Field] = field(default_factory=list)


@dataclass
class RoleAssignment:
    """Represents a security role assignment to an object."""
    role_no: int
    obj_type: int  # Object type (3=Category, 17=Root, etc.)
    obj_type_name: str = ""
    obj_no: int = 0  # Object number (e.g., category_no)
    sub_obj_no: int = 0  # Sub-object (e.g., keyword number for sub-category security)
    user_no: int = 0  # User/group number assigned
    user_name: str = ""  # Resolved user/group name
    role_name: str = ""  # Resolved role name
    condition: str = ""
    stop_inheritance: bool = False  # If true, inheritance is stopped


@dataclass
class WorkflowTransition:
    """Represents a workflow transition between tasks."""
    transition_no: int
    name: str = ""
    description: str = ""
    task_from_no: int = 0
    task_to_no: int = 0
    is_default: bool = False
    condition: str = ""
    arrow_type: int = 0
    seq_pos: int = 0
    id: str = ""
    action_text: str = ""  # The button/action label for this transition


@dataclass
class RestServiceCall:
    """Represents a REST service call configuration."""
    call_name: str = ""
    call_id: str = ""
    http_method: str = ""
    url: str = ""
    credential_no: str = ""
    body_params: List[Dict[str, str]] = field(default_factory=list)
    response_script: str = ""
    doc_to_send: str = ""
    to_pdf: bool = False
    part_name_file: str = ""
    part_name_metadata: str = ""


@dataclass
class WorkflowTask:
    """Represents a workflow task."""
    task_no: int
    task_id: str = ""
    name: str = ""
    type_no: int = 0
    type_name: str = ""
    process_no: int = 0
    pos_x: int = 0
    pos_y: int = 0
    duration: int = 0
    seq_pos: int = 0  # Sequence position for ordering
    overdue_mail: str = ""
    notification_mail: str = ""
    delegate_mail: str = ""
    use_checklist: bool = False
    checklist: List[str] = field(default_factory=list)
    choices: List[str] = field(default_factory=list)
    disable_delegation: bool = False
    user_choice: int = 0
    assigned_users: List[Dict[str, Any]] = field(default_factory=list)
    id: str = ""
    transitions: List[WorkflowTransition] = field(default_factory=list)
    # Additional fields for richer workflow display
    action_type: str = ""  # Type of automatic action (updateixdataex, routing, etc.)
    script_name: str = ""  # Script identifier
    params: str = ""  # Raw params XML for script extraction
    init_script: str = ""  # Extracted initialization script
    notification_subject: str = ""  # Email notification subject
    notification_message: str = ""  # Email notification body (HTML)
    rest_calls: List[RestServiceCall] = field(default_factory=list)  # REST service calls


@dataclass
class WorkflowProcess:
    """Represents a workflow process definition."""
    process_no: int
    name: str = ""
    description: str = ""
    version: int = 0
    folder_no: Optional[int] = None
    category_no: Optional[int] = None
    id: str = ""
    process_id: str = ""
    tasks: List[WorkflowTask] = field(default_factory=list)
    # Additional process-level settings
    duration: int = 0  # Process duration in minutes
    del_inst_days: int = 0  # Delete instance after N days
    attach_history: bool = False  # Attach workflow history to document
    allow_manual: bool = False  # Allow manual start
    notify_on_error: str = ""  # Error notification email
    comments_level: int = 0  # Comments level setting
    enabled: bool = True  # Whether workflow is enabled


@dataclass
class Folder:
    """Represents a folder in the folder hierarchy."""
    folder_no: int
    name: str = ""
    parent_no: Optional[int] = None
    folder_type: int = 0
    folder_type_name: str = ""
    id: str = ""
    children: List["Folder"] = field(default_factory=list)


@dataclass
class User:
    """Represents a user or group."""
    user_no: int
    user_name: str = ""
    display_name: str = ""
    user_type: int = 0
    user_type_name: str = ""
    id: str = ""
    domain: str = ""
    email: str = ""
    description: str = ""
    is_domain_user: bool = False
    member_of: List[str] = field(default_factory=list)  # Groups this user belongs to
    members: List["User"] = field(default_factory=list)  # Members if this is a group


@dataclass
class RoleObjectAssignment:
    """Represents an object that a role is assigned to (within Role)."""
    object_type: int
    object_type_name: str = ""
    object_no: int = 0
    object_name: str = ""
    sub_obj_no: int = 0


@dataclass
class Role:
    """Represents a permission role."""
    role_no: int
    name: str = ""
    description: str = ""
    permission: int = 0
    permission_names: List[str] = field(default_factory=list)
    id: str = ""
    is_deny: bool = False  # True if this is a deny role
    assignments: List[RoleObjectAssignment] = field(default_factory=list)
    users: List[User] = field(default_factory=list)


@dataclass
class EFormComponent:
    """Represents a component/field in an eForm."""
    key: str
    label: str = ""
    type: str = ""
    default_value: str = ""
    custom_default_value: str = ""  # JavaScript for dynamic default
    calculate_value: str = ""  # JavaScript for calculated values
    validate_custom: str = ""  # Custom validation JavaScript
    validate_required: bool = False
    conditional_show: str = ""
    conditional_when: str = ""
    conditional_json: str = ""
    custom_conditional: str = ""  # JavaScript for conditional logic
    hidden: bool = False
    disabled: bool = False
    data_source: str = ""  # Data source info for lookups/selects
    logic: List[Dict[str, Any]] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    children: List["EFormComponent"] = field(default_factory=list)


@dataclass
class EForm:
    """Represents an electronic form."""
    form_no: int
    name: str = ""
    form_id: str = ""
    version: int = 0
    folder_no: Optional[int] = None
    created_date: str = ""
    created_by: str = ""
    definition: str = ""  # JSON definition
    id: str = ""
    components: List[EFormComponent] = field(default_factory=list)  # Parsed components


@dataclass
class QueryField:
    """Represents a field in a query."""
    field_no: int
    caption: str = ""
    width: int = 0
    alignment: int = 0
    alignment_name: str = ""
    disp_pos: int = 0
    visible: bool = True


@dataclass
class Query:
    """Represents a saved search/query."""
    query_no: int
    name: str = ""
    description: str = ""
    category_no: Optional[int] = None
    folder_no: Optional[int] = None
    version_no: int = 0
    id: str = ""
    query_id: str = ""
    fields: List[QueryField] = field(default_factory=list)
    conditions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Keyword:
    """Represents a keyword in a dictionary."""
    keyword_no: int
    value: str = ""
    parent_no: Optional[int] = None
    id: str = ""


@dataclass
class KeywordDictionary:
    """Represents a keyword dictionary (lookup list)."""
    dictionary_no: int
    name: str = ""
    description: str = ""
    folder_no: Optional[int] = None
    single_type_no: Optional[int] = None  # TypeNo for single-select fields
    multi_type_no: Optional[int] = None   # TypeNo for multi-select fields
    id: str = ""
    keywords: List[Keyword] = field(default_factory=list)


@dataclass
class TreeViewLevel:
    """Represents a level in a tree view."""
    level_no: int
    field_no: int = 0
    field_name: str = ""
    level_function: int = 0
    level_function_name: str = ""
    sort_order: int = 0
    sort_order_name: str = ""


@dataclass
class TreeView:
    """Represents a tree view configuration."""
    treeview_no: int
    name: str = ""
    category_no: Optional[int] = None
    folder_no: Optional[int] = None
    id: str = ""
    levels: List[TreeViewLevel] = field(default_factory=list)


@dataclass
class Counter:
    """Represents an automatic counter."""
    counter_no: int
    name: str = ""
    counter_type: int = 0
    counter_type_name: str = ""
    format_string: str = ""
    current_value: int = 0
    folder_no: Optional[int] = None
    id: str = ""


@dataclass
class DataTypeColumn:
    """Represents a column in a user-defined data type."""
    col_no: int
    col_name: str = ""
    caption: str = ""
    type_no: int = 0
    type_name: str = ""
    length: int = 0
    is_primary: bool = False


@dataclass
class DataType:
    """Represents a custom data type."""
    datatype_no: int
    name: str = ""
    type_group: int = 0
    type_group_name: str = ""
    table_name: str = ""
    dictionary_no: Optional[int] = None
    id: str = ""
    columns: List[DataTypeColumn] = field(default_factory=list)


@dataclass
class Stamp:
    """Represents a stamp definition."""
    stamp_no: int
    name: str = ""
    stamp_type: int = 0
    stamp_type_name: str = ""
    folder_no: Optional[int] = None
    filename: str = ""
    id: str = ""


@dataclass
class CaptureProfile:
    """Represents a capture profile."""
    profile_no: int
    name: str = ""
    folder_no: Optional[int] = None
    color_mode: int = 0
    color_mode_name: str = ""
    doc_break: int = 0
    doc_break_name: str = ""
    storage_mode: int = 0
    storage_mode_name: str = ""
    id: str = ""


@dataclass
class ContentConnectorSource:
    """Represents a content connector source."""
    source_no: int
    name: str = ""
    source_mode: int = 0
    source_mode_name: str = ""
    folder_no: Optional[int] = None
    id: str = ""


@dataclass
class RetentionPolicyCategory:
    """Represents a category assignment for a retention policy."""
    category_no: int
    sub_category_no: int = 0
    category_name: str = ""
    no_retention: bool = False


@dataclass
class RetentionPolicy:
    """Represents a retention policy."""
    policy_no: int
    name: str = ""
    months: int = 0  # Retention period in months
    purge: bool = False  # Whether to purge documents
    delete_disk: bool = False  # Whether to delete from disk
    starting: str = ""  # Field or macro for retention start date
    id: str = ""
    categories: List[RetentionPolicyCategory] = field(default_factory=list)


@dataclass
class Configuration:
    """Represents the complete Therefore configuration."""
    version: str = ""
    version_int: int = 0  # Numeric version for comparison
    categories: List[Category] = field(default_factory=list)
    case_definitions: List[CaseDefinition] = field(default_factory=list)
    workflows: List[WorkflowProcess] = field(default_factory=list)
    folders: List[Folder] = field(default_factory=list)
    users: List[User] = field(default_factory=list)
    roles: List[Role] = field(default_factory=list)
    role_assignments: List[RoleAssignment] = field(default_factory=list)
    eforms: List[EForm] = field(default_factory=list)
    queries: List[Query] = field(default_factory=list)
    keyword_dictionaries: List[KeywordDictionary] = field(default_factory=list)
    tree_views: List[TreeView] = field(default_factory=list)
    counters: List[Counter] = field(default_factory=list)
    data_types: List[DataType] = field(default_factory=list)
    stamps: List[Stamp] = field(default_factory=list)
    capture_profiles: List[CaptureProfile] = field(default_factory=list)
    content_connector_sources: List[ContentConnectorSource] = field(default_factory=list)
    retention_policies: List[RetentionPolicy] = field(default_factory=list)

    # Lookup maps for cross-referencing
    _category_map: Dict[int, Category] = field(default_factory=dict)
    _case_def_map: Dict[int, CaseDefinition] = field(default_factory=dict)
    _folder_map: Dict[int, Folder] = field(default_factory=dict)
    _user_map: Dict[int, User] = field(default_factory=dict)
    _role_map: Dict[int, Role] = field(default_factory=dict)
    _dictionary_map: Dict[int, KeywordDictionary] = field(default_factory=dict)
    _counter_map: Dict[int, Counter] = field(default_factory=dict)
    _datatype_map: Dict[int, DataType] = field(default_factory=dict)
    _workflow_map: Dict[int, WorkflowProcess] = field(default_factory=dict)
    _type_to_dictionary_map: Dict[int, KeywordDictionary] = field(default_factory=dict)
    _type_to_datatype_map: Dict[int, DataType] = field(default_factory=dict)

    def build_lookup_maps(self):
        """Build lookup maps for cross-referencing."""
        self._category_map = {c.category_no: c for c in self.categories}
        self._case_def_map = {c.case_def_no: c for c in self.case_definitions}
        self._folder_map = {f.folder_no: f for f in self._flatten_folders(self.folders)}
        self._user_map = {u.user_no: u for u in self.users}
        self._role_map = {r.role_no: r for r in self.roles}
        self._dictionary_map = {d.dictionary_no: d for d in self.keyword_dictionaries}
        self._counter_map = {c.counter_no: c for c in self.counters}
        self._datatype_map = {d.datatype_no: d for d in self.data_types}
        self._workflow_map = {w.process_no: w for w in self.workflows}

        # Build maps for field TypeNo to dictionary/datatype
        # Fields reference dictionaries via SingleTypeNo or MulitTypeNo, not KeyDicNo
        self._type_to_dictionary_map = {}
        for d in self.keyword_dictionaries:
            if d.single_type_no is not None:
                self._type_to_dictionary_map[d.single_type_no] = d
            if d.multi_type_no is not None:
                self._type_to_dictionary_map[d.multi_type_no] = d

        # Fields reference datatypes via TypeNo
        self._type_to_datatype_map = {d.datatype_no: d for d in self.data_types}

        # Resolve role assignment names
        for ra in self.role_assignments:
            if ra.role_no in self._role_map:
                ra.role_name = self._role_map[ra.role_no].name
            if ra.user_no in self._user_map:
                ra.user_name = self._user_map[ra.user_no].display_name or self._user_map[ra.user_no].user_name

    def _flatten_folders(self, folders: List[Folder]) -> List[Folder]:
        """Flatten nested folder hierarchy into a list."""
        result = []
        for folder in folders:
            result.append(folder)
            result.extend(self._flatten_folders(folder.children))
        return result

    def get_category(self, category_no: int) -> Optional[Category]:
        """Get a category by number."""
        return self._category_map.get(category_no)

    def get_case_definition(self, case_def_no: int) -> Optional[CaseDefinition]:
        """Get a case definition by number."""
        return self._case_def_map.get(case_def_no)

    def get_role(self, role_no: int) -> Optional[Role]:
        """Get a role by number."""
        return self._role_map.get(role_no)

    def get_user(self, user_no: int) -> Optional[User]:
        """Get a user by number."""
        return self._user_map.get(user_no)

    def get_role_assignments_for_object(self, obj_type: int, obj_no: int) -> List[RoleAssignment]:
        """Get role assignments for a specific object."""
        return [ra for ra in self.role_assignments
                if ra.obj_type == obj_type and ra.obj_no == obj_no]

    def get_categories_for_case_def(self, case_def_no: int) -> List[Category]:
        """Get categories that belong to a case definition."""
        return [c for c in self.categories if c.belongs_to_case_def == case_def_no]

    def get_folder(self, folder_no: int) -> Optional[Folder]:
        """Get a folder by number."""
        return self._folder_map.get(folder_no)

    def get_folder_path(self, folder_no: int) -> str:
        """Get the full path of a folder."""
        folder = self.get_folder(folder_no)
        if not folder:
            return ""

        path_parts = [folder.name]
        current = folder
        while current.parent_no is not None:
            parent = self.get_folder(current.parent_no)
            if parent:
                path_parts.insert(0, parent.name)
                current = parent
            else:
                break

        return " / ".join(path_parts)

    def get_user(self, user_no: int) -> Optional[User]:
        """Get a user by number."""
        return self._user_map.get(user_no)

    def get_dictionary(self, dictionary_no: int) -> Optional[KeywordDictionary]:
        """Get a keyword dictionary by its KeyDicNo."""
        return self._dictionary_map.get(dictionary_no)

    def get_dictionary_by_type_no(self, type_no: int) -> Optional[KeywordDictionary]:
        """Get a keyword dictionary by field TypeNo (SingleTypeNo or MulitTypeNo)."""
        return self._type_to_dictionary_map.get(type_no)

    def get_datatype_by_type_no(self, type_no: int) -> Optional[DataType]:
        """Get a data type by field TypeNo."""
        return self._type_to_datatype_map.get(type_no)

    def get_counter(self, counter_no: int) -> Optional[Counter]:
        """Get a counter by number."""
        return self._counter_map.get(counter_no)

    def get_datatype(self, datatype_no: int) -> Optional[DataType]:
        """Get a data type by number."""
        return self._datatype_map.get(datatype_no)

    def get_workflow(self, process_no: int) -> Optional[WorkflowProcess]:
        """Get a workflow by process number."""
        return self._workflow_map.get(process_no)

    def get_dictionary_usage(self) -> Dict[int, List[tuple]]:
        """
        Get dictionary usage - which categories/fields use each dictionary.

        Returns:
            Dict mapping dictionary_no to list of (category_name, field_caption) tuples
        """
        usage: Dict[int, List[tuple]] = {}
        for category in self.categories:
            for fld in category.fields:
                if fld.type_no < 0:
                    # Look up dictionary by the field's TypeNo
                    dictionary = self.get_dictionary_by_type_no(fld.type_no)
                    if dictionary:
                        if dictionary.dictionary_no not in usage:
                            usage[dictionary.dictionary_no] = []
                        usage[dictionary.dictionary_no].append((category.name, fld.caption))
        return usage

    def get_categories_for_dictionary(self, dictionary_no: int) -> List[tuple]:
        """
        Get list of categories that use a specific dictionary.

        Args:
            dictionary_no: The dictionary number (KeyDicNo) to look up

        Returns:
            List of (category_name, field_caption) tuples
        """
        usage = self.get_dictionary_usage()
        return usage.get(dictionary_no, [])

    def get_field_by_no(self, field_no: int) -> Optional[Field]:
        """Get a field by its FieldNo across all categories."""
        for category in self.categories:
            for fld in category.fields:
                if fld.field_no == field_no:
                    return fld
            # Also check sub-categories
            for sub_cat in category.sub_categories:
                for fld in sub_cat.fields:
                    if fld.field_no == field_no:
                        return fld
        return None

    def resolve_field_macros(self, text: str) -> str:
        """
        Resolve field macros like [-31] to their field names.

        Args:
            text: Text containing field macros in format [FieldNo]

        Returns:
            Text with macros replaced by field names
        """
        import re

        def replace_macro(match):
            field_no_str = match.group(1)
            try:
                field_no = int(field_no_str)
                field = self.get_field_by_no(field_no)
                if field:
                    # Return field caption with the original macro as tooltip
                    return f"[{field.caption}]"
            except ValueError:
                pass
            return match.group(0)  # Return original if not found

        # Match patterns like [-31], [123], etc.
        pattern = r'\[(-?\d+)\]'
        return re.sub(pattern, replace_macro, text)

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the configuration."""
        return {
            "categories": len(self.categories),
            "case_definitions": len(self.case_definitions),
            "fields": sum(len(c.fields) for c in self.categories),
            "workflows": len(self.workflows),
            "workflow_tasks": sum(len(w.tasks) for w in self.workflows),
            "folders": len(self._flatten_folders(self.folders)),
            "users": len([u for u in self.users if u.user_type == UserType.USER]),
            "groups": len([u for u in self.users if u.user_type == UserType.GROUP]),
            "roles": len(self.roles),
            "eforms": len(self.eforms),
            "queries": len(self.queries),
            "keyword_dictionaries": len(self.keyword_dictionaries),
            "tree_views": len(self.tree_views),
            "counters": len(self.counters),
            "data_types": len(self.data_types),
            "stamps": len(self.stamps),
            "retention_policies": len(self.retention_policies),
        }

    def is_version_supported(self, supported_version: int) -> bool:
        """Check if the configuration version is supported."""
        return self.version_int <= supported_version

    def get_version_warning(self, supported_version: int) -> Optional[str]:
        """
        Get a warning message if the configuration version is newer than supported.

        Returns:
            Warning message string if version is newer, None if supported.
        """
        if self.version_int > supported_version:
            return (
                f"This configuration was exported from a newer version of Therefore "
                f"(schema version {self.version_int}) than currently supported "
                f"({supported_version}). Some features may not be fully documented."
            )
        return None

    def get_counter_usage(self) -> Dict[int, List[tuple]]:
        """Get counter usage - which categories/fields use each counter."""
        usage: Dict[int, List[tuple]] = {}
        for category in self.categories:
            for fld in category.fields:
                if fld.counter_no:
                    if fld.counter_no not in usage:
                        usage[fld.counter_no] = []
                    usage[fld.counter_no].append((category.name, fld.caption))
        return usage

    def get_workflows_for_category(self, category_no: int) -> List["WorkflowProcess"]:
        """Get workflows that are linked to a specific category."""
        return [w for w in self.workflows if w.category_no == category_no]

    def get_queries_for_category(self, category_no: int) -> List["Query"]:
        """Get queries that are linked to a specific category."""
        return [q for q in self.queries if q.category_no == category_no]

    def get_treeviews_for_category(self, category_no: int) -> List["TreeView"]:
        """Get tree views that are linked to a specific category."""
        return [tv for tv in self.tree_views if tv.category_no == category_no]

    def get_root_security(self) -> List[RoleAssignment]:
        """Get role assignments for the root level (Folder with ObjNo=0)."""
        return [ra for ra in self.role_assignments
                if ra.obj_type == ObjectType.FOLDER and ra.obj_no == 0]

    def get_folder_security(self, folder_no: int) -> List[RoleAssignment]:
        """Get role assignments for a specific folder."""
        return [ra for ra in self.role_assignments
                if ra.obj_type == ObjectType.FOLDER and ra.obj_no == folder_no]

    def folder_stops_inheritance(self, folder_no: int) -> bool:
        """Check if a folder stops inheritance (has StopInh=1 with RoleNo=0)."""
        assignments = self.get_folder_security(folder_no)
        return any(ra.stop_inheritance and ra.role_no == 0 for ra in assignments)

    def get_all_security_assignments(self) -> Dict[str, List[RoleAssignment]]:
        """
        Get all security assignments organized by object type.

        Returns:
            Dict with keys: 'root', 'folders', 'categories', 'workflows', etc.
            Each value is a list of RoleAssignment objects
        """
        result = {
            'root': [],
            'folders': [],
            'categories': [],
            'workflows': [],
            'queries': [],
            'other': []
        }

        for ra in self.role_assignments:
            if ra.obj_type == ObjectType.FOLDER:
                if ra.obj_no == 0:
                    result['root'].append(ra)
                else:
                    result['folders'].append(ra)
            elif ra.obj_type == ObjectType.CATEGORY:
                result['categories'].append(ra)
            elif ra.obj_type == ObjectType.WORKFLOW_PROCESS:
                result['workflows'].append(ra)
            elif ra.obj_type == ObjectType.QUERY:
                result['queries'].append(ra)
            else:
                result['other'].append(ra)

        return result

    def validate(self) -> List[Dict[str, Any]]:
        """
        Validate the configuration and return a list of warnings/issues.

        Returns:
            List of dicts with keys: type (warning/error), category, message, object_name
        """
        issues = []

        # Check for empty categories
        for cat in self.categories:
            if not cat.fields:
                issues.append({
                    "type": "warning",
                    "category": "Category",
                    "message": "Category has no fields defined",
                    "object_name": cat.name,
                    "object_id": f"category-{_slugify(cat.name) or abs(cat.category_no)}"
                })

        # Check for workflows with no tasks
        for wf in self.workflows:
            if not wf.tasks:
                issues.append({
                    "type": "warning",
                    "category": "Workflow",
                    "message": "Workflow has no tasks defined",
                    "object_name": wf.name,
                    "object_id": f"workflow-{_slugify(wf.name) or abs(wf.process_no)}"
                })

        # Check for unused dictionaries
        used_dict_type_nos = set()
        for cat in self.categories:
            for fld in cat.fields:
                if fld.type_no < 0:
                    used_dict_type_nos.add(fld.type_no)

        for d in self.keyword_dictionaries:
            is_used = False
            if d.single_type_no in used_dict_type_nos or d.multi_type_no in used_dict_type_nos:
                is_used = True
            if not is_used:
                issues.append({
                    "type": "info",
                    "category": "Dictionary",
                    "message": "Dictionary is not used by any category field",
                    "object_name": d.name,
                    "object_id": f"dictionary-{_slugify(d.name) or abs(d.dictionary_no)}"
                })

        # Check for unused counters
        used_counter_nos = set()
        for cat in self.categories:
            for fld in cat.fields:
                if fld.counter_no:
                    used_counter_nos.add(fld.counter_no)

        for c in self.counters:
            if c.counter_no not in used_counter_nos:
                issues.append({
                    "type": "info",
                    "category": "Counter",
                    "message": "Counter is not used by any category field",
                    "object_name": c.name,
                    "object_id": f"counter-{_slugify(c.name) or abs(c.counter_no)}"
                })

        # Check for roles with no users assigned
        for role in self.roles:
            if not role.users:
                issues.append({
                    "type": "info",
                    "category": "Role",
                    "message": "Role has no users or groups assigned",
                    "object_name": role.name,
                    "object_id": f"role-{_slugify(role.name) or abs(role.role_no)}"
                })

        # Check for orphaned workflow references (category doesn't exist)
        for wf in self.workflows:
            if wf.category_no and not self.get_category(wf.category_no):
                issues.append({
                    "type": "error",
                    "category": "Workflow",
                    "message": f"References non-existent category (CtgryNo: {wf.category_no})",
                    "object_name": wf.name,
                    "object_id": f"workflow-{_slugify(wf.name) or abs(wf.process_no)}"
                })

        # Check for empty keyword dictionaries
        for d in self.keyword_dictionaries:
            if not d.keywords:
                issues.append({
                    "type": "warning",
                    "category": "Dictionary",
                    "message": "Dictionary has no keywords defined",
                    "object_name": d.name,
                    "object_id": f"dictionary-{_slugify(d.name) or abs(d.dictionary_no)}"
                })

        return issues
