"""Security analysis for Therefore configurations."""

from typing import Dict, List, Set, Tuple, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from ..parser.models import Configuration, Role, RoleAssignment


class SecurityAnalyzer:
    """Analyzes security configuration and generates audit reports."""

    def __init__(self, config: 'Configuration'):
        """Initialize security analyzer.

        Args:
            config: Configuration object to analyze
        """
        self.config = config

    def get_role_access_matrix(self) -> Dict[str, Dict[str, List[str]]]:
        """Generate role-based access matrix.

        Returns:
            Dict mapping role names to their access permissions:
            {
                'role_name': {
                    'categories': ['Cat1', 'Cat2'],
                    'folders': ['Folder1'],
                    'workflows': ['WF1']
                }
            }
        """
        matrix = {}

        for role in self.config.roles:
            access = {
                'categories': [],
                'folders': [],
                'workflows': [],
                'queries': [],
                'other': []
            }

            for assignment in role.assignments:
                obj_type = assignment.object_type_name or f"Type {assignment.object_type}"
                obj_name = self._get_object_name(assignment)

                if obj_type == 'Category':
                    access['categories'].append(obj_name)
                elif obj_type == 'Folder':
                    access['folders'].append(obj_name)
                elif obj_type == 'Workflow':
                    access['workflows'].append(obj_name)
                elif obj_type == 'Query':
                    access['queries'].append(obj_name)
                else:
                    access['other'].append(f"{obj_type}: {obj_name}")

            matrix[role.name] = access

        return matrix

    def get_user_access_summary(self) -> List[Dict]:
        """Get summary of what each user/group can access.

        Returns:
            List of dicts with user/group access information
        """
        user_access = defaultdict(lambda: {
            'roles': set(),
            'categories': set(),
            'folders': set(),
            'is_deny': False
        })

        for role in self.config.roles:
            for user in role.users:
                user_key = f"{user.type_name}: {user.name}" if user.type_name else user.name
                user_access[user_key]['roles'].add(role.name)

                if role.is_deny:
                    user_access[user_key]['is_deny'] = True

                # Add objects this role grants access to
                for assignment in role.assignments:
                    obj_name = self._get_object_name(assignment)
                    obj_type = assignment.object_type_name

                    if obj_type == 'Category':
                        user_access[user_key]['categories'].add(obj_name)
                    elif obj_type == 'Folder':
                        user_access[user_key]['folders'].add(obj_name)

        # Convert to list and sort
        result = []
        for user_name, access in sorted(user_access.items()):
            result.append({
                'name': user_name,
                'roles': sorted(access['roles']),
                'categories': sorted(access['categories']),
                'folders': sorted(access['folders']),
                'is_deny': access['is_deny']
            })

        return result

    def get_unsecured_objects(self) -> Dict[str, List[str]]:
        """Find objects without any security assignments.

        Returns:
            Dict with lists of unsecured objects by type
        """
        unsecured = {
            'categories': [],
            'folders': [],
            'workflows': []
        }

        # Get all secured objects
        secured_categories = set()
        secured_folders = set()
        secured_workflows = set()

        for role in self.config.roles:
            for assignment in role.assignments:
                obj_type = assignment.object_type_name
                obj_no = assignment.object_no

                if obj_type == 'Category':
                    secured_categories.add(obj_no)
                elif obj_type == 'Folder':
                    secured_folders.add(obj_no)
                elif obj_type == 'Workflow':
                    secured_workflows.add(obj_no)

        # Find unsecured categories
        for category in self.config.categories:
            if category.category_no not in secured_categories and not category.belongs_to_case_def:
                unsecured['categories'].append(category.name)

        # Find unsecured folders
        for folder in self.config.folders:
            if folder.folder_no not in secured_folders:
                path = self.config.get_folder_path(folder.folder_no)
                unsecured['folders'].append(path)

        # Find unsecured workflows
        for workflow in self.config.workflows:
            if workflow.process_no not in secured_workflows:
                unsecured['workflows'].append(workflow.name)

        return unsecured

    def get_deny_role_analysis(self) -> List[Dict]:
        """Analyze deny roles and their impact.

        Returns:
            List of deny role information dicts
        """
        deny_roles = []

        for role in self.config.roles:
            if role.is_deny:
                blocks = {
                    'categories': [],
                    'folders': [],
                    'workflows': []
                }

                for assignment in role.assignments:
                    obj_name = self._get_object_name(assignment)
                    obj_type = assignment.object_type_name

                    if obj_type == 'Category':
                        blocks['categories'].append(obj_name)
                    elif obj_type == 'Folder':
                        blocks['folders'].append(obj_name)
                    elif obj_type == 'Workflow':
                        blocks['workflows'].append(obj_name)

                affected_users = [u.name for u in role.users]

                deny_roles.append({
                    'name': role.name,
                    'description': role.description or '',
                    'blocks': blocks,
                    'affected_users': affected_users,
                    'user_count': len(affected_users)
                })

        return deny_roles

    def get_permission_conflicts(self) -> List[Dict]:
        """Find potential permission conflicts.

        Returns:
            List of objects with conflicting permissions
        """
        conflicts = []

        # Group assignments by object
        object_roles = defaultdict(lambda: {'allow': [], 'deny': []})

        for role in self.config.roles:
            for assignment in role.assignments:
                key = f"{assignment.object_type_name}:{assignment.object_no}"
                obj_name = self._get_object_name(assignment)

                role_info = {
                    'role': role.name,
                    'permission': ', '.join(role.permission_names) if role.permission_names else 'Custom'
                }

                if role.is_deny:
                    object_roles[key]['deny'].append(role_info)
                    object_roles[key]['name'] = obj_name
                    object_roles[key]['type'] = assignment.object_type_name
                else:
                    object_roles[key]['allow'].append(role_info)
                    object_roles[key]['name'] = obj_name
                    object_roles[key]['type'] = assignment.object_type_name

        # Find conflicts (objects with both allow and deny)
        for key, roles in object_roles.items():
            if roles['allow'] and roles['deny']:
                conflicts.append({
                    'object': roles['name'],
                    'type': roles['type'],
                    'allow_roles': roles['allow'],
                    'deny_roles': roles['deny']
                })

        return conflicts

    def get_overprivileged_users(self, threshold: int = 3) -> List[Dict]:
        """Find users with many roles (potentially overprivileged).

        Args:
            threshold: Number of roles to consider overprivileged

        Returns:
            List of overprivileged user information
        """
        user_roles = defaultdict(list)

        for role in self.config.roles:
            for user in role.users:
                user_key = f"{user.type_name}: {user.name}" if user.type_name else user.name
                user_roles[user_key].append({
                    'role': role.name,
                    'permission': ', '.join(role.permission_names) if role.permission_names else 'Custom',
                    'is_deny': role.is_deny
                })

        overprivileged = []
        for user_name, roles in user_roles.items():
            if len(roles) >= threshold:
                overprivileged.append({
                    'name': user_name,
                    'role_count': len(roles),
                    'roles': roles
                })

        return sorted(overprivileged, key=lambda x: x['role_count'], reverse=True)

    def _get_object_name(self, assignment: 'RoleAssignment') -> str:
        """Get the name of the object referenced by a role assignment.

        Args:
            assignment: RoleAssignment to look up

        Returns:
            Object name or ID if not found
        """
        obj_type = assignment.object_type_name
        obj_no = assignment.object_no

        if obj_type == 'Category':
            category = self.config.get_category(obj_no)
            return category.name if category else f"Category #{obj_no}"
        elif obj_type == 'Folder':
            return self.config.get_folder_path(obj_no) or f"Folder #{obj_no}"
        elif obj_type == 'Workflow':
            workflow = self.config.get_workflow(obj_no)
            return workflow.name if workflow else f"Workflow #{obj_no}"
        elif obj_type == 'Query':
            query = self.config.get_query(obj_no)
            return query.name if query else f"Query #{obj_no}"
        else:
            return f"{obj_type} #{obj_no}"
