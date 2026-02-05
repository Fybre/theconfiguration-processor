"""Prompt templates and context formatters for AI summary generation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..parser.models import Category, WorkflowProcess, Role, EForm, KeywordDictionary, Configuration


# System-wide overview prompt
SYSTEM_OVERVIEW_PROMPT = """You are a technical documentation assistant specializing in document management systems.

Generate a concise summary of a Therefore configuration export in this format:

[One paragraph overview describing the system's purpose and scale]

Key Highlights:
- [Bullet point about most significant aspect]
- [Bullet point about notable configuration]
- [Bullet point about security or complexity]
- [Bullet point about workflows or automation]

Keep the summary under 150 words total. Be specific with numbers and names.

IMPORTANT: Start directly with the content. Do NOT begin with phrases like "This summary", "This is", "Here is", or similar meta-commentary."""


# Category summary prompt
CATEGORY_PROMPT = """You are analyzing a document category in a document management system.

Generate a concise summary in this format:

[One paragraph describing the category's purpose and characteristics]

Key Aspects:
- [Field structure or data model]
- [Security configuration if notable]
- [Workflow integration if present]
- [Special features or validation]

Keep under 120 words total. Focus on what makes this category important or unique.

IMPORTANT: Start directly with the content. Do NOT begin with phrases like "This category", "This is", "Here is", or similar meta-commentary."""


# Workflow summary prompt
WORKFLOW_PROMPT = """You are analyzing a workflow process in a document management system.

Generate a concise summary in this format:

[One paragraph describing the workflow's business process and automation]

Key Characteristics:
- [Number and types of tasks]
- [Task assignments and routing]
- [Duration or SLA aspects]
- [Integration or automation features]

Keep under 120 words total. Emphasize the process flow and business value.

IMPORTANT: Start directly with the content. Do NOT begin with phrases like "This workflow", "This is", "Here is", or similar meta-commentary."""


# Role summary prompt
ROLE_PROMPT = """You are analyzing a security role in a document management system.

Generate a concise summary in this format:

[One paragraph describing the role's purpose and scope]

Key Details:
- [Permission level and capabilities]
- [Number and types of assignments]
- [User/group composition]
- [Access scope or restrictions]

Keep under 100 words total. Focus on security implications and access control.

IMPORTANT: Start directly with the content. Do NOT begin with phrases like "This role", "This is", "Here is", or similar meta-commentary."""


# EForm summary prompt
EFORM_PROMPT = """You are analyzing an electronic form (EForm) in a document management system for technical support staff.

Generate a concise technical summary in this format:

[One paragraph describing the form's purpose and integration]

Technical Customizations:
- [JavaScript customizations and logic]
- [Calculated fields or dynamic defaults]
- [Validation rules and conditions]
- [API integrations or data sources]

Keep under 120 words total. Focus on technical details, scripts, and customizations that support staff need to understand.

IMPORTANT: Start directly with the content. Do NOT begin with phrases like "This form", "This is", "Here is", or similar meta-commentary."""


# Dictionary summary prompt
DICTIONARY_PROMPT = """You are analyzing a keyword dictionary (dropdown list) in a document management system for technical support staff.

Generate a concise summary in this format:

[One paragraph analyzing what this dictionary is used for based on its values and usage patterns]

Key Insights:
- [Purpose inferred from keyword values]
- [Categories/fields using this dictionary]
- [Data patterns or business logic]
- [Potential use cases]

Keep under 100 words total. Focus on inferring business purpose from the data.

IMPORTANT: Start directly with the content. Do NOT begin with phrases like "This dictionary", "This is", "Here is", or similar meta-commentary."""


def format_system_overview_context(config: 'Configuration') -> str:
    """Format configuration overview for LLM summarization.

    Args:
        config: Full configuration object

    Returns:
        Formatted context string for LLM
    """
    stats = config.get_statistics()

    context = f"""Configuration Overview:
- Total Categories: {stats.get('categories', 0)}
- Total Workflows: {stats.get('workflows', 0)}
- Total Workflow Tasks: {stats.get('workflow_tasks', 0)}
- Total Folders: {stats.get('folders', 0)}
- Total Users: {stats.get('users', 0)}
- Total Groups: {stats.get('groups', 0)}
- Total Roles: {stats.get('roles', 0)}
- Total EForms: {stats.get('eforms', 0)}
- Total Queries: {stats.get('queries', 0)}
- Total Dictionaries: {stats.get('keyword_dictionaries', 0)}

Top 5 Categories:
"""
    for i, cat in enumerate(config.categories[:5], 1):
        context += f"{i}. {cat.name} ({len(cat.fields)} fields)\n"

    if config.workflows:
        context += "\nTop 5 Workflows:\n"
        for i, wf in enumerate(config.workflows[:5], 1):
            context += f"{i}. {wf.name} ({len(wf.tasks)} tasks)\n"

    return context.strip()


def format_category_context(category: 'Category', config: 'Configuration') -> str:
    """Format category details for LLM summarization.

    Args:
        category: Category to summarize
        config: Configuration object for cross-references

    Returns:
        Formatted context string for LLM
    """
    folder_path = config.get_folder_path(category.folder_no) if category.folder_no else "Root"

    context = f"""Category: {category.name}
Title: {category.title or 'N/A'}
Description: {category.description or 'No description'}
Folder: {folder_path}
Total Fields: {len(category.fields)}

Field Structure (showing first 15):
"""
    for i, field in enumerate(category.fields[:15], 1):
        field_type = field.type_name or f"Type {field.type_no}"
        context += f"{i}. {field.caption} ({field_type})"
        if field.is_mandatory:
            context += " [Required]"
        context += "\n"

    if len(category.fields) > 15:
        context += f"... and {len(category.fields) - 15} more fields\n"

    # Add workflow integration if present
    workflows = config.get_workflows_for_category(category.category_no)
    if workflows:
        context += f"\nLinked Workflows ({len(workflows)}):\n"
        for wf in workflows[:3]:
            context += f"- {wf.name}\n"

    # Add security if present
    security = config.get_role_assignments_for_object('category', category.category_no)
    if security:
        context += f"\nSecurity: {len(security)} role assignment(s)\n"

    # Full-text search
    if category.fulltext_mode == 1:
        context += "Full-text search: Enabled\n"

    return context.strip()


def format_workflow_context(workflow: 'WorkflowProcess', config: 'Configuration') -> str:
    """Format workflow details for LLM summarization.

    Args:
        workflow: Workflow to summarize
        config: Configuration object for cross-references

    Returns:
        Formatted context string for LLM
    """
    folder_path = config.get_folder_path(workflow.folder_no) if workflow.folder_no else "Root"
    category = config.get_category(workflow.category_no) if workflow.category_no else None

    context = f"""Workflow: {workflow.name}
Description: {workflow.description or 'No description'}
Folder: {folder_path}
Category: {category.name if category else 'N/A'}
Status: {'Enabled' if workflow.enabled else 'Disabled'}
Total Tasks: {len(workflow.tasks)}
Duration: {workflow.duration} hours

"""

    # Build task lookup map
    task_map = {task.task_no: task for task in workflow.tasks}

    # Find start task (type_no == 1)
    start_tasks = [t for t in workflow.tasks if t.type_no == 1]

    # Analyze workflow flow based on transitions
    if start_tasks:
        context += "Process Flow:\n"
        start_task = start_tasks[0]
        context += f"START: {start_task.name}\n"

        # Track visited tasks to avoid loops
        visited = set()

        def trace_flow(task, indent=1):
            nonlocal context
            if task.task_no in visited:
                return
            visited.add(task.task_no)

            for trans in task.transitions:
                target_task = task_map.get(trans.task_to_no)
                if target_task:
                    prefix = "  " * indent
                    action = trans.action_text or trans.name or "Next"
                    context_line = f"{prefix}→ [{action}] → {target_task.name} ({target_task.type_name})"
                    if trans.condition:
                        context_line += f" [IF: {trans.condition[:50]}...]"
                    context += context_line + "\n"

                    # Recursively trace (limit depth to 10 to avoid infinite loops)
                    if indent < 10:
                        trace_flow(target_task, indent + 1)

        trace_flow(start_task)
    else:
        # Fallback: list tasks if no start task found
        context += "Task Breakdown:\n"
        for i, task in enumerate(workflow.tasks, 1):
            context += f"{i}. {task.name} ({task.type_name})"
            if task.assigned_users:
                user_count = len(task.assigned_users)
                context += f" - {user_count} assigned user(s)"
            context += "\n"

    # Count transitions
    total_transitions = sum(len(task.transitions) for task in workflow.tasks)
    context += f"\nTotal Transitions: {total_transitions}\n"

    return context.strip()


def format_role_context(role: 'Role', config: 'Configuration') -> str:
    """Format role details for LLM summarization.

    Args:
        role: Role to summarize
        config: Configuration object for cross-references

    Returns:
        Formatted context string for LLM
    """
    context = f"""Role: {role.name}
Description: {role.description or 'No description'}
Permission Level: {', '.join(role.permission_names) if role.permission_names else f'Code {role.permission}'}
Is Deny Role: {'Yes' if role.is_deny else 'No'}
"""

    # Count assignments by type
    assignments = role.assignments
    if assignments:
        context += f"\nTotal Assignments: {len(assignments)}\n"

        # Group by object type
        by_type = {}
        for ra in assignments:
            obj_type = ra.object_type_name or f"Type {ra.object_type}"
            by_type[obj_type] = by_type.get(obj_type, 0) + 1

        context += "Assignment Breakdown:\n"
        for obj_type, count in by_type.items():
            context += f"- {obj_type}: {count}\n"

    # Show user/group composition
    if role.users:
        context += f"\nAssigned Users/Groups: {len(role.users)}\n"

    return context.strip()


def format_eform_context(eform: 'EForm', config: 'Configuration') -> str:
    """Format eform details for LLM summarization.

    Args:
        eform: EForm to summarize
        config: Configuration object for cross-references

    Returns:
        Formatted context string for LLM
    """
    folder_path = config.get_folder_path(eform.folder_no) if eform.folder_no else "Root"

    context = f"""EForm: {eform.name}
Form ID: {eform.form_id or 'N/A'}
Version: {eform.version}
Folder: {folder_path}
Total Components: {len(eform.components)}

Technical Details:
"""

    # Count customizations
    has_custom_defaults = sum(1 for c in eform.components if c.custom_default_value)
    has_calculations = sum(1 for c in eform.components if c.calculate_value)
    has_custom_validations = sum(1 for c in eform.components if c.validate_custom)
    has_conditionals = sum(1 for c in eform.components if c.custom_conditional or c.conditional_show)

    if has_custom_defaults:
        context += f"- Custom Default Values: {has_custom_defaults} component(s)\n"
    if has_calculations:
        context += f"- Calculated Fields: {has_calculations} component(s)\n"
    if has_custom_validations:
        context += f"- Custom Validations: {has_custom_validations} component(s)\n"
    if has_conditionals:
        context += f"- Conditional Logic: {has_conditionals} component(s)\n"

    # Show sample customizations (first few)
    customized_components = [c for c in eform.components if
                           c.custom_default_value or c.calculate_value or
                           c.validate_custom or c.custom_conditional]

    if customized_components:
        context += "\nCustomization Examples:\n"
        for comp in customized_components[:3]:
            context += f"\n{comp.label} ({comp.type}):\n"
            if comp.custom_default_value:
                context += f"  Default: {comp.custom_default_value[:80]}...\n"
            if comp.calculate_value:
                context += f"  Calculation: {comp.calculate_value[:80]}...\n"
            if comp.validate_custom:
                context += f"  Validation: {comp.validate_custom[:80]}...\n"
            if comp.custom_conditional:
                context += f"  Conditional: {comp.custom_conditional[:80]}...\n"

    return context.strip()


def format_dictionary_context(dictionary: 'KeywordDictionary', config: 'Configuration') -> str:
    """Format keyword dictionary details for LLM summarization.

    Args:
        dictionary: KeywordDictionary to summarize
        config: Configuration object for cross-references

    Returns:
        Formatted context string for LLM
    """
    context = f"""Dictionary: {dictionary.name}
Description: {dictionary.description or 'No description'}
Total Keywords: {len(dictionary.keywords)}

Keyword Values (showing first 20):
"""
    for i, kw in enumerate(dictionary.keywords[:20], 1):
        context += f"{i}. {kw.value}\n"

    if len(dictionary.keywords) > 20:
        context += f"... and {len(dictionary.keywords) - 20} more\n"

    # Find categories/fields that use this dictionary
    using_fields = []
    for category in config.categories:
        for field in category.fields:
            # Dictionary reference is via negative type_no (single or multi select)
            if field.type_no == dictionary.single_type_no or field.type_no == dictionary.multi_type_no:
                using_fields.append({
                    'category': category.name,
                    'field': field.caption
                })

    if using_fields:
        context += f"\nUsed By ({len(using_fields)} field(s)):\n"
        for usage in using_fields[:10]:
            context += f"- {usage['category']} > {usage['field']}\n"
        if len(using_fields) > 10:
            context += f"... and {len(using_fields) - 10} more\n"

    return context.strip()
