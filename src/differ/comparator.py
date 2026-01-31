"""Configuration comparison logic."""

from dataclasses import fields as dataclass_fields
from typing import Any, Dict, List, Optional, Tuple, TypeVar

from ..parser.models import (
    Configuration, Category, CaseDefinition, WorkflowProcess, WorkflowTask,
    Folder, Role, User, EForm, Query, KeywordDictionary, TreeView, Counter,
    DataType, Stamp, RetentionPolicy, RoleAssignment, Field,
    WorkflowTransition, TreeViewLevel, DataTypeColumn, EFormComponent, Keyword
)
from .models import DiffResult, ObjectChange, FieldChange

T = TypeVar('T')


class DiffComparator:
    """Compares two Therefore configurations and identifies differences."""

    def __init__(self):
        self.config_a: Optional[Configuration] = None
        self.config_b: Optional[Configuration] = None

    def compare(
        self,
        config_a: Configuration,
        config_b: Configuration,
        file_a_name: str = "Configuration A",
        file_b_name: str = "Configuration B"
    ) -> DiffResult:
        """
        Compare two configurations and return the differences.

        Args:
            config_a: The "before" or "old" configuration
            config_b: The "after" or "new" configuration
            file_a_name: Display name for config A
            file_b_name: Display name for config B

        Returns:
            DiffResult containing all detected changes
        """
        self.config_a = config_a
        self.config_b = config_b

        changes: List[ObjectChange] = []

        # Compare each entity type
        changes.extend(self._compare_categories())
        changes.extend(self._compare_case_definitions())
        changes.extend(self._compare_workflows())
        changes.extend(self._compare_roles())
        changes.extend(self._compare_users())
        changes.extend(self._compare_folders())
        changes.extend(self._compare_eforms())
        changes.extend(self._compare_queries())
        changes.extend(self._compare_dictionaries())
        changes.extend(self._compare_treeviews())
        changes.extend(self._compare_counters())
        changes.extend(self._compare_datatypes())
        changes.extend(self._compare_stamps())
        changes.extend(self._compare_retention_policies())
        changes.extend(self._compare_role_assignments())

        return DiffResult(
            file_a_name=file_a_name,
            file_b_name=file_b_name,
            changes=changes
        )

    # =========================================================================
    # Object Matching
    # =========================================================================

    def _match_objects(
        self,
        list_a: List[T],
        list_b: List[T],
        id_field: str = 'id',
        name_field: str = 'name',
        num_field: Optional[str] = None
    ) -> Tuple[List[Tuple[T, T]], List[T], List[T]]:
        """
        Match objects between two lists.

        Returns:
            Tuple of (matched_pairs, only_in_a, only_in_b)
        """
        # Build lookup maps for list_b
        b_by_id: Dict[str, T] = {}
        b_by_name: Dict[str, T] = {}
        b_by_num: Dict[int, T] = {}

        for obj in list_b:
            obj_id = getattr(obj, id_field, None)
            if obj_id:
                b_by_id[obj_id] = obj

            obj_name = getattr(obj, name_field, None)
            if obj_name:
                b_by_name[obj_name] = obj

            if num_field:
                obj_num = getattr(obj, num_field, None)
                if obj_num is not None:
                    b_by_num[obj_num] = obj

        matched: List[Tuple[T, T]] = []
        only_in_a: List[T] = []
        matched_b_ids: set = set()

        # Try to match each object in A
        for obj_a in list_a:
            obj_a_id = getattr(obj_a, id_field, None)
            obj_a_name = getattr(obj_a, name_field, None)
            obj_a_num = getattr(obj_a, num_field, None) if num_field else None

            match = None

            # Try matching by GUID/id first (most reliable)
            if obj_a_id and obj_a_id in b_by_id:
                match = b_by_id[obj_a_id]
            # Try matching by numeric ID
            elif obj_a_num is not None and obj_a_num in b_by_num:
                match = b_by_num[obj_a_num]
            # Fallback to name matching
            elif obj_a_name and obj_a_name in b_by_name:
                match = b_by_name[obj_a_name]

            if match:
                matched.append((obj_a, match))
                matched_b_ids.add(id(match))
            else:
                only_in_a.append(obj_a)

        # Find objects only in B
        only_in_b = [obj for obj in list_b if id(obj) not in matched_b_ids]

        return matched, only_in_a, only_in_b

    # =========================================================================
    # Field Comparison
    # =========================================================================

    def _compare_simple_fields(
        self,
        obj_a: Any,
        obj_b: Any,
        field_names: List[str],
        display_names: Optional[Dict[str, str]] = None
    ) -> List[FieldChange]:
        """Compare simple scalar fields between two objects."""
        changes = []
        display_names = display_names or {}

        for field_name in field_names:
            val_a = getattr(obj_a, field_name, None)
            val_b = getattr(obj_b, field_name, None)

            # Normalize empty strings to None for comparison
            if val_a == '':
                val_a = None
            if val_b == '':
                val_b = None

            if val_a != val_b:
                display_name = display_names.get(field_name, field_name)
                changes.append(FieldChange(
                    field_name=display_name,
                    old_value=val_a,
                    new_value=val_b,
                    change_type='modified'
                ))

        return changes

    def _get_object_name(self, obj: Any, fallback: str = "Unknown") -> str:
        """Get display name for an object."""
        for attr in ['name', 'title', 'user_name', 'display_name']:
            val = getattr(obj, attr, None)
            if val:
                return str(val)
        return fallback

    def _get_object_id(self, obj: Any) -> str:
        """Get unique identifier for an object."""
        obj_id = getattr(obj, 'id', None)
        if obj_id:
            return str(obj_id)
        # Fallback to numeric id
        for attr in ['category_no', 'process_no', 'role_no', 'user_no',
                     'folder_no', 'form_no', 'query_no', 'dictionary_no',
                     'treeview_no', 'counter_no', 'datatype_no', 'stamp_no',
                     'policy_no', 'case_def_no']:
            val = getattr(obj, attr, None)
            if val is not None:
                return str(val)
        return str(id(obj))

    # =========================================================================
    # Category Comparison
    # =========================================================================

    def _compare_categories(self) -> List[ObjectChange]:
        """Compare categories between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.categories,
            self.config_b.categories,
            id_field='id',
            name_field='name',
            num_field='category_no'
        )

        changes = []

        # Added categories
        for cat in added:
            changes.append(ObjectChange(
                object_type='Category',
                object_name=cat.name,
                object_id=self._get_object_id(cat),
                change_type='added',
                extra_info={'field_count': len(cat.fields)}
            ))

        # Removed categories
        for cat in removed:
            changes.append(ObjectChange(
                object_type='Category',
                object_name=cat.name,
                object_id=self._get_object_id(cat),
                change_type='removed',
                extra_info={'field_count': len(cat.fields)}
            ))

        # Modified categories
        for cat_a, cat_b in matched:
            field_changes = self._compare_simple_fields(
                cat_a, cat_b,
                ['name', 'title', 'description', 'folder_no', 'fulltext_mode',
                 'checkin_mode', 'empty_doc_mode'],
                {'fulltext_mode': 'Full-text Mode', 'checkin_mode': 'Check-in Mode',
                 'empty_doc_mode': 'Empty Document Mode', 'folder_no': 'Folder'}
            )

            # Compare fields
            nested_changes = self._compare_category_fields(cat_a.fields, cat_b.fields)

            if field_changes or nested_changes:
                changes.append(ObjectChange(
                    object_type='Category',
                    object_name=cat_b.name,
                    object_id=self._get_object_id(cat_b),
                    change_type='modified',
                    field_changes=field_changes,
                    nested_changes=nested_changes
                ))

        return changes

    def _compare_category_fields(
        self,
        fields_a: List[Field],
        fields_b: List[Field]
    ) -> List[ObjectChange]:
        """Compare fields within a category."""
        matched, removed, added = self._match_objects(
            fields_a, fields_b,
            id_field='id',
            name_field='caption',
            num_field='field_no'
        )

        changes = []

        for fld in added:
            changes.append(ObjectChange(
                object_type='Field',
                object_name=fld.caption,
                object_id=self._get_object_id(fld),
                change_type='added',
                extra_info={'type': fld.type_name}
            ))

        for fld in removed:
            changes.append(ObjectChange(
                object_type='Field',
                object_name=fld.caption,
                object_id=self._get_object_id(fld),
                change_type='removed',
                extra_info={'type': fld.type_name}
            ))

        for fld_a, fld_b in matched:
            field_changes = self._compare_simple_fields(
                fld_a, fld_b,
                ['caption', 'type_no', 'length', 'index_type', 'is_mandatory'],
                {'type_no': 'Type', 'index_type': 'Index', 'is_mandatory': 'Mandatory'}
            )
            if field_changes:
                changes.append(ObjectChange(
                    object_type='Field',
                    object_name=fld_b.caption,
                    object_id=self._get_object_id(fld_b),
                    change_type='modified',
                    field_changes=field_changes
                ))

        return changes

    # =========================================================================
    # Case Definition Comparison
    # =========================================================================

    def _compare_case_definitions(self) -> List[ObjectChange]:
        """Compare case definitions between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.case_definitions,
            self.config_b.case_definitions,
            id_field='id',
            name_field='name',
            num_field='case_def_no'
        )

        changes = []

        for case_def in added:
            changes.append(ObjectChange(
                object_type='CaseDefinition',
                object_name=case_def.title or case_def.name,
                object_id=self._get_object_id(case_def),
                change_type='added',
                extra_info={'field_count': len(case_def.fields)}
            ))

        for case_def in removed:
            changes.append(ObjectChange(
                object_type='CaseDefinition',
                object_name=case_def.title or case_def.name,
                object_id=self._get_object_id(case_def),
                change_type='removed',
                extra_info={'field_count': len(case_def.fields)}
            ))

        for cd_a, cd_b in matched:
            field_changes = self._compare_simple_fields(
                cd_a, cd_b,
                ['name', 'title', 'description', 'folder_no', 'checkin_mode', 'auto_append_mode'],
                {'checkin_mode': 'Check-in Mode', 'auto_append_mode': 'Auto-append Mode',
                 'folder_no': 'Folder'}
            )

            nested_changes = self._compare_category_fields(cd_a.fields, cd_b.fields)

            if field_changes or nested_changes:
                changes.append(ObjectChange(
                    object_type='CaseDefinition',
                    object_name=cd_b.title or cd_b.name,
                    object_id=self._get_object_id(cd_b),
                    change_type='modified',
                    field_changes=field_changes,
                    nested_changes=nested_changes
                ))

        return changes

    # =========================================================================
    # Workflow Comparison
    # =========================================================================

    def _compare_workflows(self) -> List[ObjectChange]:
        """Compare workflows between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.workflows,
            self.config_b.workflows,
            id_field='id',
            name_field='name',
            num_field='process_no'
        )

        changes = []

        for wf in added:
            changes.append(ObjectChange(
                object_type='Workflow',
                object_name=wf.name,
                object_id=self._get_object_id(wf),
                change_type='added',
                extra_info={'task_count': len(wf.tasks)}
            ))

        for wf in removed:
            changes.append(ObjectChange(
                object_type='Workflow',
                object_name=wf.name,
                object_id=self._get_object_id(wf),
                change_type='removed',
                extra_info={'task_count': len(wf.tasks)}
            ))

        for wf_a, wf_b in matched:
            field_changes = self._compare_simple_fields(
                wf_a, wf_b,
                ['name', 'description', 'enabled', 'category_no', 'folder_no',
                 'duration', 'del_inst_days', 'allow_manual', 'attach_history',
                 'notify_on_error'],
                {'enabled': 'Enabled', 'category_no': 'Category', 'folder_no': 'Folder',
                 'del_inst_days': 'Delete After (days)', 'allow_manual': 'Manual Start',
                 'attach_history': 'Attach History', 'notify_on_error': 'Error Notification'}
            )

            nested_changes = self._compare_workflow_tasks(wf_a.tasks, wf_b.tasks)

            if field_changes or nested_changes:
                changes.append(ObjectChange(
                    object_type='Workflow',
                    object_name=wf_b.name,
                    object_id=self._get_object_id(wf_b),
                    change_type='modified',
                    field_changes=field_changes,
                    nested_changes=nested_changes
                ))

        return changes

    def _compare_workflow_tasks(
        self,
        tasks_a: List[WorkflowTask],
        tasks_b: List[WorkflowTask]
    ) -> List[ObjectChange]:
        """Compare tasks within a workflow."""
        matched, removed, added = self._match_objects(
            tasks_a, tasks_b,
            id_field='id',
            name_field='name',
            num_field='task_no'
        )

        changes = []

        for task in added:
            changes.append(ObjectChange(
                object_type='Task',
                object_name=task.name,
                object_id=self._get_object_id(task),
                change_type='added',
                extra_info={'type': task.type_name}
            ))

        for task in removed:
            changes.append(ObjectChange(
                object_type='Task',
                object_name=task.name,
                object_id=self._get_object_id(task),
                change_type='removed',
                extra_info={'type': task.type_name}
            ))

        for task_a, task_b in matched:
            field_changes = self._compare_simple_fields(
                task_a, task_b,
                ['name', 'type_no', 'duration', 'seq_pos', 'disable_delegation',
                 'action_type', 'init_script'],
                {'type_no': 'Type', 'seq_pos': 'Position', 'disable_delegation': 'Delegation Disabled',
                 'action_type': 'Action Type', 'init_script': 'Init Script'}
            )

            # Compare transitions
            trans_changes = self._compare_transitions(task_a.transitions, task_b.transitions)

            if field_changes or trans_changes:
                changes.append(ObjectChange(
                    object_type='Task',
                    object_name=task_b.name,
                    object_id=self._get_object_id(task_b),
                    change_type='modified',
                    field_changes=field_changes,
                    nested_changes=trans_changes
                ))

        return changes

    def _compare_transitions(
        self,
        trans_a: List[WorkflowTransition],
        trans_b: List[WorkflowTransition]
    ) -> List[ObjectChange]:
        """Compare transitions within a task."""
        # Transitions don't have reliable unique IDs, so we match by composite key:
        # (action_text, task_to_no) which should be unique within a task

        def trans_key(t):
            return (t.action_text or t.name or '', t.task_to_no)

        trans_a_by_key = {trans_key(t): t for t in trans_a}
        trans_b_by_key = {trans_key(t): t for t in trans_b}

        keys_a = set(trans_a_by_key.keys())
        keys_b = set(trans_b_by_key.keys())

        added_keys = keys_b - keys_a
        removed_keys = keys_a - keys_b
        common_keys = keys_a & keys_b

        changes = []

        for key in added_keys:
            trans = trans_b_by_key[key]
            changes.append(ObjectChange(
                object_type='Transition',
                object_name=trans.name or trans.action_text or f"→ Task {trans.task_to_no}",
                object_id=f"{trans.action_text}:{trans.task_to_no}",
                change_type='added'
            ))

        for key in removed_keys:
            trans = trans_a_by_key[key]
            changes.append(ObjectChange(
                object_type='Transition',
                object_name=trans.name or trans.action_text or f"→ Task {trans.task_to_no}",
                object_id=f"{trans.action_text}:{trans.task_to_no}",
                change_type='removed'
            ))

        # For common transitions, compare their other properties (like condition)
        for key in common_keys:
            tr_a = trans_a_by_key[key]
            tr_b = trans_b_by_key[key]
            # Only compare condition since action_text and task_to_no are the key
            field_changes = self._compare_simple_fields(
                tr_a, tr_b,
                ['condition'],
                {'condition': 'Condition'}
            )
            if field_changes:
                changes.append(ObjectChange(
                    object_type='Transition',
                    object_name=tr_b.name or tr_b.action_text or f"→ Task {tr_b.task_to_no}",
                    object_id=f"{tr_b.action_text}:{tr_b.task_to_no}",
                    change_type='modified',
                    field_changes=field_changes
                ))

        return changes

    # =========================================================================
    # Role Comparison
    # =========================================================================

    def _compare_roles(self) -> List[ObjectChange]:
        """Compare roles between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.roles,
            self.config_b.roles,
            id_field='id',
            name_field='name',
            num_field='role_no'
        )

        changes = []

        for role in added:
            changes.append(ObjectChange(
                object_type='Role',
                object_name=role.name,
                object_id=self._get_object_id(role),
                change_type='added',
                extra_info={'is_deny': role.is_deny, 'permissions': role.permission_names}
            ))

        for role in removed:
            changes.append(ObjectChange(
                object_type='Role',
                object_name=role.name,
                object_id=self._get_object_id(role),
                change_type='removed',
                extra_info={'is_deny': role.is_deny, 'permissions': role.permission_names}
            ))

        for role_a, role_b in matched:
            field_changes = self._compare_simple_fields(
                role_a, role_b,
                ['name', 'description', 'is_deny', 'permissions'],
                {'is_deny': 'Is Deny Role', 'permissions': 'Permissions'}
            )

            # Compare assigned users
            users_a = set(u.user_name for u in role_a.users)
            users_b = set(u.user_name for u in role_b.users)
            if users_a != users_b:
                field_changes.append(FieldChange(
                    field_name='Assigned Users',
                    old_value=sorted(users_a),
                    new_value=sorted(users_b),
                    change_type='modified'
                ))

            if field_changes:
                changes.append(ObjectChange(
                    object_type='Role',
                    object_name=role_b.name,
                    object_id=self._get_object_id(role_b),
                    change_type='modified',
                    field_changes=field_changes
                ))

        return changes

    # =========================================================================
    # User Comparison
    # =========================================================================

    def _compare_users(self) -> List[ObjectChange]:
        """Compare users and groups between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.users,
            self.config_b.users,
            id_field='id',
            name_field='user_name',
            num_field='user_no'
        )

        changes = []

        for user in added:
            obj_type = 'Group' if user.user_type == 2 else 'User'
            changes.append(ObjectChange(
                object_type=obj_type,
                object_name=user.display_name or user.user_name,
                object_id=self._get_object_id(user),
                change_type='added',
                extra_info={'email': user.email}
            ))

        for user in removed:
            obj_type = 'Group' if user.user_type == 2 else 'User'
            changes.append(ObjectChange(
                object_type=obj_type,
                object_name=user.display_name or user.user_name,
                object_id=self._get_object_id(user),
                change_type='removed',
                extra_info={'email': user.email}
            ))

        for user_a, user_b in matched:
            obj_type = 'Group' if user_b.user_type == 2 else 'User'

            field_changes = self._compare_simple_fields(
                user_a, user_b,
                ['user_name', 'display_name', 'email', 'domain', 'description'],
                {}
            )

            # Compare group members if this is a group
            if user_a.members or user_b.members:
                members_a = set(m.user_name for m in user_a.members)
                members_b = set(m.user_name for m in user_b.members)
                if members_a != members_b:
                    field_changes.append(FieldChange(
                        field_name='Members',
                        old_value=sorted(members_a),
                        new_value=sorted(members_b),
                        change_type='modified'
                    ))

            if field_changes:
                changes.append(ObjectChange(
                    object_type=obj_type,
                    object_name=user_b.display_name or user_b.user_name,
                    object_id=self._get_object_id(user_b),
                    change_type='modified',
                    field_changes=field_changes
                ))

        return changes

    # =========================================================================
    # Folder Comparison
    # =========================================================================

    def _compare_folders(self) -> List[ObjectChange]:
        """Compare folders between configurations."""
        # Flatten folder hierarchies for comparison
        folders_a = self._flatten_folders(self.config_a.folders)
        folders_b = self._flatten_folders(self.config_b.folders)

        matched, removed, added = self._match_objects(
            folders_a, folders_b,
            id_field='id',
            name_field='name',
            num_field='folder_no'
        )

        changes = []

        for folder in added:
            changes.append(ObjectChange(
                object_type='Folder',
                object_name=folder.name,
                object_id=self._get_object_id(folder),
                change_type='added',
                extra_info={'type': folder.folder_type_name}
            ))

        for folder in removed:
            changes.append(ObjectChange(
                object_type='Folder',
                object_name=folder.name,
                object_id=self._get_object_id(folder),
                change_type='removed',
                extra_info={'type': folder.folder_type_name}
            ))

        for fld_a, fld_b in matched:
            field_changes = self._compare_simple_fields(
                fld_a, fld_b,
                ['name', 'folder_type', 'parent_no'],
                {'folder_type': 'Type', 'parent_no': 'Parent Folder'}
            )
            if field_changes:
                changes.append(ObjectChange(
                    object_type='Folder',
                    object_name=fld_b.name,
                    object_id=self._get_object_id(fld_b),
                    change_type='modified',
                    field_changes=field_changes
                ))

        return changes

    def _flatten_folders(self, folders: List[Folder]) -> List[Folder]:
        """Flatten folder hierarchy into a flat list."""
        result = []
        for folder in folders:
            result.append(folder)
            result.extend(self._flatten_folders(folder.children))
        return result

    # =========================================================================
    # EForm Comparison
    # =========================================================================

    def _compare_eforms(self) -> List[ObjectChange]:
        """Compare EForms between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.eforms,
            self.config_b.eforms,
            id_field='id',
            name_field='name',
            num_field='form_no'
        )

        changes = []

        for eform in added:
            changes.append(ObjectChange(
                object_type='EForm',
                object_name=eform.name,
                object_id=self._get_object_id(eform),
                change_type='added',
                extra_info={'version': eform.version}
            ))

        for eform in removed:
            changes.append(ObjectChange(
                object_type='EForm',
                object_name=eform.name,
                object_id=self._get_object_id(eform),
                change_type='removed',
                extra_info={'version': eform.version}
            ))

        for ef_a, ef_b in matched:
            field_changes = self._compare_simple_fields(
                ef_a, ef_b,
                ['name', 'version', 'folder_no'],
                {'folder_no': 'Folder'}
            )

            # Compare components (simplified - just check if different)
            comp_count_a = self._count_components(ef_a.components)
            comp_count_b = self._count_components(ef_b.components)
            if comp_count_a != comp_count_b:
                field_changes.append(FieldChange(
                    field_name='Component Count',
                    old_value=comp_count_a,
                    new_value=comp_count_b,
                    change_type='modified'
                ))

            if field_changes:
                changes.append(ObjectChange(
                    object_type='EForm',
                    object_name=ef_b.name,
                    object_id=self._get_object_id(ef_b),
                    change_type='modified',
                    field_changes=field_changes
                ))

        return changes

    def _count_components(self, components: List[EFormComponent]) -> int:
        """Count total components including nested."""
        count = len(components)
        for comp in components:
            if comp.children:
                count += self._count_components(comp.children)
        return count

    # =========================================================================
    # Query Comparison
    # =========================================================================

    def _compare_queries(self) -> List[ObjectChange]:
        """Compare queries between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.queries,
            self.config_b.queries,
            id_field='id',
            name_field='name',
            num_field='query_no'
        )

        changes = []

        for query in added:
            changes.append(ObjectChange(
                object_type='Query',
                object_name=query.name,
                object_id=self._get_object_id(query),
                change_type='added'
            ))

        for query in removed:
            changes.append(ObjectChange(
                object_type='Query',
                object_name=query.name,
                object_id=self._get_object_id(query),
                change_type='removed'
            ))

        for q_a, q_b in matched:
            field_changes = self._compare_simple_fields(
                q_a, q_b,
                ['name', 'description', 'category_no', 'folder_no'],
                {'category_no': 'Category', 'folder_no': 'Folder'}
            )
            if field_changes:
                changes.append(ObjectChange(
                    object_type='Query',
                    object_name=q_b.name,
                    object_id=self._get_object_id(q_b),
                    change_type='modified',
                    field_changes=field_changes
                ))

        return changes

    # =========================================================================
    # Dictionary Comparison
    # =========================================================================

    def _compare_dictionaries(self) -> List[ObjectChange]:
        """Compare keyword dictionaries between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.keyword_dictionaries,
            self.config_b.keyword_dictionaries,
            id_field='id',
            name_field='name',
            num_field='dictionary_no'
        )

        changes = []

        for d in added:
            changes.append(ObjectChange(
                object_type='Dictionary',
                object_name=d.name,
                object_id=self._get_object_id(d),
                change_type='added',
                extra_info={'keyword_count': len(d.keywords)}
            ))

        for d in removed:
            changes.append(ObjectChange(
                object_type='Dictionary',
                object_name=d.name,
                object_id=self._get_object_id(d),
                change_type='removed',
                extra_info={'keyword_count': len(d.keywords)}
            ))

        for d_a, d_b in matched:
            field_changes = self._compare_simple_fields(
                d_a, d_b,
                ['name', 'description', 'folder_no'],
                {'folder_no': 'Folder'}
            )

            # Compare keywords
            kw_a = set(kw.value for kw in d_a.keywords)
            kw_b = set(kw.value for kw in d_b.keywords)
            added_kw = kw_b - kw_a
            removed_kw = kw_a - kw_b

            nested_changes = []
            for kw in added_kw:
                nested_changes.append(ObjectChange(
                    object_type='Keyword',
                    object_name=kw,
                    object_id=kw,
                    change_type='added'
                ))
            for kw in removed_kw:
                nested_changes.append(ObjectChange(
                    object_type='Keyword',
                    object_name=kw,
                    object_id=kw,
                    change_type='removed'
                ))

            if field_changes or nested_changes:
                changes.append(ObjectChange(
                    object_type='Dictionary',
                    object_name=d_b.name,
                    object_id=self._get_object_id(d_b),
                    change_type='modified',
                    field_changes=field_changes,
                    nested_changes=nested_changes
                ))

        return changes

    # =========================================================================
    # TreeView Comparison
    # =========================================================================

    def _compare_treeviews(self) -> List[ObjectChange]:
        """Compare tree views between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.tree_views,
            self.config_b.tree_views,
            id_field='id',
            name_field='name',
            num_field='treeview_no'
        )

        changes = []

        for tv in added:
            changes.append(ObjectChange(
                object_type='TreeView',
                object_name=tv.name,
                object_id=self._get_object_id(tv),
                change_type='added',
                extra_info={'level_count': len(tv.levels)}
            ))

        for tv in removed:
            changes.append(ObjectChange(
                object_type='TreeView',
                object_name=tv.name,
                object_id=self._get_object_id(tv),
                change_type='removed',
                extra_info={'level_count': len(tv.levels)}
            ))

        for tv_a, tv_b in matched:
            field_changes = self._compare_simple_fields(
                tv_a, tv_b,
                ['name', 'category_no', 'folder_no'],
                {'category_no': 'Category', 'folder_no': 'Folder'}
            )

            # Compare levels
            if len(tv_a.levels) != len(tv_b.levels):
                field_changes.append(FieldChange(
                    field_name='Level Count',
                    old_value=len(tv_a.levels),
                    new_value=len(tv_b.levels),
                    change_type='modified'
                ))

            if field_changes:
                changes.append(ObjectChange(
                    object_type='TreeView',
                    object_name=tv_b.name,
                    object_id=self._get_object_id(tv_b),
                    change_type='modified',
                    field_changes=field_changes
                ))

        return changes

    # =========================================================================
    # Counter Comparison
    # =========================================================================

    def _compare_counters(self) -> List[ObjectChange]:
        """Compare counters between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.counters,
            self.config_b.counters,
            id_field='id',
            name_field='name',
            num_field='counter_no'
        )

        changes = []

        for c in added:
            changes.append(ObjectChange(
                object_type='Counter',
                object_name=c.name,
                object_id=self._get_object_id(c),
                change_type='added',
                extra_info={'type': c.counter_type_name, 'format': c.format_string}
            ))

        for c in removed:
            changes.append(ObjectChange(
                object_type='Counter',
                object_name=c.name,
                object_id=self._get_object_id(c),
                change_type='removed',
                extra_info={'type': c.counter_type_name, 'format': c.format_string}
            ))

        for c_a, c_b in matched:
            field_changes = self._compare_simple_fields(
                c_a, c_b,
                ['name', 'counter_type', 'format_string'],
                {'counter_type': 'Type', 'format_string': 'Format'}
            )
            if field_changes:
                changes.append(ObjectChange(
                    object_type='Counter',
                    object_name=c_b.name,
                    object_id=self._get_object_id(c_b),
                    change_type='modified',
                    field_changes=field_changes
                ))

        return changes

    # =========================================================================
    # DataType Comparison
    # =========================================================================

    def _compare_datatypes(self) -> List[ObjectChange]:
        """Compare data types between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.data_types,
            self.config_b.data_types,
            id_field='id',
            name_field='name',
            num_field='datatype_no'
        )

        changes = []

        for dt in added:
            changes.append(ObjectChange(
                object_type='DataType',
                object_name=dt.name,
                object_id=self._get_object_id(dt),
                change_type='added',
                extra_info={'table': dt.table_name, 'column_count': len(dt.columns)}
            ))

        for dt in removed:
            changes.append(ObjectChange(
                object_type='DataType',
                object_name=dt.name,
                object_id=self._get_object_id(dt),
                change_type='removed',
                extra_info={'table': dt.table_name, 'column_count': len(dt.columns)}
            ))

        for dt_a, dt_b in matched:
            field_changes = self._compare_simple_fields(
                dt_a, dt_b,
                ['name', 'table_name', 'type_group'],
                {'table_name': 'Table', 'type_group': 'Type Group'}
            )

            # Compare columns
            cols_a = set(c.col_name for c in dt_a.columns)
            cols_b = set(c.col_name for c in dt_b.columns)
            if cols_a != cols_b:
                field_changes.append(FieldChange(
                    field_name='Columns',
                    old_value=sorted(cols_a),
                    new_value=sorted(cols_b),
                    change_type='modified'
                ))

            if field_changes:
                changes.append(ObjectChange(
                    object_type='DataType',
                    object_name=dt_b.name,
                    object_id=self._get_object_id(dt_b),
                    change_type='modified',
                    field_changes=field_changes
                ))

        return changes

    # =========================================================================
    # Stamp Comparison
    # =========================================================================

    def _compare_stamps(self) -> List[ObjectChange]:
        """Compare stamps between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.stamps,
            self.config_b.stamps,
            id_field='id',
            name_field='name',
            num_field='stamp_no'
        )

        changes = []

        for s in added:
            changes.append(ObjectChange(
                object_type='Stamp',
                object_name=s.name,
                object_id=self._get_object_id(s),
                change_type='added',
                extra_info={'type': s.stamp_type_name}
            ))

        for s in removed:
            changes.append(ObjectChange(
                object_type='Stamp',
                object_name=s.name,
                object_id=self._get_object_id(s),
                change_type='removed',
                extra_info={'type': s.stamp_type_name}
            ))

        for s_a, s_b in matched:
            field_changes = self._compare_simple_fields(
                s_a, s_b,
                ['name', 'stamp_type', 'filename'],
                {'stamp_type': 'Type', 'filename': 'Filename'}
            )
            if field_changes:
                changes.append(ObjectChange(
                    object_type='Stamp',
                    object_name=s_b.name,
                    object_id=self._get_object_id(s_b),
                    change_type='modified',
                    field_changes=field_changes
                ))

        return changes

    # =========================================================================
    # Retention Policy Comparison
    # =========================================================================

    def _compare_retention_policies(self) -> List[ObjectChange]:
        """Compare retention policies between configurations."""
        matched, removed, added = self._match_objects(
            self.config_a.retention_policies,
            self.config_b.retention_policies,
            id_field='id',
            name_field='name',
            num_field='policy_no'
        )

        changes = []

        for p in added:
            changes.append(ObjectChange(
                object_type='RetentionPolicy',
                object_name=p.name,
                object_id=self._get_object_id(p),
                change_type='added',
                extra_info={'months': p.months}
            ))

        for p in removed:
            changes.append(ObjectChange(
                object_type='RetentionPolicy',
                object_name=p.name,
                object_id=self._get_object_id(p),
                change_type='removed',
                extra_info={'months': p.months}
            ))

        for p_a, p_b in matched:
            field_changes = self._compare_simple_fields(
                p_a, p_b,
                ['name', 'months', 'starting', 'purge', 'delete_disk'],
                {'months': 'Retention (months)', 'starting': 'Starting From',
                 'purge': 'Purge', 'delete_disk': 'Delete from Disk'}
            )

            # Compare assigned categories
            cats_a = set(c.category_no for c in p_a.categories)
            cats_b = set(c.category_no for c in p_b.categories)
            if cats_a != cats_b:
                field_changes.append(FieldChange(
                    field_name='Assigned Categories',
                    old_value=len(cats_a),
                    new_value=len(cats_b),
                    change_type='modified'
                ))

            if field_changes:
                changes.append(ObjectChange(
                    object_type='RetentionPolicy',
                    object_name=p_b.name,
                    object_id=self._get_object_id(p_b),
                    change_type='modified',
                    field_changes=field_changes
                ))

        return changes

    # =========================================================================
    # Role Assignment Comparison
    # =========================================================================

    def _compare_role_assignments(self) -> List[ObjectChange]:
        """Compare role assignments (security settings) between configurations."""
        # Create sets of assignment keys for comparison
        def assignment_key(ra: RoleAssignment) -> tuple:
            return (ra.obj_type, ra.obj_no, ra.role_no, ra.user_no)

        keys_a = {assignment_key(ra) for ra in self.config_a.role_assignments}
        keys_b = {assignment_key(ra) for ra in self.config_b.role_assignments}

        added_keys = keys_b - keys_a
        removed_keys = keys_a - keys_b

        changes = []

        # Find the actual objects for added/removed assignments
        ra_map_b = {assignment_key(ra): ra for ra in self.config_b.role_assignments}
        ra_map_a = {assignment_key(ra): ra for ra in self.config_a.role_assignments}

        for key in added_keys:
            ra = ra_map_b[key]
            name = f"{ra.role_name or f'Role #{ra.role_no}'} → {ra.user_name or f'User #{ra.user_no}'}"
            changes.append(ObjectChange(
                object_type='RoleAssignment',
                object_name=name,
                object_id=f"{ra.obj_type}:{ra.obj_no}:{ra.role_no}:{ra.user_no}",
                change_type='added',
                extra_info={'obj_type': ra.obj_type, 'obj_no': ra.obj_no}
            ))

        for key in removed_keys:
            ra = ra_map_a[key]
            name = f"{ra.role_name or f'Role #{ra.role_no}'} → {ra.user_name or f'User #{ra.user_no}'}"
            changes.append(ObjectChange(
                object_type='RoleAssignment',
                object_name=name,
                object_id=f"{ra.obj_type}:{ra.obj_no}:{ra.role_no}:{ra.user_no}",
                change_type='removed',
                extra_info={'obj_type': ra.obj_type, 'obj_no': ra.obj_no}
            ))

        return changes
