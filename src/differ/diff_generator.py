"""HTML generator for configuration diff results."""

from typing import List, Dict
from datetime import datetime

from .. import __version__
from ..utils.helpers import escape_html
from .models import DiffResult, ObjectChange, FieldChange


class DiffHTMLGenerator:
    """Generates HTML documentation for configuration differences."""

    def __init__(self, diff_result: DiffResult):
        self.diff = diff_result

    def generate(self) -> str:
        """Generate complete HTML document for the diff."""
        parts = [
            self._generate_head(),
            '<body>',
            '<div class="diff-container">',
            self._generate_header(),
            self._generate_summary(),
            self._generate_changes_sections(),
            '</div>',
            self._generate_footer(),
            '</body>',
            '</html>'
        ]
        return '\n'.join(parts)

    def _generate_head(self) -> str:
        """Generate HTML head section."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuration Comparison</title>
    <style>
{DIFF_CSS}
    </style>
</head>'''

    def _generate_header(self) -> str:
        """Generate the header section with file names."""
        return f'''
<header class="diff-header">
    <h1>Configuration Comparison</h1>
    <div class="diff-files">
        <div class="diff-file diff-file-a">
            <span class="diff-file-label">Before:</span>
            <span class="diff-file-name">{escape_html(self.diff.file_a_name)}</span>
        </div>
        <span class="diff-vs">vs</span>
        <div class="diff-file diff-file-b">
            <span class="diff-file-label">After:</span>
            <span class="diff-file-name">{escape_html(self.diff.file_b_name)}</span>
        </div>
    </div>
</header>'''

    def _generate_summary(self) -> str:
        """Generate the summary statistics section."""
        if not self.diff.has_changes:
            return '''
<div class="diff-no-changes">
    <div class="diff-no-changes-icon">&#10003;</div>
    <h2>No Differences Found</h2>
    <p>The two configurations are identical.</p>
</div>'''

        # Build summary cards
        cards = []
        for obj_type in self.diff.object_types_with_changes:
            summary = self.diff.summary.get(obj_type)
            if summary and summary.has_changes:
                cards.append(self._render_summary_card(obj_type, summary))

        # Total changes
        total_added = sum(s.added for s in self.diff.summary.values())
        total_removed = sum(s.removed for s in self.diff.summary.values())
        total_modified = sum(s.modified for s in self.diff.summary.values())

        return f'''
<div class="diff-summary">
    <div class="diff-summary-header">
        <h2>Summary</h2>
        <div class="diff-summary-totals">
            <span class="diff-total diff-total-added">+{total_added} added</span>
            <span class="diff-total diff-total-removed">-{total_removed} removed</span>
            <span class="diff-total diff-total-modified">~{total_modified} modified</span>
        </div>
    </div>
    <div class="diff-summary-grid">
        {''.join(cards)}
    </div>
</div>'''

    def _render_summary_card(self, obj_type: str, summary) -> str:
        """Render a summary card for an object type."""
        # Make object type more readable
        display_name = self._format_object_type(obj_type)

        return f'''
<div class="diff-summary-card">
    <div class="diff-summary-card-title">{display_name}</div>
    <div class="diff-summary-card-stats">
        {f'<span class="stat-added">+{summary.added}</span>' if summary.added else ''}
        {f'<span class="stat-removed">-{summary.removed}</span>' if summary.removed else ''}
        {f'<span class="stat-modified">~{summary.modified}</span>' if summary.modified else ''}
    </div>
</div>'''

    def _format_object_type(self, obj_type: str) -> str:
        """Format object type for display."""
        # Add spaces before capitals and handle special cases
        display_names = {
            'Category': 'Categories',
            'CaseDefinition': 'Case Definitions',
            'Workflow': 'Workflows',
            'Role': 'Roles',
            'User': 'Users',
            'Group': 'Groups',
            'Folder': 'Folders',
            'EForm': 'EForms',
            'Query': 'Queries',
            'Dictionary': 'Dictionaries',
            'TreeView': 'Tree Views',
            'Counter': 'Counters',
            'DataType': 'Data Types',
            'Stamp': 'Stamps',
            'RetentionPolicy': 'Retention Policies',
            'RoleAssignment': 'Security Assignments'
        }
        return display_names.get(obj_type, obj_type)

    def _generate_changes_sections(self) -> str:
        """Generate all change sections."""
        if not self.diff.has_changes:
            return ''

        sections = []
        for obj_type in self.diff.object_types_with_changes:
            changes = self.diff.get_changes_by_type(obj_type)
            if changes:
                sections.append(self._render_changes_section(obj_type, changes))

        return '\n'.join(sections)

    def _render_changes_section(self, obj_type: str, changes: List[ObjectChange]) -> str:
        """Render a section for one object type's changes."""
        display_name = self._format_object_type(obj_type)

        # Group by change type
        added = [c for c in changes if c.change_type == 'added']
        removed = [c for c in changes if c.change_type == 'removed']
        modified = [c for c in changes if c.change_type == 'modified']

        items = []

        for change in added:
            items.append(self._render_change_item(change))

        for change in removed:
            items.append(self._render_change_item(change))

        for change in modified:
            items.append(self._render_change_item(change))

        section_id = f"diff-{obj_type.lower()}"

        return f'''
<section class="diff-section" id="{section_id}">
    <div class="diff-section-header" onclick="this.parentElement.classList.toggle('collapsed')">
        <span class="diff-section-toggle">&#9660;</span>
        <h2>{display_name}</h2>
        <span class="diff-section-count">{len(changes)} change(s)</span>
    </div>
    <div class="diff-section-body">
        {''.join(items)}
    </div>
</section>'''

    def _render_change_item(self, change: ObjectChange) -> str:
        """Render a single change item."""
        css_class = f"diff-item diff-{change.change_type}"
        icon = {
            'added': '+',
            'removed': '-',
            'modified': '~'
        }.get(change.change_type, '?')

        label = {
            'added': 'Added',
            'removed': 'Removed',
            'modified': 'Modified'
        }.get(change.change_type, 'Changed')

        # Extra info badges
        extra_badges = []
        if change.extra_info:
            for key, value in change.extra_info.items():
                if value and key not in ['obj_type', 'obj_no']:
                    if isinstance(value, list):
                        extra_badges.append(f'{len(value)} {key}')
                    elif isinstance(value, bool):
                        if value:
                            extra_badges.append(key)
                    else:
                        extra_badges.append(f'{key}: {value}')

        extra_html = ''
        if extra_badges:
            extra_html = '<div class="diff-item-extra">' + \
                ' '.join(f'<span class="diff-badge">{escape_html(str(b))}</span>' for b in extra_badges) + \
                '</div>'

        # Details section for modified items
        details_html = ''
        if change.change_type == 'modified' and (change.field_changes or change.nested_changes):
            details_html = self._render_change_details(change)

        return f'''
<div class="{css_class}">
    <div class="diff-item-header" onclick="this.parentElement.classList.toggle('expanded')">
        <span class="diff-item-icon">{icon}</span>
        <span class="diff-item-name">{escape_html(change.object_name)}</span>
        <span class="diff-item-label">{label}</span>
        {extra_html}
        {f'<span class="diff-item-expand">&#9660;</span>' if details_html else ''}
    </div>
    {details_html}
</div>'''

    def _render_change_details(self, change: ObjectChange) -> str:
        """Render the details of a modified item."""
        parts = []

        # Field changes
        if change.field_changes:
            parts.append('<div class="diff-field-changes">')
            parts.append('<div class="diff-field-changes-title">Property Changes:</div>')
            parts.append('<table class="diff-field-table">')
            parts.append('<thead><tr><th>Property</th><th>Before</th><th>After</th></tr></thead>')
            parts.append('<tbody>')

            for fc in change.field_changes:
                parts.append(f'''
<tr>
    <td class="diff-field-name">{escape_html(fc.field_name)}</td>
    <td class="diff-field-old">{escape_html(fc.display_old_value)}</td>
    <td class="diff-field-new">{escape_html(fc.display_new_value)}</td>
</tr>''')

            parts.append('</tbody></table>')
            parts.append('</div>')

        # Nested changes
        if change.nested_changes:
            nested_added = [n for n in change.nested_changes if n.change_type == 'added']
            nested_removed = [n for n in change.nested_changes if n.change_type == 'removed']
            nested_modified = [n for n in change.nested_changes if n.change_type == 'modified']

            parts.append('<div class="diff-nested-changes">')

            if nested_added:
                parts.append(f'<div class="diff-nested-section diff-nested-added">')
                parts.append(f'<div class="diff-nested-title">+ Added {change.nested_changes[0].object_type}s ({len(nested_added)}):</div>')
                parts.append('<ul class="diff-nested-list">')
                for nc in nested_added:
                    extra = ''
                    if nc.extra_info.get('type'):
                        extra = f' <span class="diff-badge">{escape_html(nc.extra_info["type"])}</span>'
                    parts.append(f'<li>{escape_html(nc.object_name)}{extra}</li>')
                parts.append('</ul></div>')

            if nested_removed:
                parts.append(f'<div class="diff-nested-section diff-nested-removed">')
                parts.append(f'<div class="diff-nested-title">- Removed {change.nested_changes[0].object_type}s ({len(nested_removed)}):</div>')
                parts.append('<ul class="diff-nested-list">')
                for nc in nested_removed:
                    parts.append(f'<li>{escape_html(nc.object_name)}</li>')
                parts.append('</ul></div>')

            if nested_modified:
                parts.append(f'<div class="diff-nested-section diff-nested-modified">')
                parts.append(f'<div class="diff-nested-title">~ Modified {change.nested_changes[0].object_type}s ({len(nested_modified)}):</div>')
                for nc in nested_modified:
                    parts.append(f'<div class="diff-nested-item">')
                    parts.append(f'<div class="diff-nested-item-name">{escape_html(nc.object_name)}</div>')
                    if nc.field_changes:
                        parts.append('<ul class="diff-nested-field-list">')
                        for fc in nc.field_changes:
                            parts.append(f'<li><strong>{escape_html(fc.field_name)}:</strong> '
                                        f'<span class="diff-old">{escape_html(fc.display_old_value)}</span> → '
                                        f'<span class="diff-new">{escape_html(fc.display_new_value)}</span></li>')
                        parts.append('</ul>')
                    parts.append('</div>')
                parts.append('</div>')

            parts.append('</div>')

        return f'<div class="diff-item-details">{"".join(parts)}</div>'

    def _generate_footer(self) -> str:
        """Generate the footer."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f'''
<footer class="diff-footer">
    <span>Generated by Therefore Config Processor v{__version__}</span>
    <span>{timestamp}</span>
</footer>
<script>
{DIFF_JS}
</script>'''


# CSS styles for diff output
DIFF_CSS = '''
:root {
    --primary-color: #2563eb;
    --success-color: #22c55e;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --bg-color: #f8fafc;
    --card-bg: #ffffff;
    --text-color: #1e293b;
    --text-muted: #64748b;
    --border-color: #e2e8f0;

    --added-bg: #dcfce7;
    --added-border: #22c55e;
    --added-text: #166534;

    --removed-bg: #fee2e2;
    --removed-border: #ef4444;
    --removed-text: #991b1b;

    --modified-bg: #fef3c7;
    --modified-border: #f59e0b;
    --modified-text: #92400e;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background-color: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
}

.diff-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

/* Header */
.diff-header {
    text-align: center;
    margin-bottom: 2rem;
}

.diff-header h1 {
    font-size: 2rem;
    margin-bottom: 1rem;
    color: var(--text-color);
}

.diff-files {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.diff-file {
    background: var(--card-bg);
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    border: 1px solid var(--border-color);
}

.diff-file-label {
    color: var(--text-muted);
    font-size: 0.875rem;
    margin-right: 0.5rem;
}

.diff-file-name {
    font-weight: 600;
}

.diff-vs {
    color: var(--text-muted);
    font-weight: 500;
}

/* No changes */
.diff-no-changes {
    text-align: center;
    padding: 4rem 2rem;
    background: var(--added-bg);
    border-radius: 12px;
    border: 2px solid var(--added-border);
}

.diff-no-changes-icon {
    font-size: 4rem;
    color: var(--added-border);
    margin-bottom: 1rem;
}

.diff-no-changes h2 {
    color: var(--added-text);
    margin-bottom: 0.5rem;
}

.diff-no-changes p {
    color: var(--text-muted);
}

/* Summary */
.diff-summary {
    background: var(--card-bg);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    padding: 1.5rem;
    margin-bottom: 2rem;
}

.diff-summary-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.diff-summary-header h2 {
    font-size: 1.25rem;
}

.diff-summary-totals {
    display: flex;
    gap: 1rem;
}

.diff-total {
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
}

.diff-total-added {
    background: var(--added-bg);
    color: var(--added-text);
}

.diff-total-removed {
    background: var(--removed-bg);
    color: var(--removed-text);
}

.diff-total-modified {
    background: var(--modified-bg);
    color: var(--modified-text);
}

.diff-summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
}

.diff-summary-card {
    background: var(--bg-color);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}

.diff-summary-card-title {
    font-size: 0.875rem;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}

.diff-summary-card-stats {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    font-weight: 600;
}

.stat-added { color: var(--added-text); }
.stat-removed { color: var(--removed-text); }
.stat-modified { color: var(--modified-text); }

/* Sections */
.diff-section {
    background: var(--card-bg);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    margin-bottom: 1rem;
    overflow: hidden;
}

.diff-section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.5rem;
    background: var(--bg-color);
    cursor: pointer;
    user-select: none;
}

.diff-section-header:hover {
    background: #f1f5f9;
}

.diff-section-toggle {
    transition: transform 0.2s;
}

.diff-section.collapsed .diff-section-toggle {
    transform: rotate(-90deg);
}

.diff-section.collapsed .diff-section-body {
    display: none;
}

.diff-section-header h2 {
    font-size: 1.125rem;
    flex: 1;
}

.diff-section-count {
    color: var(--text-muted);
    font-size: 0.875rem;
}

.diff-section-body {
    padding: 1rem;
}

/* Change items */
.diff-item {
    border-radius: 8px;
    margin-bottom: 0.5rem;
    overflow: hidden;
}

.diff-item:last-child {
    margin-bottom: 0;
}

.diff-item-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    cursor: pointer;
}

.diff-item-header:hover {
    filter: brightness(0.98);
}

.diff-item-icon {
    font-weight: 700;
    font-size: 1.25rem;
    width: 1.5rem;
    text-align: center;
}

.diff-item-name {
    font-weight: 500;
    flex: 1;
}

.diff-item-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    background: rgba(0,0,0,0.1);
}

.diff-item-extra {
    display: flex;
    gap: 0.5rem;
}

.diff-badge {
    font-size: 0.75rem;
    padding: 0.125rem 0.5rem;
    background: rgba(0,0,0,0.05);
    border-radius: 4px;
    color: var(--text-muted);
}

.diff-item-expand {
    transition: transform 0.2s;
    color: var(--text-muted);
}

.diff-item.expanded .diff-item-expand {
    transform: rotate(180deg);
}

.diff-item-details {
    display: none;
    padding: 0 1rem 1rem;
    border-top: 1px solid rgba(0,0,0,0.1);
}

.diff-item.expanded .diff-item-details {
    display: block;
}

/* Added items */
.diff-added {
    background: var(--added-bg);
    border-left: 4px solid var(--added-border);
}

.diff-added .diff-item-icon { color: var(--added-text); }
.diff-added .diff-item-label { color: var(--added-text); }

/* Removed items */
.diff-removed {
    background: var(--removed-bg);
    border-left: 4px solid var(--removed-border);
}

.diff-removed .diff-item-icon { color: var(--removed-text); }
.diff-removed .diff-item-label { color: var(--removed-text); }

/* Modified items */
.diff-modified {
    background: var(--modified-bg);
    border-left: 4px solid var(--modified-border);
}

.diff-modified .diff-item-icon { color: var(--modified-text); }
.diff-modified .diff-item-label { color: var(--modified-text); }

/* Field changes table */
.diff-field-changes {
    margin-top: 1rem;
}

.diff-field-changes-title {
    font-weight: 600;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
}

.diff-field-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
}

.diff-field-table th,
.diff-field-table td {
    padding: 0.5rem;
    text-align: left;
    border-bottom: 1px solid rgba(0,0,0,0.1);
}

.diff-field-table th {
    font-weight: 600;
    background: rgba(0,0,0,0.05);
}

.diff-field-name {
    font-weight: 500;
}

.diff-field-old {
    color: var(--removed-text);
    text-decoration: line-through;
}

.diff-field-new {
    color: var(--added-text);
}

/* Nested changes */
.diff-nested-changes {
    margin-top: 1rem;
}

.diff-nested-section {
    margin-bottom: 0.75rem;
    padding: 0.75rem;
    border-radius: 6px;
}

.diff-nested-added {
    background: var(--added-bg);
}

.diff-nested-removed {
    background: var(--removed-bg);
}

.diff-nested-modified {
    background: rgba(0,0,0,0.03);
}

.diff-nested-title {
    font-weight: 600;
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
}

.diff-nested-added .diff-nested-title { color: var(--added-text); }
.diff-nested-removed .diff-nested-title { color: var(--removed-text); }

.diff-nested-list {
    list-style: none;
    padding-left: 1rem;
}

.diff-nested-list li {
    padding: 0.25rem 0;
    font-size: 0.875rem;
}

.diff-nested-item {
    padding: 0.5rem;
    background: var(--card-bg);
    border-radius: 4px;
    margin-bottom: 0.5rem;
}

.diff-nested-item-name {
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.diff-nested-field-list {
    list-style: none;
    padding-left: 1rem;
    font-size: 0.8125rem;
}

.diff-old {
    color: var(--removed-text);
    text-decoration: line-through;
}

.diff-new {
    color: var(--added-text);
}

/* Footer */
.diff-footer {
    display: flex;
    justify-content: space-between;
    padding: 1rem;
    color: var(--text-muted);
    font-size: 0.75rem;
    border-top: 1px solid var(--border-color);
    margin-top: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
    .diff-container {
        padding: 1rem;
    }

    .diff-files {
        flex-direction: column;
    }

    .diff-summary-header {
        flex-direction: column;
        text-align: center;
    }

    .diff-summary-totals {
        justify-content: center;
    }

    .diff-footer {
        flex-direction: column;
        text-align: center;
        gap: 0.5rem;
    }
}

/* Print */
@media print {
    .diff-section-header {
        cursor: default;
    }

    .diff-section.collapsed .diff-section-body,
    .diff-item-details {
        display: block !important;
    }

    .diff-item-expand,
    .diff-section-toggle {
        display: none;
    }
}
'''

# JavaScript for interactivity
DIFF_JS = '''
// Toggle all sections
document.querySelectorAll('.diff-section-header').forEach(header => {
    // Don't add click handler here - it's in the onclick attribute
});

// Expand item details on click (for modified items)
document.querySelectorAll('.diff-item-header').forEach(header => {
    // Don't add click handler here - it's in the onclick attribute
});

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    // Press 'e' to expand all, 'c' to collapse all
    if (e.key === 'e' && !e.ctrlKey && !e.metaKey) {
        document.querySelectorAll('.diff-section').forEach(s => s.classList.remove('collapsed'));
        document.querySelectorAll('.diff-item').forEach(i => i.classList.add('expanded'));
    }
    if (e.key === 'c' && !e.ctrlKey && !e.metaKey) {
        document.querySelectorAll('.diff-section').forEach(s => s.classList.add('collapsed'));
        document.querySelectorAll('.diff-item').forEach(i => i.classList.remove('expanded'));
    }
});
'''
