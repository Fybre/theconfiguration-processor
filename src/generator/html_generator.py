"""HTML documentation generator for Therefore configurations."""

from pathlib import Path
from datetime import datetime
from typing import List, Dict

from ..parser.models import (
    Configuration, Category, CaseDefinition, WorkflowProcess, Folder, Role,
    EForm, Query, KeywordDictionary, TreeView, Counter, DataType, Stamp,
    RetentionPolicy
)
from ..utils.helpers import escape_html, slugify
from .templates import (
    CSS_STYLES, JAVASCRIPT, HTML_HEAD, HTML_FOOTER, SIDEBAR_TEMPLATE,
    NAV_SECTION_TEMPLATE, NAV_ITEM_TEMPLATE, OVERVIEW_TEMPLATE,
    STAT_CARD_TEMPLATE, SECTION_TEMPLATE, CATEGORY_TEMPLATE,
    FIELDS_TABLE_TEMPLATE, FIELD_ROW_TEMPLATE, WORKFLOW_TEMPLATE,
    TASKS_TABLE_TEMPLATE, TASK_ROW_TEMPLATE, FOLDER_TREE_TEMPLATE,
    FOLDER_ITEM_TEMPLATE, ROLE_TEMPLATE, USERS_TABLE_TEMPLATE,
    EFORM_TEMPLATE, QUERY_TEMPLATE, DICTIONARY_TEMPLATE,
    TREEVIEW_TEMPLATE, COUNTER_TEMPLATE, DATATYPE_TEMPLATE, STAMP_TEMPLATE
)


class HTMLGenerator:
    """Generates HTML documentation from a Therefore configuration."""

    def __init__(self, config: Configuration, title: str = "Therefore Configuration"):
        self.config = config
        self.title = title

    def generate(self, output_path: str) -> str:
        """
        Generate HTML documentation and write to file.

        Args:
            output_path: Path to output HTML file

        Returns:
            Path to the generated file
        """
        html = self._generate_html()

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html, encoding='utf-8')

        return str(output_file)

    def generate_string(self) -> str:
        """
        Generate HTML documentation and return as string.

        Returns:
            HTML documentation as a string
        """
        return self._generate_html()

    def _generate_html(self) -> str:
        """Generate the complete HTML document."""
        parts = []

        # Head
        parts.append(HTML_HEAD.format(
            title=escape_html(self.title),
            css=CSS_STYLES
        ))

        # Layout wrapper
        parts.append('<div class="layout">')

        # Sidebar
        parts.append(self._generate_sidebar())

        # Main content
        parts.append('<main class="main-content" id="top">')
        parts.append(self._generate_overview())
        parts.append(self._generate_folders_section())  # Design Structure - right after overview
        parts.append(self._generate_case_definitions_section())
        parts.append(self._generate_categories_section())
        parts.append(self._generate_workflows_section())
        parts.append(self._generate_roles_section())
        parts.append(self._generate_users_section())
        parts.append(self._generate_eforms_section())
        parts.append(self._generate_queries_section())
        parts.append(self._generate_dictionaries_section())
        parts.append(self._generate_treeviews_section())
        parts.append(self._generate_counters_section())
        parts.append(self._generate_datatypes_section())
        parts.append(self._generate_stamps_section())
        parts.append(self._generate_retention_policies_section())
        parts.append('</main>')

        parts.append('</div>')  # Close layout

        # Footer with JavaScript
        parts.append(HTML_FOOTER.format(javascript=JAVASCRIPT))

        return '\n'.join(parts)

    def _generate_sidebar(self) -> str:
        """Generate the navigation sidebar."""
        nav_sections = []

        # Design Structure (folders) comes first - no sub-items, just a link
        if self.config.folders:
            nav_sections.append(
                '<div class="nav-section">'
                '<a href="#folders" class="nav-section-header" style="text-decoration: none;">'
                '<span class="icon">&#128193;</span>'
                'Design Structure'
                '</a>'
                '</div>'
            )

        # Filter out categories that belong to case definitions
        standalone_categories = [c for c in self.config.categories if not c.belongs_to_case_def]

        sections = [
            ("case-definitions", "Case Definitions", self.config.case_definitions),
            ("categories", "Categories", standalone_categories),
            ("workflows", "Workflows", self.config.workflows),
            ("roles", "Roles", self.config.roles),
            ("eforms", "EForms", self.config.eforms),
            ("queries", "Queries", self.config.queries),
            ("dictionaries", "Dictionaries", self.config.keyword_dictionaries),
            ("treeviews", "Tree Views", self.config.tree_views),
            ("counters", "Counters", self.config.counters),
            ("datatypes", "Data Types", self.config.data_types),
            ("stamps", "Stamps", self.config.stamps),
            ("retention-policies", "Retention Policies", self.config.retention_policies),
        ]

        # Track where to insert Users & Groups (after Roles)
        users_insert_index = None

        for section_id, title, items in sections:
            if not items:
                # Track position even if roles is empty
                if section_id == "roles":
                    users_insert_index = len(nav_sections)
                continue

            nav_items = []
            for item in items[:50]:  # Limit to 50 items in nav
                name = getattr(item, 'name', '') or getattr(item, 'title', '') or f"#{getattr(item, section_id[:-1] + '_no', '')}"
                item_id = self._get_item_id(section_id, item)
                nav_items.append(NAV_ITEM_TEMPLATE.format(
                    id=item_id,
                    name=escape_html(name[:40])
                ))

            if len(items) > 50:
                nav_items.append(f'<span class="nav-item" style="color: var(--text-muted);">... and {len(items) - 50} more</span>')

            nav_sections.append(NAV_SECTION_TEMPLATE.format(
                title=title,
                count=len(items),
                items='\n'.join(nav_items)
            ))

            # Mark position after Roles
            if section_id == "roles":
                users_insert_index = len(nav_sections)

        # Add Users & Groups section after Roles (or at the tracked position)
        if self.config.users:
            groups = [u for u in self.config.users if u.user_type == 2]
            users = [u for u in self.config.users if u.user_type == 1]
            users_section = NAV_SECTION_TEMPLATE.format(
                title="Users & Groups",
                count=len(self.config.users),
                items=f'''
                    <a href="#groups" class="nav-item">Groups ({len(groups)})</a>
                    <a href="#users" class="nav-item">Users ({len(users)})</a>
                '''
            )
            if users_insert_index is not None:
                nav_sections.insert(users_insert_index, users_section)
            else:
                nav_sections.append(users_section)

        return SIDEBAR_TEMPLATE.format(nav_sections='\n'.join(nav_sections))

    def _generate_overview(self) -> str:
        """Generate the overview/dashboard section."""
        stats = self.config.get_statistics()

        stats_cards = []
        stat_labels = [
            ("categories", "Categories"),
            ("case_definitions", "Case Definitions"),
            ("fields", "Fields"),
            ("workflows", "Workflows"),
            ("workflow_tasks", "Workflow Tasks"),
            ("folders", "Folders"),
            ("users", "Users"),
            ("groups", "Groups"),
            ("roles", "Roles"),
            ("eforms", "EForms"),
            ("queries", "Queries"),
            ("keyword_dictionaries", "Dictionaries"),
            ("tree_views", "Tree Views"),
            ("counters", "Counters"),
            ("data_types", "Data Types"),
            ("retention_policies", "Retention Policies"),
        ]

        for key, label in stat_labels:
            value = stats.get(key, 0)
            if value > 0:
                stats_cards.append(STAT_CARD_TEMPLATE.format(
                    value=value,
                    label=label
                ))

        # Generate validation warnings section
        validation_section = self._generate_validation_section()

        return OVERVIEW_TEMPLATE.format(
            title=escape_html(self.title),
            stats_cards='\n'.join(stats_cards),
            validation_section=validation_section,
            version=escape_html(self.config.version or "N/A"),
            generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def _generate_validation_section(self) -> str:
        """Generate the validation warnings section."""
        issues = self.config.validate()
        if not issues:
            return ""

        # Group by type
        errors = [i for i in issues if i['type'] == 'error']
        warnings = [i for i in issues if i['type'] == 'warning']
        infos = [i for i in issues if i['type'] == 'info']

        # Icons for each type
        icons = {
            'error': '&#10060;',    # ❌
            'warning': '&#9888;',   # ⚠️
            'info': '&#8505;'       # ℹ️
        }

        items_html = []
        for issue in errors + warnings + infos:
            icon = icons.get(issue['type'], '&#8505;')
            items_html.append(f'''
            <li class="validation-item">
                <span class="validation-icon {issue['type']}">{icon}</span>
                <div class="validation-content">
                    <div class="validation-message">{escape_html(issue['message'])}</div>
                    <div class="validation-object">
                        <span class="badge">{escape_html(issue['category'])}</span>
                        <a href="#{issue['object_id']}">{escape_html(issue['object_name'])}</a>
                    </div>
                </div>
            </li>
            ''')

        has_errors = len(errors) > 0
        card_class = "validation-card has-errors" if has_errors else "validation-card"
        title = f"Validation Issues ({len(issues)})"

        return f'''
        <div class="card {card_class} collapsible-card">
            <div class="card-header collapsible-header" onclick="this.parentElement.classList.toggle('collapsed')">
                <span class="expand-icon">&#9660;</span>
                <h2>{title}</h2>
            </div>
            <div class="card-body collapsible-body">
                <ul class="validation-list">
                    {''.join(items_html)}
                </ul>
            </div>
        </div>
        '''

    def _generate_categories_section(self) -> str:
        """Generate the categories section (excludes case-belonging categories)."""
        # Filter out categories that belong to a case definition
        standalone_categories = [c for c in self.config.categories if not c.belongs_to_case_def]

        if not standalone_categories:
            return ""

        items = []
        for category in standalone_categories:
            items.append(self._render_category(category))

        return SECTION_TEMPLATE.format(
            id="categories",
            title="Categories",
            count=len(standalone_categories),
            content='\n'.join(items)
        )

    def _render_category(self, category: Category) -> str:
        """Render a single category."""
        # Badges
        badges = []
        if category.fulltext_mode == 1:
            badges.append('<span class="badge badge-success">Full-text</span>')

        # Fields section
        fields_section = ""
        if category.fields:
            field_rows = []
            for fld in category.fields:
                # Get type name, with dictionary/datatype link if applicable
                type_display = escape_html(fld.type_name)

                if fld.type_no < 0:
                    # Check if it's a keyword dictionary reference
                    dictionary = self.config.get_dictionary_by_type_no(fld.type_no)
                    if dictionary:
                        dict_slug = slugify(dictionary.name) or str(abs(dictionary.dictionary_no))
                        type_display = f'<a href="#dictionary-{dict_slug}">{escape_html(dictionary.name)}</a>'
                    else:
                        # Check if it's a datatype/referenced table
                        datatype = self.config.get_datatype_by_type_no(fld.type_no)
                        if datatype:
                            dt_slug = slugify(datatype.name) or str(abs(datatype.datatype_no))
                            type_display = f'<a href="#datatype-{dt_slug}">{escape_html(datatype.name)}</a>'
                        else:
                            type_display = f"Reference ({fld.type_no})"

                field_rows.append(FIELD_ROW_TEMPLATE.format(
                    caption=escape_html(fld.caption),
                    field_id=escape_html(fld.field_id or fld.col_name or ""),
                    type_name=type_display,
                    length=fld.length if fld.length > 0 else "-",
                    index_type=escape_html(fld.index_type_name) if fld.index_type > 0 else "-",
                    mandatory="Yes" if fld.is_mandatory else "No"
                ))

            fields_section = FIELDS_TABLE_TEMPLATE.format(
                count=len(category.fields),
                rows='\n'.join(field_rows)
            )

        folder_path = self.config.get_folder_path(category.folder_no) if category.folder_no else "-"

        # Build security section showing role assignments
        security_section = self._render_object_security(3, category.category_no, category.sub_category_field_no)

        # Build "Used by" section showing related objects
        used_by_section = self._render_category_used_by(category)

        return CATEGORY_TEMPLATE.format(
            id=slugify(category.name) or str(abs(category.category_no)),
            name=escape_html(category.name),
            badges=' '.join(badges),
            guid=escape_html(category.id or ""),
            title=escape_html(category.title or category.name),
            description=escape_html(category.description or "-"),
            folder=escape_html(folder_path),
            fulltext_mode=escape_html(category.fulltext_mode_name),
            checkin_mode=escape_html(category.checkin_mode_name),
            empty_doc_mode="Yes" if category.empty_doc_mode else "No",
            fields_section=fields_section,
            security_section=security_section,
            used_by_section=used_by_section
        )

    def _render_category_used_by(self, category: Category) -> str:
        """Render the 'Used by' section for a category showing related objects."""
        related_items = []

        # Get workflows linked to this category
        workflows = self.config.get_workflows_for_category(category.category_no)
        for wf in workflows:
            wf_slug = slugify(wf.name) or str(abs(wf.process_no))
            related_items.append({
                'type': 'Workflow',
                'name': wf.name,
                'href': f'#workflow-{wf_slug}',
                'icon': '&#9881;',
                'badge_class': 'warning'
            })

        # Get queries linked to this category
        queries = self.config.get_queries_for_category(category.category_no)
        for q in queries:
            q_slug = slugify(q.name) or str(abs(q.query_no))
            related_items.append({
                'type': 'Query',
                'name': q.name,
                'href': f'#query-{q_slug}',
                'icon': '&#128269;',
                'badge_class': ''
            })

        # Get tree views linked to this category
        treeviews = self.config.get_treeviews_for_category(category.category_no)
        for tv in treeviews:
            tv_slug = slugify(tv.name) or str(abs(tv.treeview_no))
            related_items.append({
                'type': 'Tree View',
                'name': tv.name,
                'href': f'#treeview-{tv_slug}',
                'icon': '&#127795;',
                'badge_class': ''
            })

        if not related_items:
            return ""

        # Build HTML for related items
        items_html = []
        for item in related_items:
            badge_class = f"badge-{item['badge_class']}" if item['badge_class'] else ""
            items_html.append(
                f'<span class="used-by-item">'
                f'<span class="icon">{item["icon"]}</span>'
                f'<a href="{item["href"]}">{escape_html(item["name"])}</a>'
                f'<span class="badge {badge_class}">{item["type"]}</span>'
                f'</span>'
            )

        return f'''
        <div class="fields-list used-by-section">
            <h4>Used By ({len(related_items)} items)</h4>
            <div class="used-by-list">
                {''.join(items_html)}
            </div>
        </div>
        '''

    def _render_object_security(self, obj_type: int, obj_no: int, sub_category_field_no: int = None) -> str:
        """Render the security section for an object showing role assignments."""
        # Get role assignments for this object
        assignments = self.config.get_role_assignments_for_object(obj_type, obj_no)

        if not assignments:
            return ""

        # Group assignments by role
        role_groups = {}
        for ra in assignments:
            role_key = ra.role_no
            if role_key not in role_groups:
                role_groups[role_key] = {
                    'role_name': ra.role_name or f"Role #{ra.role_no}",
                    'role_no': ra.role_no,
                    'users': [],
                    'stop_inheritance': False
                }
            role_groups[role_key]['users'].append({
                'name': ra.user_name or f"User #{ra.user_no}",
                'user_no': ra.user_no,
                'sub_obj_no': ra.sub_obj_no
            })
            if ra.stop_inheritance:
                role_groups[role_key]['stop_inheritance'] = True

        # Build HTML
        rows = []
        for role_key, role_data in role_groups.items():
            role_slug = slugify(role_data['role_name']) or str(abs(role_data['role_no']))
            user_badges = []
            for user in role_data['users']:
                user_badges.append(f'<span class="badge badge-secondary">{escape_html(user["name"])}</span>')

            stop_badge = '<span class="badge badge-danger" title="Inheritance Stopped">&#128683;</span>' if role_data['stop_inheritance'] else ''

            rows.append(f'''
                <tr>
                    <td><a href="#role-{role_slug}">{escape_html(role_data["role_name"])}</a></td>
                    <td>{' '.join(user_badges)}</td>
                    <td>{stop_badge}</td>
                </tr>
            ''')

        # Add sub-category security note if applicable
        sub_cat_note = ""
        if sub_category_field_no:
            field = self.config.get_field_by_no(sub_category_field_no)
            if field:
                sub_cat_note = f'''
                <div class="alert alert-info" style="margin-top: 0.5rem; padding: 0.5rem;">
                    <strong>Sub-category Security:</strong> Security varies by value of field "{escape_html(field.caption)}"
                </div>
                '''

        return f'''
        <div class="fields-list security-section">
            <h4>Security ({len(assignments)} assignments)</h4>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Role</th>
                            <th>Users/Groups</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
            {sub_cat_note}
        </div>
        '''

    def _generate_case_definitions_section(self) -> str:
        """Generate the case definitions section."""
        if not self.config.case_definitions:
            return ""

        items = []
        for case_def in self.config.case_definitions:
            items.append(self._render_case_definition(case_def))

        return SECTION_TEMPLATE.format(
            id="case-definitions",
            title="Case Definitions",
            count=len(self.config.case_definitions),
            content='\n'.join(items)
        )

    def _render_case_definition(self, case_def: CaseDefinition) -> str:
        """Render a single case definition."""
        item_id = f"case-definition-{slugify(case_def.title or case_def.name) or abs(case_def.case_def_no)}"

        # Badges
        badges = []
        if case_def.checkin_mode:
            badges.append(f'<span class="badge badge-info">{escape_html(case_def.checkin_mode_name)}</span>')
        if case_def.auto_append_mode:
            badges.append(f'<span class="badge badge-secondary">{escape_html(case_def.auto_append_mode_name)}</span>')

        # Fields section
        fields_section = ""
        if case_def.fields:
            field_rows = []
            for fld in case_def.fields:
                # Get type name, with dictionary/datatype link if applicable
                type_display = escape_html(fld.type_name)
                if fld.type_no < 0:
                    # Check if it's a dictionary reference
                    dictionary = self.config.get_dictionary_by_type_no(fld.type_no)
                    if dictionary:
                        dict_id = f"dictionary-{slugify(dictionary.name) or abs(dictionary.dictionary_no)}"
                        type_display = f'<a href="#{dict_id}">📖 {escape_html(dictionary.name)}</a>'
                    else:
                        # Check if it's a datatype reference
                        datatype = self.config.get_datatype_by_type_no(fld.type_no)
                        if datatype:
                            dt_id = f"datatype-{slugify(datatype.name) or abs(datatype.datatype_no)}"
                            type_display = f'<a href="#{dt_id}">📊 {escape_html(datatype.name)}</a>'

                # Mandatory indicator
                mandatory = '<span class="badge badge-danger" title="Required">*</span>' if fld.is_mandatory else ''

                field_rows.append(FIELD_ROW_TEMPLATE.format(
                    caption=escape_html(fld.caption),
                    field_id=escape_html(fld.field_id or fld.col_name or ''),
                    type_name=type_display,
                    length=fld.length or '-',
                    index_type=escape_html(fld.index_type_name) if fld.index_type_name else '-',
                    mandatory=mandatory
                ))

            fields_section = FIELDS_TABLE_TEMPLATE.format(
                count=len(case_def.fields),
                rows=''.join(field_rows)
            )

        # Find categories that belong to this case definition and render them as expandable items
        linked_categories = self.config.get_categories_for_case_def(case_def.case_def_no)
        linked_cats_section = ""
        if linked_categories:
            cat_items = []
            for cat in linked_categories:
                cat_items.append(self._render_case_category(cat))
            linked_cats_section = f'''
            <div class="fields-list case-categories-section">
                <h4>Case Categories ({len(linked_categories)})</h4>
                <div class="case-categories-list">
                    {''.join(cat_items)}
                </div>
            </div>
            '''

        # Folder path if available
        folder_info = ""
        if case_def.folder_no:
            folder_path = self.config.get_folder_path(case_def.folder_no)
            if folder_path:
                folder_info = f'<div class="meta-info"><span class="meta-label">Folder:</span> {escape_html(folder_path)}</div>'

        description = f'<p class="description">{escape_html(case_def.description)}</p>' if case_def.description else ''

        return f'''
        <div class="card" id="{item_id}">
            <div class="card-header">
                <h3>{escape_html(case_def.title or case_def.name)}</h3>
                <div class="badges">{' '.join(badges)}</div>
            </div>
            <div class="card-body">
                {description}
                {folder_info}
                {fields_section}
                {linked_cats_section}
            </div>
        </div>
        '''

    def _render_case_category(self, category: Category) -> str:
        """Render a category as an expandable item within a case definition."""
        cat_id = f"case-cat-{slugify(category.name) or abs(category.category_no)}"

        # Badges
        badges = []
        if category.fulltext_mode == 1:
            badges.append('<span class="badge badge-success">Full-text</span>')

        # Fields table
        fields_html = ""
        if category.fields:
            field_rows = []
            for fld in category.fields:
                type_display = escape_html(fld.type_name)
                if fld.type_no < 0:
                    dictionary = self.config.get_dictionary_by_type_no(fld.type_no)
                    if dictionary:
                        dict_slug = slugify(dictionary.name) or str(abs(dictionary.dictionary_no))
                        type_display = f'<a href="#dictionary-{dict_slug}">{escape_html(dictionary.name)}</a>'
                    else:
                        datatype = self.config.get_datatype_by_type_no(fld.type_no)
                        if datatype:
                            dt_slug = slugify(datatype.name) or str(abs(datatype.datatype_no))
                            type_display = f'<a href="#datatype-{dt_slug}">{escape_html(datatype.name)}</a>'

                field_rows.append(f'''
                    <tr>
                        <td>{escape_html(fld.caption)}</td>
                        <td><code>{escape_html(fld.field_id or fld.col_name or "")}</code></td>
                        <td>{type_display}</td>
                        <td>{"Yes" if fld.is_mandatory else "No"}</td>
                    </tr>
                ''')

            fields_html = f'''
                <table class="compact-table">
                    <thead>
                        <tr>
                            <th>Caption</th>
                            <th>Field ID</th>
                            <th>Type</th>
                            <th>Required</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(field_rows)}
                    </tbody>
                </table>
            '''

        # Security section for the category
        security_section = self._render_object_security(3, category.category_no, category.sub_category_field_no)

        return f'''
        <div class="nested-item" id="{cat_id}">
            <div class="nested-item-header" onclick="this.parentElement.classList.toggle('collapsed')">
                <span class="expand-icon">&#9660;</span>
                <strong>{escape_html(category.name)}</strong>
                <span class="field-count">({len(category.fields)} fields)</span>
                {' '.join(badges)}
            </div>
            <div class="nested-item-body">
                {fields_html}
                {security_section}
            </div>
        </div>
        '''

    def _generate_workflows_section(self) -> str:
        """Generate the workflows section."""
        if not self.config.workflows:
            return ""

        items = []
        for workflow in self.config.workflows:
            items.append(self._render_workflow(workflow))

        return SECTION_TEMPLATE.format(
            id="workflows",
            title="Workflows",
            count=len(self.config.workflows),
            content='\n'.join(items)
        )

    def _render_workflow(self, workflow: WorkflowProcess) -> str:
        """Render a single workflow with enhanced details."""
        # Build task lookup map for transitions
        task_map = {task.task_no: task for task in workflow.tasks}

        # Tasks section - rendered as expandable cards
        tasks_section = ""
        if workflow.tasks:
            task_cards = []
            for task in workflow.tasks:
                task_cards.append(self._render_workflow_task(task, task_map))

            tasks_section = f'''
            <div class="fields-list">
                <h4>Tasks ({len(workflow.tasks)})</h4>
                {''.join(task_cards)}
            </div>
            '''

        folder_path = self.config.get_folder_path(workflow.folder_no) if workflow.folder_no else "-"
        category = self.config.get_category(workflow.category_no) if workflow.category_no else None
        if category:
            cat_slug = slugify(category.name) or str(abs(category.category_no))
            category_link = f'<a href="#category-{cat_slug}">{escape_html(category.name)}</a>'
        else:
            category_link = "-"

        # Badges
        badges = []
        if workflow.enabled:
            badges.append('<span class="badge badge-success">Enabled</span>')
        else:
            badges.append('<span class="badge badge-danger">Disabled</span>')
        if workflow.allow_manual:
            badges.append('<span class="badge badge-primary">Manual Start</span>')

        # Format duration
        duration_str = "-"
        if workflow.duration > 0:
            hours = workflow.duration // 60
            mins = workflow.duration % 60
            if hours > 0 and mins > 0:
                duration_str = f"{hours}h {mins}m"
            elif hours > 0:
                duration_str = f"{hours} hours"
            else:
                duration_str = f"{mins} minutes"

        return WORKFLOW_TEMPLATE.format(
            id=slugify(workflow.name) or str(abs(workflow.process_no)),
            name=escape_html(workflow.name),
            badges=' '.join(badges),
            guid=escape_html(workflow.id or ""),
            process_id=escape_html(workflow.process_id or "-"),
            description=escape_html(workflow.description or "-"),
            folder=escape_html(folder_path),
            category=category_link,
            duration=duration_str,
            del_inst_days=f"{workflow.del_inst_days} days" if workflow.del_inst_days > 0 else "-",
            allow_manual="Yes" if workflow.allow_manual else "No",
            attach_history="Yes" if workflow.attach_history else "No",
            notify_on_error=escape_html(workflow.notify_on_error) if workflow.notify_on_error else "-",
            tasks_section=tasks_section
        )

    def _render_workflow_task(self, task, task_map: dict) -> str:
        """Render a single workflow task as an expandable card."""
        # Determine badge class based on task type
        type_class = {
            1: "success",   # Start
            2: "danger",    # End
            3: "primary",   # Manual
            4: "warning"    # Automatic
        }.get(task.type_no, "")

        # Format assigned users
        assigned_users = []
        for u in task.assigned_users:
            display = u.get("display_name") or u.get("user_name", "")
            if display:
                assigned_users.append(escape_html(display))
        assigned_str = ", ".join(assigned_users) if assigned_users else "-"

        # Build transitions section
        transitions_html = ""
        if task.transitions:
            trans_items = []
            for tr in task.transitions:
                target_task = task_map.get(tr.task_to_no)
                target_name = target_task.name if target_task else f"Task {tr.task_to_no}"

                # Action text (button label)
                action = tr.action_text or tr.name or target_name

                # Condition if present - resolve field macros
                condition_html = ""
                if tr.condition:
                    # Resolve field macros like [-31] to field names
                    resolved_condition = self.config.resolve_field_macros(tr.condition)
                    # Show both resolved and original if different
                    if resolved_condition != tr.condition:
                        condition_html = f'<span class="condition" title="{escape_html(tr.condition)}">{escape_html(resolved_condition)}</span>'
                    else:
                        condition_html = f'<span class="condition">{escape_html(tr.condition)}</span>'

                trans_items.append(f'''
                <div class="transition-item">
                    <span class="transition-arrow">&#8594;</span>
                    <strong>{escape_html(action)}</strong>
                    <span style="color: var(--text-muted);">to</span>
                    <span>{escape_html(target_name)}</span>
                    {condition_html}
                </div>
                ''')

            transitions_html = f'''
            <div class="transitions-list">
                <div class="label" style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.5rem;">Transitions</div>
                {''.join(trans_items)}
            </div>
            '''

        # Script section if present
        script_html = ""
        if task.init_script:
            script_html = f'''
            <div style="margin-top: 0.75rem;">
                <div class="label" style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.25rem;">Initialization Script</div>
                <div class="script-block">{escape_html(task.init_script)}</div>
            </div>
            '''

        # Checklist section if present
        checklist_html = ""
        if task.checklist:
            items = ''.join([f'<li>{escape_html(item)}</li>' for item in task.checklist])
            checklist_html = f'''
            <div style="margin-top: 0.75rem;">
                <div class="label" style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.25rem;">Checklist</div>
                <ul class="checklist-items">{items}</ul>
            </div>
            '''

        # Notification mail section if present
        notification_html = ""
        if task.notification_subject or task.notification_message:
            notification_html = f'''
            <div style="margin-top: 0.75rem;">
                <div class="label" style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.25rem;">Notification Email</div>
                <div class="notification-preview">
                    <div class="subject">Subject: {escape_html(task.notification_subject or "(no subject)")}</div>
                    <div class="message">{task.notification_message or "(no message)"}</div>
                </div>
            </div>
            '''

        # Action type info
        action_type_html = ""
        if task.action_type:
            action_type_html = f'''
            <div class="task-info-item">
                <div class="label">Action Type</div>
                <div><code>{escape_html(task.action_type)}</code></div>
            </div>
            '''

        return f'''
        <div class="task-detail">
            <div class="task-detail-header" onclick="this.parentElement.classList.toggle('collapsed')">
                <span class="task-arrow">&#9660;</span>
                <span class="task-seq">#{task.seq_pos}</span>
                <span class="task-name">{escape_html(task.name)}</span>
                <span class="badge badge-{type_class}">{escape_html(task.type_name)}</span>
            </div>
            <div class="task-detail-body">
                <div class="task-info-grid">
                    <div class="task-info-item">
                        <div class="label">Assigned To</div>
                        <div>{assigned_str}</div>
                    </div>
                    <div class="task-info-item">
                        <div class="label">Duration</div>
                        <div>{f"{task.duration}h" if task.duration > 0 else "-"}</div>
                    </div>
                    {action_type_html}
                    <div class="task-info-item">
                        <div class="label">Delegation</div>
                        <div>{"Disabled" if task.disable_delegation else "Enabled"}</div>
                    </div>
                </div>
                {transitions_html}
                {script_html}
                {checklist_html}
                {notification_html}
            </div>
        </div>
        '''

    def _generate_folders_section(self) -> str:
        """Generate the folders section."""
        if not self.config.folders:
            return ""

        # Build mapping of folder_no to all object types
        folder_items = self._build_folder_items_map()

        tree_content = self._render_folder_tree(self.config.folders, folder_items)

        content = FOLDER_TREE_TEMPLATE.format(tree_content=tree_content)

        # Use a custom section without the count for Design Structure
        return f'''
        <section id="folders" class="section collapsible-section">
            <div class="section-header collapsible-header" onclick="this.parentElement.classList.toggle('collapsed')">
                <span class="expand-icon">&#9660;</span>
                <h2>Design Structure</h2>
            </div>
            <div class="collapsible-body">
                {content}
            </div>
        </section>
        '''

    def _build_folder_items_map(self) -> Dict[int, List[Dict]]:
        """Build a mapping of folder_no to all items in that folder."""
        folder_items: Dict[int, List[Dict]] = {}

        def add_item(folder_no, item_type, name, item_id, slug_prefix, icon, badge_class):
            if folder_no is not None:
                if folder_no not in folder_items:
                    folder_items[folder_no] = []
                folder_items[folder_no].append({
                    'type': item_type,
                    'name': name,
                    'href': f"#{slug_prefix}-{item_id}",
                    'icon': icon,
                    'badge_class': badge_class
                })

        # Categories
        for cat in self.config.categories:
            slug = slugify(cat.name) or str(abs(cat.category_no))
            add_item(cat.folder_no, 'Category', cat.name, slug, 'category', '&#128196;', 'primary')

        # Workflows
        for wf in self.config.workflows:
            slug = slugify(wf.name) or str(abs(wf.process_no))
            add_item(wf.folder_no, 'Workflow', wf.name, slug, 'workflow', '&#9881;', 'warning')

        # EForms
        for ef in self.config.eforms:
            slug = slugify(ef.name) or str(abs(ef.form_no))
            add_item(ef.folder_no, 'EForm', ef.name, slug, 'eform', '&#128221;', 'success')

        # Queries
        for q in self.config.queries:
            slug = slugify(q.name) or str(abs(q.query_no))
            add_item(q.folder_no, 'Query', q.name, slug, 'query', '&#128269;', '')

        # Dictionaries
        for d in self.config.keyword_dictionaries:
            slug = slugify(d.name) or str(abs(d.dictionary_no))
            add_item(d.folder_no, 'Dictionary', d.name, slug, 'dictionary', '&#128218;', 'primary')

        # Tree Views
        for tv in self.config.tree_views:
            slug = slugify(tv.name) or str(abs(tv.treeview_no))
            add_item(tv.folder_no, 'Tree View', tv.name, slug, 'treeview', '&#127795;', '')

        # Counters
        for c in self.config.counters:
            slug = slugify(c.name) or str(abs(c.counter_no))
            add_item(c.folder_no, 'Counter', c.name, slug, 'counter', '&#128290;', '')

        # Stamps
        for s in self.config.stamps:
            slug = slugify(s.name) or str(abs(s.stamp_no))
            add_item(s.folder_no, 'Stamp', s.name, slug, 'stamp', '&#128395;', 'danger')

        # Data Types
        for dt in self.config.data_types:
            slug = slugify(dt.name) or str(abs(dt.datatype_no))
            add_item(dt.folder_no if hasattr(dt, 'folder_no') else None, 'Data Type', dt.name, slug, 'datatype', '&#128202;', '')

        return folder_items

    def _render_folder_tree(self, folders: List[Folder], folder_items: Dict[int, List[Dict]], level: int = 0) -> str:
        """Render folder tree recursively, including all item types."""
        items = []
        for folder in folders:
            # Build children content (subfolders + items)
            children_parts = []

            # Add subfolders first
            if folder.children:
                children_parts.append(self._render_folder_tree(folder.children, folder_items, level + 1))

            # Add items in this folder (sorted by type then name)
            folder_contents = folder_items.get(folder.folder_no, [])
            # Sort by type first, then by name
            type_order = ['Category', 'Workflow', 'EForm', 'Query', 'Dictionary', 'Tree View', 'Counter', 'Stamp', 'Data Type']
            folder_contents.sort(key=lambda x: (type_order.index(x['type']) if x['type'] in type_order else 99, x['name']))

            for item in folder_contents:
                badge_class = f"badge-{item['badge_class']}" if item['badge_class'] else ""
                children_parts.append(f'''
                <div class="tree-item tree-item-object" data-type="{item['type'].lower().replace(' ', '-')}">
                    <div class="tree-item-label">
                        <span class="icon">{item['icon']}</span>
                        <a href="{item['href']}">{escape_html(item['name'])}</a>
                        <span class="badge {badge_class}">{item['type']}</span>
                    </div>
                </div>
                ''')

            children = ""
            if children_parts:
                children = f'<div class="tree">{"".join(children_parts)}</div>'

            items.append(FOLDER_ITEM_TEMPLATE.format(
                name=escape_html(folder.name),
                type=escape_html(folder.folder_type_name) if folder.folder_type > 0 else "",
                children=children
            ))

        return '\n'.join(items)

    def _flatten_folders(self, folders: List[Folder]) -> List[Folder]:
        """Flatten folder hierarchy."""
        result = []
        for folder in folders:
            result.append(folder)
            result.extend(self._flatten_folders(folder.children))
        return result

    def _generate_roles_section(self) -> str:
        """Generate the roles section."""
        if not self.config.roles:
            return ""

        items = []
        for role in self.config.roles:
            items.append(self._render_role(role))

        return SECTION_TEMPLATE.format(
            id="roles",
            title="Roles",
            count=len(self.config.roles),
            content='\n'.join(items)
        )

    def _render_role(self, role: Role) -> str:
        """Render a single role."""
        # Permissions
        permissions = '\n'.join([
            f'<span class="permission-item">{escape_html(p)}</span>'
            for p in role.permission_names
        ])

        # Users section
        users_section = ""
        if role.users:
            user_rows = []
            for user in role.users:
                user_rows.append(f'''
                <tr>
                    <td>{escape_html(user.user_name)}</td>
                    <td>{escape_html(user.display_name)}</td>
                    <td><span class="badge">{escape_html(user.user_type_name)}</span></td>
                </tr>
                ''')

            users_section = USERS_TABLE_TEMPLATE.format(
                count=len(role.users),
                rows='\n'.join(user_rows)
            )

        # Assignments section
        assignments_section = ""
        if role.assignments:
            assignment_rows = []
            for assign in role.assignments:
                assignment_rows.append(f'''
                <tr>
                    <td>{escape_html(assign.object_type_name)}</td>
                    <td>{escape_html(assign.object_name)}</td>
                </tr>
                ''')

            assignments_section = f'''
            <div class="fields-list">
                <h4>Object Assignments ({len(role.assignments)})</h4>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr><th>Object Type</th><th>Object Name</th></tr>
                        </thead>
                        <tbody>
                            {''.join(assignment_rows)}
                        </tbody>
                    </table>
                </div>
            </div>
            '''

        # Deny badge for deny roles
        deny_badge = '<span class="badge badge-danger">DENY</span>' if role.is_deny else ''

        return ROLE_TEMPLATE.format(
            id=slugify(role.name) or str(abs(role.role_no)),
            name=escape_html(role.name),
            deny_badge=deny_badge,
            guid=escape_html(role.id or ""),
            description=escape_html(role.description or "-"),
            permissions=permissions or '<span class="permission-item">None</span>',
            users_section=users_section,
            assignments_section=assignments_section
        )

    def _generate_users_section(self) -> str:
        """Generate the users and groups section."""
        if not self.config.users:
            return ""

        # Separate users and groups
        users = [u for u in self.config.users if u.user_type == 1]
        groups = [u for u in self.config.users if u.user_type == 2]

        # Build reverse lookup: user_name -> list of group names they belong to
        user_groups_map = {}
        for group in groups:
            for member in group.members:
                if member.user_name not in user_groups_map:
                    user_groups_map[member.user_name] = []
                user_groups_map[member.user_name].append(group.display_name or group.user_name)

        sections = []

        # Groups section
        if groups:
            group_items = []
            for group in groups:
                group_items.append(self._render_user_or_group(group, user_groups_map))
            sections.append(f'''
            <section id="groups" class="section">
                <div class="section-header">
                    <h2>Groups</h2>
                    <span class="count">{len(groups)} items</span>
                    <div class="section-controls">
                        <button class="expand-all-btn" title="Expand all">&#9660; Expand All</button>
                        <button class="collapse-all-btn" title="Collapse all">&#9650; Collapse All</button>
                    </div>
                </div>
                {''.join(group_items)}
            </section>
            ''')

        # Users section
        if users:
            user_items = []
            for user in users:
                user_items.append(self._render_user_or_group(user, user_groups_map))
            sections.append(f'''
            <section id="users" class="section">
                <div class="section-header">
                    <h2>Users</h2>
                    <span class="count">{len(users)} items</span>
                    <div class="section-controls">
                        <button class="expand-all-btn" title="Expand all">&#9660; Expand All</button>
                        <button class="collapse-all-btn" title="Collapse all">&#9650; Collapse All</button>
                    </div>
                </div>
                {''.join(user_items)}
            </section>
            ''')

        return '\n'.join(sections)

    def _render_user_or_group(self, user, user_groups_map=None) -> str:
        """Render a single user or group."""
        is_group = user.user_type == 2
        icon = "&#128101;" if is_group else "&#128100;"  # Group or person icon
        type_badge = "Group" if is_group else "User"
        badge_class = "primary" if is_group else ""

        # Domain info
        domain_html = ""
        if user.domain:
            domain_html = f'''
            <div class="property">
                <span class="property-label">Domain</span>
                <span class="property-value">{escape_html(user.domain)}</span>
            </div>
            '''

        # Email info
        email_html = ""
        if user.email:
            email_html = f'''
            <div class="property">
                <span class="property-label">Email</span>
                <span class="property-value">{escape_html(user.email)}</span>
            </div>
            '''

        # Description
        desc_html = ""
        if user.description:
            desc_html = f'''
            <div class="property">
                <span class="property-label">Description</span>
                <span class="property-value">{escape_html(user.description)}</span>
            </div>
            '''

        # Member of (for users) - show which groups they belong to
        member_of_html = ""
        if not is_group and user_groups_map:
            group_names = user_groups_map.get(user.user_name, [])
            if group_names:
                group_badges = ' '.join([f'<span class="badge badge-primary">{escape_html(g)}</span>' for g in group_names])
                member_of_html = f'''
                <div class="property">
                    <span class="property-label">Member of</span>
                    <span class="property-value">{group_badges}</span>
                </div>
                '''

        # Members (for groups)
        members_html = ""
        if user.members:
            member_rows = []
            for member in user.members:
                member_type = "Group" if member.user_type == 2 else "User"
                member_rows.append(f'''
                <tr>
                    <td>{escape_html(member.user_name)}</td>
                    <td>{escape_html(member.display_name)}</td>
                    <td>{escape_html(member.email or "-")}</td>
                    <td><span class="badge">{member_type}</span></td>
                </tr>
                ''')

            members_html = f'''
            <div class="fields-list">
                <h4>Members ({len(user.members)})</h4>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr><th>Username</th><th>Display Name</th><th>Email</th><th>Type</th></tr>
                        </thead>
                        <tbody>
                            {''.join(member_rows)}
                        </tbody>
                    </table>
                </div>
            </div>
            '''

        slug = slugify(user.user_name) or str(abs(user.user_no))

        return f'''
        <div id="user-{slug}" class="item-detail">
            <div class="item-detail-header">
                <span class="expand-icon">&#9660;</span>
                <span style="margin-right: 0.5rem;">{icon}</span>
                <h3>{escape_html(user.display_name or user.user_name)}</h3>
                <span class="badge badge-{badge_class}">{type_badge}</span>
                <span class="id">{escape_html(user.id or "")}</span>
            </div>
            <div class="item-detail-body">
                <div class="property-grid">
                    <div class="property">
                        <span class="property-label">Username</span>
                        <span class="property-value">{escape_html(user.user_name)}</span>
                    </div>
                    {domain_html}
                    {email_html}
                    {desc_html}
                    {member_of_html}
                </div>
                {members_html}
            </div>
        </div>
        '''

    def _generate_eforms_section(self) -> str:
        """Generate the EForms section."""
        if not self.config.eforms:
            return ""

        items = []
        for eform in self.config.eforms:
            folder_path = self.config.get_folder_path(eform.folder_no) if eform.folder_no else "-"

            # Generate components section
            components_section = ""
            if eform.components:
                total_count = self._count_eform_components(eform.components)
                components_html = self._render_eform_components(eform.components)
                components_section = f'''
                <div class="fields-list">
                    <h4>Form Components ({total_count})</h4>
                    {components_html}
                </div>
                '''

            items.append(EFORM_TEMPLATE.format(
                id=slugify(eform.name) or str(abs(eform.form_no)),
                name=escape_html(eform.name),
                guid=escape_html(eform.id or ""),
                form_id=escape_html(eform.form_id or ""),
                version=eform.version,
                folder=escape_html(folder_path),
                created_date=escape_html(eform.created_date or "-"),
                created_by=escape_html(eform.created_by or "-"),
                component_count=self._count_eform_components(eform.components) if eform.components else 0,
                components_section=components_section
            ))

        return SECTION_TEMPLATE.format(
            id="eforms",
            title="EForms",
            count=len(self.config.eforms),
            content='\n'.join(items)
        )

    def _count_eform_components(self, components) -> int:
        """Count total number of eForm components including nested ones."""
        count = 0
        for comp in components:
            count += 1
            if comp.children:
                count += self._count_eform_components(comp.children)
        return count

    def _render_eform_components(self, components, level: int = 0) -> str:
        """Render eForm components as expandable sections."""
        html_parts = []

        for comp in components:
            # Skip layout-only components without meaningful content at top level
            has_scripts = bool(
                comp.custom_default_value or
                comp.calculate_value or
                comp.validate_custom or
                comp.custom_conditional
            )
            has_data = bool(comp.default_value or comp.data_source or comp.validate_required)

            # Build component body content
            body_parts = []

            # Basic info
            info_items = []
            if comp.type:
                info_items.append(f'<strong>Type:</strong> {escape_html(comp.type)}')
            if comp.validate_required:
                info_items.append('<strong>Required:</strong> Yes')
            if comp.hidden:
                info_items.append('<strong>Hidden:</strong> Yes')
            if comp.disabled:
                info_items.append('<strong>Disabled:</strong> Yes')
            if comp.default_value:
                info_items.append(f'<strong>Default:</strong> <code>{escape_html(str(comp.default_value)[:100])}</code>')
            if comp.data_source:
                info_items.append(f'<strong>Data Source:</strong> {escape_html(comp.data_source)}')

            if info_items:
                body_parts.append(f'<div style="margin-bottom: 0.5rem;">{" | ".join(info_items)}</div>')

            # Conditional logic
            if comp.conditional_when:
                body_parts.append(f'''
                <div class="eform-script-section">
                    <div class="eform-script-label">Conditional (show when)</div>
                    <code>{escape_html(comp.conditional_when)}</code>
                </div>
                ''')

            # Custom conditional JavaScript
            if comp.custom_conditional:
                body_parts.append(f'''
                <div class="eform-script-section">
                    <div class="eform-script-label">Custom Conditional Script</div>
                    <div class="script-block">{escape_html(comp.custom_conditional)}</div>
                </div>
                ''')

            # Custom default value JavaScript
            if comp.custom_default_value:
                body_parts.append(f'''
                <div class="eform-script-section">
                    <div class="eform-script-label">Custom Default Value Script</div>
                    <div class="script-block">{escape_html(comp.custom_default_value)}</div>
                </div>
                ''')

            # Calculate value JavaScript
            if comp.calculate_value:
                body_parts.append(f'''
                <div class="eform-script-section">
                    <div class="eform-script-label">Calculate Value Script</div>
                    <div class="script-block">{escape_html(comp.calculate_value)}</div>
                </div>
                ''')

            # Validation JavaScript
            if comp.validate_custom:
                body_parts.append(f'''
                <div class="eform-script-section">
                    <div class="eform-script-label">Custom Validation Script</div>
                    <div class="script-block">{escape_html(comp.validate_custom)}</div>
                </div>
                ''')

            # Logic rules
            if comp.logic:
                logic_summary = f'{len(comp.logic)} logic rule(s)'
                body_parts.append(f'''
                <div class="eform-script-section">
                    <div class="eform-script-label">Logic Rules</div>
                    <span class="badge">{logic_summary}</span>
                </div>
                ''')

            # Children components
            if comp.children:
                children_html = self._render_eform_components(comp.children, level + 1)
                body_parts.append(f'''
                <div class="eform-children">
                    <div class="eform-script-label">Child Components ({len(comp.children)})</div>
                    {children_html}
                </div>
                ''')

            body_content = ''.join(body_parts)

            # Determine badge class based on type
            type_class = {
                'textfield': 'primary',
                'textarea': 'primary',
                'number': 'primary',
                'select': 'success',
                'checkbox': 'success',
                'radio': 'success',
                'datetime': 'warning',
                'button': 'danger',
                'hidden': '',
                'panel': '',
                'columns': '',
            }.get(comp.type, '')

            # Render component
            collapsed_class = "collapsed" if not has_scripts and level == 0 else ""
            label_display = escape_html(comp.label) if comp.label else f'<em>(no label)</em>'

            html_parts.append(f'''
            <div class="eform-component {collapsed_class}">
                <div class="eform-component-header" onclick="this.parentElement.classList.toggle('collapsed')">
                    <span class="arrow">&#9660;</span>
                    <span class="component-key">{escape_html(comp.key)}</span>
                    <span>{label_display}</span>
                    <span class="badge badge-{type_class} component-type">{escape_html(comp.type)}</span>
                    {' <span class="badge badge-warning">Script</span>' if has_scripts else ''}
                </div>
                <div class="eform-component-body">
                    {body_content if body_content else '<em>No additional configuration</em>'}
                </div>
            </div>
            ''')

        return ''.join(html_parts)

    def _generate_queries_section(self) -> str:
        """Generate the queries section."""
        if not self.config.queries:
            return ""

        items = []
        for query in self.config.queries:
            folder_path = self.config.get_folder_path(query.folder_no) if query.folder_no else "-"
            category = self.config.get_category(query.category_no) if query.category_no else None
            if category:
                cat_slug = slugify(category.name) or str(abs(category.category_no))
                category_link = f'<a href="#category-{cat_slug}">{escape_html(category.name)}</a>'
            else:
                category_link = "-"

            items.append(QUERY_TEMPLATE.format(
                id=slugify(query.name) or str(abs(query.query_no)),
                name=escape_html(query.name),
                guid=escape_html(query.id or ""),
                query_id=escape_html(query.query_id or ""),
                description=escape_html(query.description or "-"),
                category=category_link,
                folder=escape_html(folder_path)
            ))

        return SECTION_TEMPLATE.format(
            id="queries",
            title="Queries",
            count=len(self.config.queries),
            content='\n'.join(items)
        )

    def _generate_dictionaries_section(self) -> str:
        """Generate the keyword dictionaries section."""
        if not self.config.keyword_dictionaries:
            return ""

        items = []
        for dictionary in self.config.keyword_dictionaries:
            folder_path = self.config.get_folder_path(dictionary.folder_no) if dictionary.folder_no else "-"

            # Keywords section
            keywords_section = ""
            if dictionary.keywords:
                keyword_list = ', '.join([escape_html(kw.value) for kw in dictionary.keywords[:20]])
                if len(dictionary.keywords) > 20:
                    keyword_list += f' ... and {len(dictionary.keywords) - 20} more'

                keywords_section = f'''
                <div class="fields-list">
                    <h4>Keywords</h4>
                    <p style="font-size: 0.875rem; color: var(--text-muted);">{keyword_list}</p>
                </div>
                '''

            # Used by categories section
            usage = self.config.get_categories_for_dictionary(dictionary.dictionary_no)
            used_by_section = ""
            if usage:
                usage_items = []
                for cat_name, field_caption in usage:
                    cat_slug = slugify(cat_name)
                    usage_items.append(
                        f'<a href="#category-{cat_slug}" class="badge" style="text-decoration:none;">'
                        f'{escape_html(cat_name)}</a> ({escape_html(field_caption)})'
                    )
                used_by_section = f'''
                <div class="fields-list">
                    <h4>Used By ({len(usage)} fields)</h4>
                    <p style="font-size: 0.875rem;">{", ".join(usage_items)}</p>
                </div>
                '''

            items.append(DICTIONARY_TEMPLATE.format(
                id=slugify(dictionary.name) or str(abs(dictionary.dictionary_no)),
                name=escape_html(dictionary.name),
                guid=escape_html(dictionary.id or ""),
                keyword_count=len(dictionary.keywords),
                description=escape_html(dictionary.description or "-"),
                folder=escape_html(folder_path),
                keywords_section=keywords_section,
                used_by_section=used_by_section
            ))

        return SECTION_TEMPLATE.format(
            id="dictionaries",
            title="Keyword Dictionaries",
            count=len(self.config.keyword_dictionaries),
            content='\n'.join(items)
        )

    def _generate_treeviews_section(self) -> str:
        """Generate the tree views section."""
        if not self.config.tree_views:
            return ""

        items = []
        for treeview in self.config.tree_views:
            folder_path = self.config.get_folder_path(treeview.folder_no) if treeview.folder_no else "-"
            category = self.config.get_category(treeview.category_no) if treeview.category_no else None
            if category:
                cat_slug = slugify(category.name) or str(abs(category.category_no))
                category_link = f'<a href="#category-{cat_slug}">{escape_html(category.name)}</a>'
            else:
                category_link = "-"

            # Levels section
            levels_section = ""
            if treeview.levels:
                level_rows = []
                for level in treeview.levels:
                    level_rows.append(f'''
                    <tr>
                        <td>{level.level_no}</td>
                        <td>{escape_html(level.field_name)}</td>
                        <td>{escape_html(level.level_function_name)}</td>
                        <td>{escape_html(level.sort_order_name)}</td>
                    </tr>
                    ''')

                levels_section = f'''
                <div class="fields-list">
                    <h4>Levels ({len(treeview.levels)})</h4>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr><th>#</th><th>Field</th><th>Function</th><th>Sort</th></tr>
                            </thead>
                            <tbody>
                                {''.join(level_rows)}
                            </tbody>
                        </table>
                    </div>
                </div>
                '''

            items.append(TREEVIEW_TEMPLATE.format(
                id=slugify(treeview.name) or str(abs(treeview.treeview_no)),
                name=escape_html(treeview.name),
                guid=escape_html(treeview.id or ""),
                category=category_link,
                folder=escape_html(folder_path),
                levels_section=levels_section
            ))

        return SECTION_TEMPLATE.format(
            id="treeviews",
            title="Tree Views",
            count=len(self.config.tree_views),
            content='\n'.join(items)
        )

    def _generate_counters_section(self) -> str:
        """Generate the counters section."""
        if not self.config.counters:
            return ""

        # Get counter usage map
        counter_usage = self.config.get_counter_usage()

        items = []
        for counter in self.config.counters:
            # Used by section
            usage = counter_usage.get(counter.counter_no, [])
            used_by_section = ""
            if usage:
                usage_items = []
                for cat_name, field_caption in usage:
                    cat_slug = slugify(cat_name)
                    usage_items.append(
                        f'<a href="#category-{cat_slug}" class="badge" style="text-decoration:none;">'
                        f'{escape_html(cat_name)}</a> ({escape_html(field_caption)})'
                    )
                used_by_section = f'''
                <div class="fields-list">
                    <h4>Used By ({len(usage)} fields)</h4>
                    <p style="font-size: 0.875rem;">{", ".join(usage_items)}</p>
                </div>
                '''

            items.append(COUNTER_TEMPLATE.format(
                id=slugify(counter.name) or str(abs(counter.counter_no)),
                name=escape_html(counter.name),
                guid=escape_html(counter.id or ""),
                type_name=escape_html(counter.counter_type_name),
                format_string=escape_html(counter.format_string) if counter.format_string else "-",
                used_by_section=used_by_section
            ))

        return SECTION_TEMPLATE.format(
            id="counters",
            title="Counters",
            count=len(self.config.counters),
            content='\n'.join(items)
        )

    def _generate_datatypes_section(self) -> str:
        """Generate the data types section."""
        if not self.config.data_types:
            return ""

        items = []
        for datatype in self.config.data_types:
            # Columns section
            columns_section = ""
            if datatype.columns:
                col_rows = []
                for col in datatype.columns:
                    col_rows.append(f'''
                    <tr>
                        <td>{escape_html(col.col_name)}</td>
                        <td>{escape_html(col.caption)}</td>
                        <td><span class="badge">{escape_html(col.type_name)}</span></td>
                        <td>{col.length if col.length > 0 else "-"}</td>
                        <td>{"Yes" if col.is_primary else "No"}</td>
                    </tr>
                    ''')

                columns_section = f'''
                <div class="fields-list">
                    <h4>Columns ({len(datatype.columns)})</h4>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr><th>Column</th><th>Caption</th><th>Type</th><th>Length</th><th>Primary</th></tr>
                            </thead>
                            <tbody>
                                {''.join(col_rows)}
                            </tbody>
                        </table>
                    </div>
                </div>
                '''

            items.append(DATATYPE_TEMPLATE.format(
                id=slugify(datatype.name) or str(abs(datatype.datatype_no)),
                name=escape_html(datatype.name),
                guid=escape_html(datatype.id or ""),
                type_group=escape_html(datatype.type_group_name),
                table_name=escape_html(datatype.table_name or "-"),
                columns_section=columns_section
            ))

        return SECTION_TEMPLATE.format(
            id="datatypes",
            title="Data Types",
            count=len(self.config.data_types),
            content='\n'.join(items)
        )

    def _generate_stamps_section(self) -> str:
        """Generate the stamps section."""
        if not self.config.stamps:
            return ""

        items = []
        for stamp in self.config.stamps:
            items.append(STAMP_TEMPLATE.format(
                id=slugify(stamp.name) or str(abs(stamp.stamp_no)),
                name=escape_html(stamp.name),
                guid=escape_html(stamp.id or ""),
                type_name=escape_html(stamp.stamp_type_name),
                filename=escape_html(stamp.filename or "-")
            ))

        return SECTION_TEMPLATE.format(
            id="stamps",
            title="Stamps",
            count=len(self.config.stamps),
            content='\n'.join(items)
        )

    def _generate_retention_policies_section(self) -> str:
        """Generate the retention policies section."""
        if not self.config.retention_policies:
            return ""

        items = []
        for policy in self.config.retention_policies:
            items.append(self._render_retention_policy(policy))

        return SECTION_TEMPLATE.format(
            id="retention-policies",
            title="Retention Policies",
            count=len(self.config.retention_policies),
            content='\n'.join(items)
        )

    def _render_retention_policy(self, policy: RetentionPolicy) -> str:
        """Render a single retention policy."""
        item_id = f"retention-policy-{slugify(policy.name) or abs(policy.policy_no)}"

        # Badges
        badges = []
        if policy.purge:
            badges.append('<span class="badge badge-danger">Purge</span>')
        if policy.delete_disk:
            badges.append('<span class="badge badge-warning">Delete from Disk</span>')

        # Starting field
        starting_display = escape_html(policy.starting or "-")
        if policy.starting and policy.starting.startswith("$"):
            # System field
            starting_display = f'<code>{escape_html(policy.starting)}</code>'

        # Categories section - simple list of category links
        categories_section = ""
        if policy.categories:
            cat_links = []
            for cat_assign in policy.categories:
                # Resolve category name
                cat_name = cat_assign.category_name
                if not cat_name:
                    cat = self.config.get_category(cat_assign.category_no)
                    cat_name = cat.name if cat else f"Category #{cat_assign.category_no}"
                cat_slug = slugify(cat_name) or str(abs(cat_assign.category_no))
                cat_links.append(f'<a href="#category-{cat_slug}" class="badge badge-secondary" style="margin: 0.125rem;">{escape_html(cat_name)}</a>')

            categories_section = f'''
            <div class="fields-list">
                <h4>Applies To ({len(policy.categories)} categories)</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 0.25rem;">
                    {''.join(cat_links)}
                </div>
            </div>
            '''

        return f'''
        <div class="card" id="{item_id}">
            <div class="card-header">
                <h3>{escape_html(policy.name)}</h3>
                <div class="badges">{' '.join(badges)}</div>
            </div>
            <div class="card-body">
                <div class="property-grid">
                    <div class="property">
                        <span class="property-label">Retention Period</span>
                        <span class="property-value">{policy.months} month(s)</span>
                    </div>
                    <div class="property">
                        <span class="property-label">Starting From</span>
                        <span class="property-value">{starting_display}</span>
                    </div>
                </div>
                {categories_section}
            </div>
        </div>
        '''

    def _get_item_id(self, section_id: str, item) -> str:
        """Get the HTML ID for an item."""
        # Proper singular forms for section IDs
        singular_map = {
            "categories": "category",
            "workflows": "workflow",
            "folders": "folder",
            "roles": "role",
            "eforms": "eform",
            "queries": "query",
            "dictionaries": "dictionary",
            "treeviews": "treeview",
            "counters": "counter",
            "datatypes": "datatype",
            "stamps": "stamp",
            "retention-policies": "retention-policy",
            "case-definitions": "case-definition"
        }
        singular = singular_map.get(section_id, section_id[:-1])

        name = getattr(item, 'name', '') or getattr(item, 'title', '')
        if name:
            slug = slugify(name)
            if slug:
                return f"{singular}-{slug}"

        # Fall back to numeric ID
        id_attr = {
            "categories": "category_no",
            "workflows": "process_no",
            "folders": "folder_no",
            "roles": "role_no",
            "eforms": "form_no",
            "queries": "query_no",
            "dictionaries": "dictionary_no",
            "treeviews": "treeview_no",
            "counters": "counter_no",
            "datatypes": "datatype_no",
            "stamps": "stamp_no"
        }.get(section_id, "")

        if id_attr:
            num = abs(getattr(item, id_attr, 0))
            return f"{singular}-{num}"

        return section_id
