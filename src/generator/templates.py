"""HTML templates for documentation generation."""

# CSS styles for the documentation
CSS_STYLES = """
:root {
    --primary-color: #2563eb;
    --primary-hover: #1d4ed8;
    --secondary-color: #64748b;
    --success-color: #22c55e;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --bg-color: #f8fafc;
    --card-bg: #ffffff;
    --text-color: #1e293b;
    --text-muted: #64748b;
    --border-color: #e2e8f0;
    --sidebar-width: 280px;
    --header-height: 60px;
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

/* Layout */
.layout {
    display: flex;
    min-height: 100vh;
}

/* Sidebar */
.sidebar {
    width: var(--sidebar-width);
    background: var(--card-bg);
    border-right: 1px solid var(--border-color);
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    overflow-y: auto;
    z-index: 100;
}

.sidebar-header {
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    background: var(--card-bg);
}

.sidebar-header h1 {
    font-size: 1.1rem;
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

/* Content search */
.content-search-wrapper {
    position: relative;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.content-search {
    flex: 1;
    max-width: 400px;
    padding: 0.75rem 2.5rem 0.75rem 1rem;
    border: 2px solid var(--border-color);
    border-radius: 8px;
    font-size: 1rem;
}

.content-search:focus {
    outline: none;
    border-color: var(--primary-color);
}

.content-search-clear {
    position: absolute;
    left: 370px;
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 1.25rem;
    padding: 0;
    line-height: 1;
    display: none;
}

.content-search-wrapper.has-value .content-search-clear {
    display: block;
}

.content-search-count {
    font-size: 0.875rem;
    color: var(--text-muted);
}

.search-highlight {
    background-color: #fef08a;
    padding: 0 2px;
    border-radius: 2px;
}

/* Validation warnings */
.validation-card {
    margin-bottom: 1.5rem;
    border-left: 4px solid var(--warning-color);
}

.validation-card.has-errors {
    border-left-color: var(--danger-color);
}

/* Version warning card */
.version-warning-card {
    margin-bottom: 1.5rem;
    border-left: 4px solid var(--warning-color);
    background: #fffbeb;
}

.version-warning-card .card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: #fef3c7;
}

.version-warning-card .card-header h2 {
    margin: 0;
    color: #92400e;
}

.version-warning-card .warning-icon {
    font-size: 1.25rem;
    color: var(--warning-color);
}

.version-warning-card .card-body p {
    color: #78350f;
    margin: 0;
}

.root-security-card {
    margin-bottom: 1.5rem;
    border-left: 4px solid var(--primary-color);
}

.root-security-card .card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.root-security-card .card-header h2 {
    margin: 0;
}

.validation-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.validation-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border-color);
}

.validation-item:last-child {
    border-bottom: none;
}

.validation-icon {
    font-size: 1rem;
    flex-shrink: 0;
}

.validation-icon.error { color: var(--danger-color); }
.validation-icon.warning { color: var(--warning-color); }
.validation-icon.info { color: var(--primary-color); }

.validation-content {
    flex: 1;
}

.validation-message {
    font-size: 0.875rem;
}

.validation-object {
    font-size: 0.75rem;
    color: var(--text-muted);
}

.validation-object a {
    color: var(--primary-color);
}

/* Used By section */
.used-by-section {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
}

.used-by-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.used-by-item {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.35rem 0.65rem;
    background-color: var(--bg-secondary);
    border-radius: 4px;
    font-size: 0.875rem;
}

.used-by-item .icon {
    font-size: 0.9rem;
}

.used-by-item a {
    color: var(--primary-color);
    text-decoration: none;
}

.used-by-item a:hover {
    text-decoration: underline;
}

.used-by-item .badge {
    font-size: 0.65rem;
    padding: 0.1rem 0.3rem;
}

.sidebar-search-wrapper {
    position: relative;
    width: 100%;
}

.sidebar-search {
    width: 100%;
    padding: 0.5rem;
    padding-right: 2rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-size: 0.875rem;
}

.search-clear-btn {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 1rem;
    padding: 0;
    line-height: 1;
    display: none;
}

.search-clear-btn:hover {
    color: var(--text-color);
}

.sidebar-search-wrapper.has-value .search-clear-btn {
    display: block;
}

.sidebar-controls {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.sidebar-btn {
    flex: 1;
    padding: 0.25rem 0.5rem;
    font-size: 0.7rem;
    border: 1px solid var(--border-color);
    background: var(--bg-color);
    border-radius: 4px;
    cursor: pointer;
    color: var(--text-muted);
}

.sidebar-btn:hover {
    background: var(--border-color);
    color: var(--text-color);
}

.sidebar-nav {
    padding: 0.5rem 0;
}

.nav-section {
    margin-bottom: 0.25rem;
}

.nav-section-header {
    display: flex;
    align-items: center;
    padding: 0.5rem 1rem;
    cursor: pointer;
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--text-color);
    transition: background 0.2s;
}

.nav-section-header:hover {
    background: var(--bg-color);
}

.nav-section-header .icon {
    margin-right: 0.5rem;
    transition: transform 0.2s;
}

.nav-section-header .count {
    margin-left: auto;
    font-size: 0.75rem;
    color: var(--text-muted);
    background: var(--bg-color);
    padding: 0.125rem 0.375rem;
    border-radius: 10px;
}

.nav-section.collapsed .nav-section-header .icon {
    transform: rotate(-90deg);
}

.nav-section.collapsed .nav-items {
    display: none;
}

.nav-items {
    padding-left: 1.5rem;
}

.nav-item {
    display: block;
    padding: 0.375rem 1rem;
    color: var(--text-muted);
    text-decoration: none;
    font-size: 0.8125rem;
    border-left: 2px solid transparent;
    transition: all 0.2s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.nav-item:hover {
    color: var(--primary-color);
    background: var(--bg-color);
    border-left-color: var(--primary-color);
}

.nav-item.active {
    color: var(--primary-color);
    border-left-color: var(--primary-color);
    font-weight: 500;
}

/* Main Content */
.main-content {
    margin-left: var(--sidebar-width);
    flex: 1;
    padding: 2rem;
    max-width: 1200px;
}

/* Header */
.page-header {
    margin-bottom: 2rem;
}

.page-header h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.page-header .subtitle {
    color: var(--text-muted);
}

/* Cards */
.card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    margin-bottom: 1.5rem;
    overflow: hidden;
}

.card-header {
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.card-header h2, .card-header h3 {
    font-size: 1rem;
    font-weight: 600;
}

.card-body {
    padding: 1.25rem;
}

/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.25rem;
    text-align: center;
}

.stat-card .stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary-color);
}

.stat-card .stat-label {
    font-size: 0.875rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
}

/* Tables */
.table-responsive {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

th {
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--text-muted);
    background: var(--bg-color);
}

tr:hover {
    background: var(--bg-color);
}

/* Badges */
.badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    font-weight: 500;
    border-radius: 4px;
    background: var(--bg-color);
    color: var(--text-muted);
}

.badge-primary {
    background: #dbeafe;
    color: var(--primary-color);
}

.badge-success {
    background: #dcfce7;
    color: #16a34a;
}

.badge-warning {
    background: #fef3c7;
    color: #d97706;
}

.badge-danger {
    background: #fee2e2;
    color: #dc2626;
}

.badge-logic {
    background: #e0e7ff;
    color: #4338ca;
}

.badge-info {
    background: #cffafe;
    color: #0891b2;
}

.badge-secondary {
    background: #e5e7eb;
    color: #4b5563;
}

/* AI Summary */
.ai-summary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
    color: white;
}

.ai-summary-badge {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
    opacity: 0.9;
}

.ai-summary-content {
    font-size: 0.95rem;
    line-height: 1.6;
    white-space: pre-wrap;
}

/* Dark mode support for AI summary */
@media (prefers-color-scheme: dark) {
    .ai-summary {
        background: linear-gradient(135deg, #4c51bf 0%, #553c9a 100%);
    }
}

/* Section */
.section {
    margin-bottom: 3rem;
}

.section-header {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--primary-color);
}

.section-header h2 {
    font-size: 1.5rem;
}

.section-header .count {
    margin-left: 0.75rem;
    font-size: 0.875rem;
    color: var(--text-muted);
}

.section-header .section-controls {
    margin-left: auto;
    display: flex;
    gap: 0.5rem;
}

.section-controls button {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    border: 1px solid var(--border-color);
    background: var(--card-bg);
    border-radius: 4px;
    cursor: pointer;
    color: var(--text-muted);
}

.section-controls button:hover {
    background: var(--bg-color);
    color: var(--text-color);
}

/* Item Detail */
.item-detail {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    margin-bottom: 1.5rem;
}

.item-detail-header {
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.item-detail-header h3 {
    font-size: 1.125rem;
    margin: 0;
}

.item-detail-header .id {
    font-size: 0.75rem;
    color: var(--text-muted);
    font-family: monospace;
}

.item-detail-body {
    padding: 1.25rem;
}

.item-detail.collapsed .item-detail-body {
    display: none;
}

.item-detail-header .expand-icon {
    margin-right: 0.5rem;
    transition: transform 0.2s;
}

.item-detail.collapsed .item-detail-header .expand-icon {
    transform: rotate(-90deg);
}

/* Collapsible cards and sections */
.collapsible-header {
    cursor: pointer;
    display: flex;
    align-items: center;
}

.collapsible-header .expand-icon {
    margin-right: 0.5rem;
    transition: transform 0.2s;
}

.collapsible-card.collapsed .collapsible-body,
.collapsible-section.collapsed .collapsible-body {
    display: none;
}

.collapsible-card.collapsed .expand-icon,
.collapsible-section.collapsed .expand-icon {
    transform: rotate(-90deg);
}

.collapsible-header:hover {
    background-color: var(--bg-secondary);
}

.card-header.collapsible-header {
    border-radius: 8px 8px 0 0;
}

.collapsible-card.collapsed .card-header.collapsible-header {
    border-radius: 8px;
}

/* Nested expandable items (for case categories) */
.nested-item {
    border: 1px solid var(--border-color);
    border-radius: 6px;
    margin-bottom: 0.5rem;
    background: var(--bg-primary);
}

.nested-item-header {
    padding: 0.75rem 1rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--bg-secondary);
    border-radius: 6px;
}

.nested-item-header:hover {
    background: var(--bg-tertiary, #e5e7eb);
}

.nested-item-header .expand-icon {
    transition: transform 0.2s;
}

.nested-item.collapsed .nested-item-header {
    border-radius: 6px;
}

.nested-item.collapsed .nested-item-body {
    display: none;
}

.nested-item.collapsed .expand-icon {
    transform: rotate(-90deg);
}

.nested-item-body {
    padding: 1rem;
    border-top: 1px solid var(--border-color);
}

.nested-item-header .field-count {
    color: var(--text-muted);
    font-size: 0.875rem;
}

.nested-item-header .category-no {
    color: var(--text-muted);
    font-size: 0.75rem;
    margin-left: auto;
}

.compact-table {
    width: 100%;
    font-size: 0.875rem;
}

.compact-table th,
.compact-table td {
    padding: 0.5rem;
}

.case-categories-section {
    margin-top: 1rem;
}

/* Property Grid */
.property-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
}

.property {
    display: flex;
    flex-direction: column;
}

.property-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
}

.property-value {
    font-size: 0.875rem;
}

/* Fields List */
.fields-list {
    margin-top: 1rem;
}

.fields-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.75rem;
}

.fields-header h4 {
    font-size: 0.875rem;
    margin: 0;
    color: var(--text-muted);
}

.label-toggle {
    font-size: 0.75rem;
    cursor: pointer;
    color: var(--primary-color);
    padding: 0.25rem 0.5rem;
    border: 1px solid var(--primary-color);
    border-radius: 4px;
    transition: background-color 0.2s, color 0.2s;
}

.label-toggle:hover {
    background: var(--primary-color);
    color: white;
}

.fields-list.show-labels .label-toggle {
    background: var(--primary-color);
    color: white;
}

.fields-list:not(.show-labels) tr.label-field {
    display: none;
}

.fields-list h4 {
    font-size: 0.875rem;
    margin-bottom: 0.75rem;
    color: var(--text-muted);
}

.field-item {
    display: flex;
    align-items: center;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
}

.field-item .field-name {
    font-weight: 500;
    min-width: 150px;
}

.field-item .field-type {
    color: var(--text-muted);
    margin-left: auto;
}

/* Keywords Table */
.keywords-table {
    margin-top: 1rem;
}

.keywords-table h4 {
    font-size: 0.875rem;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}

.keywords-table table {
    font-size: 0.8125rem;
}

.keywords-table td:first-child {
    width: 80px;
    color: var(--text-muted);
}

/* Workflow Diagram */
.workflow-diagram {
    background: var(--bg-color);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 1rem;
    min-height: 200px;
    position: relative;
}

.workflow-task {
    display: inline-block;
    padding: 0.75rem 1rem;
    background: var(--card-bg);
    border: 2px solid var(--border-color);
    border-radius: 8px;
    margin: 0.5rem;
    font-size: 0.875rem;
}

.workflow-task.start {
    border-color: var(--success-color);
    background: #dcfce7;
}

.workflow-task.end {
    border-color: var(--danger-color);
    background: #fee2e2;
}

.workflow-task.manual {
    border-color: var(--primary-color);
}

.workflow-task.automatic {
    border-color: var(--warning-color);
}

/* Tree View */
.tree {
    padding-left: 1rem;
}

.tree-item {
    padding: 0.25rem 0;
}

.tree-item > .tree {
    margin-left: 1rem;
    border-left: 1px dashed var(--border-color);
}

.tree-item-label {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
}

.tree-item-label .icon {
    color: var(--text-muted);
}

.tree-item-object .tree-item-label a {
    color: var(--text-color);
    font-weight: 500;
}

.tree-item-object .tree-item-label a:hover {
    color: var(--primary-color);
}

/* Object type specific icon colors */
.tree-item-object[data-type="category"] .icon {
    color: var(--primary-color);
}

.tree-item-object[data-type="workflow"] .icon {
    color: var(--warning-color);
}

.tree-item-object[data-type="eform"] .icon {
    color: var(--success-color);
}

.tree-item-object[data-type="query"] .icon {
    color: #8b5cf6;
}

.tree-item-object[data-type="dictionary"] .icon {
    color: var(--primary-color);
}

.tree-item-object[data-type="tree-view"] .icon {
    color: #10b981;
}

.tree-item-object[data-type="counter"] .icon {
    color: #6366f1;
}

.tree-item-object[data-type="stamp"] .icon {
    color: var(--danger-color);
}

.tree-item-object[data-type="data-type"] .icon {
    color: #0891b2;
}

/* Folder Security Styles */
.tree-item.has-security > .tree-item-label {
    background: #fef3c7;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    margin-left: -0.5rem;
}

.folder-security-details {
    background: #f9fafb;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 0.5rem;
    margin-bottom: 0.5rem;
}

.folder-security-details .compact-table {
    width: 100%;
    font-size: 0.8rem;
}

.folder-security-details .compact-table th,
.folder-security-details .compact-table td {
    padding: 0.25rem 0.5rem;
    border-bottom: 1px solid var(--border-color);
}

.folder-security-details .compact-table th {
    background: #f3f4f6;
    font-weight: 600;
    text-align: left;
}

/* Permission List */
.permission-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.permission-item {
    background: var(--bg-color);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
}

/* Search Highlight */
.highlight {
    background: #fef08a;
    padding: 0 0.125rem;
}

/* Collapsible */
.collapsible-header {
    cursor: pointer;
    user-select: none;
}

.collapsible-content {
    display: block;
}

.collapsible.collapsed .collapsible-content {
    display: none;
}

/* Links */
a {
    color: var(--primary-color);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* Back to Top */
.back-to-top {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: var(--primary-color);
    color: white;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    opacity: 0;
    transition: opacity 0.3s;
    z-index: 1000;
}

.back-to-top.visible {
    opacity: 1;
}

.back-to-top:hover {
    background: var(--primary-hover);
    text-decoration: none;
}

/* App Footer */
.app-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--bg-color);
    border-top: 1px solid var(--border-color);
    padding: 0.25rem 1rem;
    text-align: right;
    z-index: 999;
}

.version-info {
    font-size: 0.7rem;
    color: var(--text-muted);
    opacity: 0.6;
}

/* Workflow Task Details */
.task-detail {
    border: 1px solid var(--border-color);
    border-radius: 6px;
    margin-bottom: 0.75rem;
    background: var(--card-bg);
}

.task-detail-header {
    padding: 0.75rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    user-select: none;
    background: var(--bg-color);
    border-radius: 6px 6px 0 0;
}

.task-detail-header:hover {
    background: #e2e8f0;
}

.task-detail-header .task-name {
    font-weight: 600;
    font-size: 0.9rem;
}

.task-detail-header .task-seq {
    font-size: 0.75rem;
    color: var(--text-muted);
    background: var(--card-bg);
    padding: 0.125rem 0.5rem;
    border-radius: 10px;
}

.task-detail-header .task-arrow {
    margin-right: 0.5rem;
    transition: transform 0.2s;
}

.task-detail.collapsed .task-detail-header .task-arrow {
    transform: rotate(-90deg);
}

.task-detail.collapsed .task-detail-body {
    display: none;
}

.task-detail-body {
    padding: 1rem;
    border-top: 1px solid var(--border-color);
}

.task-info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.task-info-item {
    font-size: 0.8125rem;
}

.task-info-item .label {
    color: var(--text-muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    margin-bottom: 0.125rem;
}

/* Transitions section */
.transitions-list {
    margin-top: 0.75rem;
}

.transition-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem;
    background: var(--bg-color);
    border-radius: 4px;
    margin-bottom: 0.5rem;
    font-size: 0.8125rem;
}

.transition-item .transition-arrow {
    color: var(--primary-color);
}

.transition-item .condition {
    background: #fef3c7;
    color: #92400e;
    padding: 0.125rem 0.375rem;
    border-radius: 3px;
    font-family: monospace;
    font-size: 0.75rem;
}

/* Script code block */
.script-block {
    background: #1e293b;
    color: #e2e8f0;
    border-radius: 4px;
    padding: 0.75rem 1rem;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.75rem;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-all;
    margin-top: 0.5rem;
}

/* Checklist display */
.checklist-items {
    list-style: none;
    padding: 0;
    margin: 0.5rem 0 0 0;
}

.checklist-items li {
    padding: 0.25rem 0;
    font-size: 0.8125rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.checklist-items li:before {
    content: "\\2610";
    color: var(--text-muted);
}

/* Notification mail preview */
.notification-preview {
    background: var(--bg-color);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 0.75rem;
    margin-top: 0.5rem;
}

.notification-preview .subject {
    font-weight: 600;
    font-size: 0.8125rem;
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-color);
}

.notification-preview .message {
    font-size: 0.8125rem;
    color: var(--text-muted);
}

/* EForm component styles */
.eform-component {
    border: 1px solid var(--border-color);
    border-radius: 6px;
    margin-bottom: 0.5rem;
    background: var(--card-bg);
}

.eform-component-header {
    padding: 0.5rem 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    background: var(--bg-color);
    border-radius: 6px 6px 0 0;
    font-size: 0.8125rem;
}

.eform-component-header:hover {
    background: #e2e8f0;
}

.eform-component.collapsed .eform-component-header {
    border-radius: 6px;
}

.eform-component-header .component-key {
    font-family: monospace;
    color: var(--primary-color);
}

.eform-component-header .component-type {
    font-size: 0.7rem;
}

.eform-component-header .arrow {
    transition: transform 0.2s;
}

.eform-component.collapsed .eform-component-header .arrow {
    transform: rotate(-90deg);
}

.eform-component.collapsed .eform-component-body {
    display: none;
}

.eform-component-body {
    padding: 0.75rem;
    border-top: 1px solid var(--border-color);
    font-size: 0.8125rem;
}

.eform-children {
    margin-left: 1rem;
    padding-left: 0.75rem;
    border-left: 2px solid var(--border-color);
    margin-top: 0.5rem;
}

.eform-script-section {
    margin-top: 0.5rem;
}

.eform-script-label {
    font-size: 0.7rem;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

/* Logic rule styles */
.logic-rule {
    background: var(--bg-color);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 0.75rem;
    margin-top: 0.5rem;
}

.logic-rule-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.logic-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.logic-action {
    background: #f8fafc;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 0.5rem;
}

.logic-action-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
}

.eform-components-summary {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.eform-components-summary .component-badge {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    background: var(--bg-color);
    border-radius: 4px;
    border: 1px solid var(--border-color);
}

/* Print Styles */
@media print {
    .sidebar, .back-to-top {
        display: none;
    }
    .main-content {
        margin-left: 0;
        max-width: 100%;
    }
    .card, .item-detail {
        break-inside: avoid;
    }
}


/* Mermaid Diagram Overlay */
.diagram-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    z-index: 10000;
    padding: 2rem;
    overflow: hidden;
}

.diagram-overlay.active {
    display: flex;
    align-items: center;
    justify-content: center;
}

.diagram-overlay-header {
    background: #f8f9fa;
    padding: 1rem 1.5rem;
    border-bottom: 2px solid #e9ecef;
    border-radius: 8px 8px 0 0;
}

.diagram-overlay-header h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
    color: #333;
}

.diagram-overlay-instructions {
    font-size: 0.85rem;
    color: #6c757d;
    margin: 0;
    line-height: 1.5;
}

.diagram-overlay-content {
    background: white;
    border-radius: 0 0 8px 8px;
    max-width: 95vw;
    max-height: 80vh;
    overflow-x: auto;
    overflow-y: auto;
    position: relative;
}

.diagram-overlay-wrapper {
    background: white;
    border-radius: 8px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    max-width: 95vw;
}

.diagram-overlay-content svg {
    display: block;
}

.diagram-overlay-close {
    position: fixed;
    top: 1rem;
    right: 1rem;
    background: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    z-index: 10001;
}

.diagram-overlay-close:hover {
    background: #f3f4f6;
}

.mermaid-container {
    cursor: pointer;
    position: relative;
}

.mermaid-container::after {
    content: '🔍 Click to expand';
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(0,0,0,0.7);
    color: white;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.85rem;
    opacity: 0;
    transition: opacity 0.2s;
    pointer-events: none;
}

.mermaid-container:hover::after {
    opacity: 1;
}

/* Responsive */
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s;
    }
    .sidebar.open {
        transform: translateX(0);
    }
    .main-content {
        margin-left: 0;
        padding: 1rem;
    }
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
"""

# JavaScript for interactivity
JAVASCRIPT = """
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality with state preservation
    const searchInput = document.getElementById('search-input');
    const searchWrapper = document.getElementById('search-wrapper');
    const searchClear = document.getElementById('search-clear');
    let savedNavState = null;  // Store collapsed state before search

    function saveNavState() {
        if (savedNavState === null) {
            savedNavState = [];
            document.querySelectorAll('.nav-section').forEach((section, index) => {
                savedNavState[index] = section.classList.contains('collapsed');
            });
        }
    }

    function restoreNavState() {
        if (savedNavState !== null) {
            document.querySelectorAll('.nav-section').forEach((section, index) => {
                if (savedNavState[index]) {
                    section.classList.add('collapsed');
                } else {
                    section.classList.remove('collapsed');
                }
            });
            savedNavState = null;
        }
    }

    function performSearch(query) {
        const navItems = document.querySelectorAll('.nav-item');
        const navSections = document.querySelectorAll('.nav-section');

        // Update wrapper class for clear button visibility
        if (searchWrapper) {
            searchWrapper.classList.toggle('has-value', query.length > 0);
        }

        // Filter nav items
        navItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            const matches = text.includes(query);
            item.style.display = matches || !query ? 'block' : 'none';
        });

        // Expand sections that have visible items when searching
        if (query) {
            navSections.forEach(section => {
                const visibleItems = section.querySelectorAll('.nav-item');
                const hasVisible = Array.from(visibleItems).some(item => item.style.display !== 'none');
                if (hasVisible) {
                    section.classList.remove('collapsed');
                } else {
                    section.classList.add('collapsed');
                }
            });
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();

            // Save state when search starts (first character)
            if (query.length === 1 && savedNavState === null) {
                saveNavState();
            }

            // Restore state when search is cleared
            if (query.length === 0) {
                restoreNavState();
            }

            performSearch(query);
        });
    }

    if (searchClear) {
        searchClear.addEventListener('click', function() {
            searchInput.value = '';
            restoreNavState();
            performSearch('');
            searchInput.focus();
        });
    }

    // Collapsible navigation sections - default to expanded
    // (click handlers are set up below to allow toggling)

    document.querySelectorAll('.nav-section-header').forEach(header => {
        header.addEventListener('click', function() {
            this.parentElement.classList.toggle('collapsed');
        });
    });

    // Sidebar expand/collapse all buttons
    const sidebarExpandAll = document.getElementById('sidebar-expand-all');
    const sidebarCollapseAll = document.getElementById('sidebar-collapse-all');

    if (sidebarExpandAll) {
        sidebarExpandAll.addEventListener('click', function() {
            document.querySelectorAll('.nav-section').forEach(section => {
                section.classList.remove('collapsed');
            });
        });
    }

    if (sidebarCollapseAll) {
        sidebarCollapseAll.addEventListener('click', function() {
            document.querySelectorAll('.nav-section').forEach(section => {
                section.classList.add('collapsed');
            });
        });
    }

    // Back to top button
    const backToTop = document.getElementById('back-to-top');
    if (backToTop) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                // Update active nav item
                document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });

    // Highlight current section on scroll
    const sections = document.querySelectorAll('.section[id]');
    const navItems = document.querySelectorAll('.nav-item');

    function highlightNav() {
        const scrollPos = window.scrollY + 100;

        sections.forEach(section => {
            const top = section.offsetTop;
            const bottom = top + section.offsetHeight;
            const id = section.getAttribute('id');

            if (scrollPos >= top && scrollPos < bottom) {
                navItems.forEach(item => {
                    item.classList.remove('active');
                    if (item.getAttribute('href') === '#' + id) {
                        item.classList.add('active');
                    }
                });
            }
        });
    }

    window.addEventListener('scroll', highlightNav);
    highlightNav();

    // Content search with highlighting
    const contentSearch = document.getElementById('content-search');
    const contentSearchClear = document.getElementById('content-search-clear');
    const contentSearchCount = document.getElementById('content-search-count');
    const contentSearchWrapper = contentSearch ? contentSearch.closest('.content-search-wrapper') : null;

    function performContentSearch(query) {
        const items = document.querySelectorAll('.item-detail');
        const sections = document.querySelectorAll('.section');
        let matchCount = 0;

        // Update wrapper class for clear button visibility
        if (contentSearchWrapper) {
            contentSearchWrapper.classList.toggle('has-value', query.length > 0);
        }

        // Remove existing highlights
        document.querySelectorAll('.search-highlight').forEach(el => {
            const parent = el.parentNode;
            parent.replaceChild(document.createTextNode(el.textContent), el);
            parent.normalize();
        });

        if (!query) {
            // Show all items
            items.forEach(item => {
                item.style.display = 'block';
                item.classList.add('collapsed');
            });
            sections.forEach(section => {
                if (!section.id.match(/^(overview|folders)$/)) {
                    section.style.display = 'block';
                }
            });
            if (contentSearchCount) contentSearchCount.textContent = '';
            return;
        }

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(query)) {
                item.style.display = 'block';
                item.classList.remove('collapsed');
                matchCount++;
            } else {
                item.style.display = 'none';
            }
        });

        // Hide empty sections
        sections.forEach(section => {
            if (section.id.match(/^(overview|folders|groups|users)$/)) return;
            const visibleItems = section.querySelectorAll('.item-detail[style="display: block"]');
            section.style.display = visibleItems.length > 0 ? 'block' : 'none';
        });

        if (contentSearchCount) {
            contentSearchCount.textContent = matchCount > 0 ? `${matchCount} matches` : 'No matches';
        }
    }

    if (contentSearch) {
        contentSearch.addEventListener('input', function(e) {
            performContentSearch(e.target.value.toLowerCase());
        });
    }

    if (contentSearchClear) {
        contentSearchClear.addEventListener('click', function() {
            contentSearch.value = '';
            performContentSearch('');
            contentSearch.focus();
        });
    }

    // Collapsible item details - default to expanded
    // (click handlers are set up below to allow toggling)

    document.querySelectorAll('.item-detail-header').forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function(e) {
            // Don't toggle if clicking a link
            if (e.target.tagName === 'A') return;
            this.parentElement.classList.toggle('collapsed');
        });
    });

    // Expand all / Collapse all buttons
    document.querySelectorAll('.expand-all-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const section = this.closest('.section');
            section.querySelectorAll('.item-detail').forEach(item => {
                item.classList.remove('collapsed');
            });
            section.querySelectorAll('.task-detail').forEach(item => {
                item.classList.remove('collapsed');
            });
            section.querySelectorAll('.eform-component').forEach(item => {
                item.classList.remove('collapsed');
            });
        });
    });

    document.querySelectorAll('.collapse-all-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const section = this.closest('.section');
            section.querySelectorAll('.item-detail').forEach(item => {
                item.classList.add('collapsed');
            });
            section.querySelectorAll('.task-detail').forEach(item => {
                item.classList.add('collapsed');
            });
            section.querySelectorAll('.eform-component').forEach(item => {
                item.classList.add('collapsed');
            });
        });
    });

    // Label field toggle
    document.querySelectorAll('.label-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const fieldsList = this.closest('.fields-list');
            fieldsList.classList.toggle('show-labels');
            const count = this.textContent.match(/\d+/)[0];
            this.textContent = fieldsList.classList.contains('show-labels')
                ? 'Hide Label Fields (' + count + ')'
                : 'Show Label Fields (' + count + ')';
        });
    });
});
"""

# HTML template parts
HTML_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Therefore Configuration Documentation</title>
    <style>
{css}
    </style>
</head>
<body>
"""

HTML_FOOTER = """
    <a href="#top" id="back-to-top" class="back-to-top" title="Back to top">&#8593;</a>
    <footer class="app-footer">
        <span class="version-info">Therefore Config Processor v{app_version}</span>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true }});

        // Wait for Mermaid to finish rendering, then add click-to-expand
        mermaid.run().then(() => {{
            let currentPanZoom = null;

            // Create overlay element
            const overlay = document.createElement('div');
            overlay.className = 'diagram-overlay';
            overlay.innerHTML = `
                <button class="diagram-overlay-close" onclick="this.parentElement.classList.remove('active')">&times;</button>
                <div class="diagram-overlay-wrapper">
                    <div class="diagram-overlay-header">
                        <h3>Workflow Diagram</h3>
                        <p class="diagram-overlay-instructions">
                            🖱️ Mouse wheel to zoom • Click and drag to pan • Double-click to zoom in • Press ESC to close
                        </p>
                    </div>
                    <div class="diagram-overlay-content"></div>
                </div>
            `;
            document.body.appendChild(overlay);

            // Add click handlers to all mermaid containers
            document.querySelectorAll('.mermaid-container').forEach(container => {{
                container.addEventListener('click', function(e) {{
                    const svg = this.querySelector('svg');
                    if (svg) {{
                        // Clone the entire SVG with all attributes
                        const clone = svg.cloneNode(true);

                        // Preserve viewBox and dimensions
                        if (svg.hasAttribute('viewBox')) {{
                            clone.setAttribute('viewBox', svg.getAttribute('viewBox'));
                        }}

                        // Set explicit dimensions from the original
                        const bbox = svg.getBBox();
                        clone.setAttribute('width', bbox.width);
                        clone.setAttribute('height', bbox.height);
                        clone.style.maxWidth = 'none';
                        clone.style.width = bbox.width + 'px';
                        clone.style.height = bbox.height + 'px';

                        const content = overlay.querySelector('.diagram-overlay-content');
                        content.innerHTML = '';
                        content.appendChild(clone);
                        overlay.classList.add('active');

                        // Initialize pan & zoom on the cloned SVG
                        setTimeout(() => {{
                            if (currentPanZoom) {{
                                currentPanZoom.destroy();
                            }}
                            currentPanZoom = svgPanZoom(clone, {{
                                zoomEnabled: true,
                                controlIconsEnabled: true,
                                fit: false,
                                center: false,
                                minZoom: 0.1,
                                maxZoom: 20,
                                zoomScaleSensitivity: 0.3,
                                dblClickZoomEnabled: true,
                                mouseWheelZoomEnabled: true
                            }});
                        }}, 50);
                    }}
                }});
            }});

            // Close on overlay background click
            overlay.addEventListener('click', function(e) {{
                if (e.target === overlay) {{
                    if (currentPanZoom) {{
                        currentPanZoom.destroy();
                        currentPanZoom = null;
                    }}
                    overlay.classList.remove('active');
                }}
            }});

            // Close on Escape key
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape' && overlay.classList.contains('active')) {{
                    if (currentPanZoom) {{
                        currentPanZoom.destroy();
                        currentPanZoom = null;
                    }}
                    overlay.classList.remove('active');
                }}
            }});
        }});
    </script>
    <script>
{javascript}
    </script>
</body>
</html>
"""

SIDEBAR_TEMPLATE = """
<aside class="sidebar">
    <div class="sidebar-header">
        <h1>Therefore Documentation</h1>
        <div class="sidebar-search-wrapper" id="search-wrapper">
            <input type="text" id="search-input" class="sidebar-search" placeholder="Search...">
            <button type="button" class="search-clear-btn" id="search-clear" title="Clear search">&times;</button>
        </div>
        <div class="sidebar-controls">
            <button id="sidebar-expand-all" class="sidebar-btn" title="Expand all sections">&#9660; Expand</button>
            <button id="sidebar-collapse-all" class="sidebar-btn" title="Collapse all sections">&#9650; Collapse</button>
        </div>
    </div>
    <nav class="sidebar-nav">
        <div class="nav-section">
            <div class="nav-section-header">
                <span class="icon">&#9660;</span>
                Overview
            </div>
            <div class="nav-items">
                <a href="#overview" class="nav-item active">Dashboard</a>
                <a href="#security-audit" class="nav-item">🔒 Security Audit</a>
            </div>
        </div>
        {nav_sections}
    </nav>
</aside>
"""

NAV_SECTION_TEMPLATE = """
<div class="nav-section">
    <div class="nav-section-header">
        <span class="icon">&#9660;</span>
        {title}
        <span class="count">{count}</span>
    </div>
    <div class="nav-items">
        {items}
    </div>
</div>
"""

NAV_ITEM_TEMPLATE = '<a href="#{id}" class="nav-item">{name}</a>'

OVERVIEW_TEMPLATE = """
<section id="overview" class="section">
    <div class="page-header">
        <h1>{title}</h1>
        <p class="subtitle">Configuration Documentation</p>
    </div>

    <div class="content-search-wrapper">
        <input type="text" id="content-search" class="content-search" placeholder="Search content...">
        <button type="button" class="content-search-clear" id="content-search-clear" title="Clear search">&times;</button>
        <span id="content-search-count" class="content-search-count"></span>
    </div>

    {ai_summary}

    <div class="stats-grid">
        {stats_cards}
    </div>

    {version_warning_section}

    {validation_section}

    {root_security_section}

    <div class="card">
        <div class="card-header">
            <h2>Configuration Overview</h2>
        </div>
        <div class="card-body">
            <div class="property-grid">
                <div class="property">
                    <span class="property-label">Version</span>
                    <span class="property-value">{version}</span>
                </div>
                <div class="property">
                    <span class="property-label">Generated</span>
                    <span class="property-value">{generated_date}</span>
                </div>
            </div>
        </div>
    </div>
</section>
"""

STAT_CARD_TEMPLATE = """
<div class="stat-card">
    <div class="stat-value">{value}</div>
    <div class="stat-label">{label}</div>
</div>
"""

SECTION_TEMPLATE = """
<section id="{id}" class="section">
    <div class="section-header">
        <h2>{title}</h2>
        <span class="count">{count} items</span>
        <div class="section-controls">
            <button class="expand-all-btn" title="Expand all">&#9660; Expand All</button>
            <button class="collapse-all-btn" title="Collapse all">&#9650; Collapse All</button>
        </div>
    </div>
    {content}
</section>
"""

CATEGORY_TEMPLATE = """
<div id="category-{id}" class="item-detail">
    <div class="item-detail-header">
        <span class="expand-icon">&#9660;</span>
        <h3>{name}</h3>
        {badges}
        <span class="id">Category No: {category_no}</span>
        <span class="id">{guid}</span>
    </div>
    <div class="item-detail-body">
        {ai_summary}
        <div class="property-grid">
            <div class="property">
                <span class="property-label">Title</span>
                <span class="property-value">{title}</span>
            </div>
            <div class="property">
                <span class="property-label">Description</span>
                <span class="property-value">{description}</span>
            </div>
            <div class="property">
                <span class="property-label">Folder</span>
                <span class="property-value">{folder}</span>
            </div>
            <div class="property">
                <span class="property-label">Full-text Mode</span>
                <span class="property-value">{fulltext_mode}</span>
            </div>
            <div class="property">
                <span class="property-label">Check-in Mode</span>
                <span class="property-value">{checkin_mode}</span>
            </div>
            <div class="property">
                <span class="property-label">Empty Document Mode</span>
                <span class="property-value">{empty_doc_mode}</span>
            </div>
        </div>
        {fields_section}
        {security_section}
        {used_by_section}
    </div>
</div>
"""

FIELDS_TABLE_TEMPLATE = """
<div class="fields-list">
    <div class="fields-header">
        <h4>Fields ({count})</h4>
        {label_toggle}
    </div>
    <div class="table-responsive">
        <table>
            <thead>
                <tr>
                    <th>Caption</th>
                    <th>Field ID</th>
                    <th>Type</th>
                    <th>Length</th>
                    <th>Index</th>
                    <th>Mandatory</th>
                    <th>Field No</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
</div>
"""

FIELD_ROW_TEMPLATE = """
<tr class="{row_class}">
    <td>{caption}</td>
    <td><code>{field_id}</code></td>
    <td><span class="badge">{type_name}</span></td>
    <td>{length}</td>
    <td>{index_type}</td>
    <td>{mandatory}</td>
    <td>{field_no}</td>
</tr>
"""

WORKFLOW_TEMPLATE = """
<div id="workflow-{id}" class="item-detail">
    <div class="item-detail-header">
        <span class="expand-icon">&#9660;</span>
        <h3>{name}</h3>
        {badges}
        <span class="id">{guid}</span>
    </div>
    <div class="item-detail-body">
        {ai_summary}
        <div class="property-grid">
            <div class="property">
                <span class="property-label">Process ID</span>
                <span class="property-value"><code>{process_id}</code></span>
            </div>
            <div class="property">
                <span class="property-label">Description</span>
                <span class="property-value">{description}</span>
            </div>
            <div class="property">
                <span class="property-label">Folder</span>
                <span class="property-value">{folder}</span>
            </div>
            <div class="property">
                <span class="property-label">Category</span>
                <span class="property-value">{category}</span>
            </div>
            <div class="property">
                <span class="property-label">Duration</span>
                <span class="property-value">{duration}</span>
            </div>
            <div class="property">
                <span class="property-label">Delete After</span>
                <span class="property-value">{del_inst_days}</span>
            </div>
            <div class="property">
                <span class="property-label">Manual Start</span>
                <span class="property-value">{allow_manual}</span>
            </div>
            <div class="property">
                <span class="property-label">Attach History</span>
                <span class="property-value">{attach_history}</span>
            </div>
            <div class="property">
                <span class="property-label">Error Notification</span>
                <span class="property-value">{notify_on_error}</span>
            </div>
        </div>
        {flow_diagram}
        {tasks_section}
    </div>
</div>
"""

TASKS_TABLE_TEMPLATE = """
<div class="fields-list">
    <h4>Tasks ({count})</h4>
    <div class="table-responsive">
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Assigned To</th>
                    <th>Duration</th>
                    <th>Transitions</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
</div>
"""

TASK_ROW_TEMPLATE = """
<tr>
    <td>{name}</td>
    <td><span class="badge badge-{type_class}">{type_name}</span></td>
    <td>{assigned_to}</td>
    <td>{duration}</td>
    <td>{transitions}</td>
</tr>
"""

FOLDER_TREE_TEMPLATE = """
<div class="card">
    <div class="card-header">
        <h2>Folder Hierarchy</h2>
    </div>
    <div class="card-body">
        <div class="tree">
            {tree_content}
        </div>
    </div>
</div>
"""

FOLDER_ITEM_TEMPLATE = """
<div class="tree-item{security_class}">
    <div class="tree-item-label">
        <span class="icon">&#128193;</span>
        {name}
        <span class="badge">{type}</span>
        {security_badges}
    </div>
    {security_details}
    {children}
</div>
"""

ROLE_TEMPLATE = """
<div id="role-{id}" class="item-detail">
    <div class="item-detail-header">
        <span class="expand-icon">&#9660;</span>
        <h3>{name}</h3>
        {deny_badge}
        <span class="id">{guid}</span>
    </div>
    <div class="item-detail-body">
        {ai_summary}
        <div class="property-grid">
            <div class="property">
                <span class="property-label">Description</span>
                <span class="property-value">{description}</span>
            </div>
        </div>
        <div class="fields-list">
            <h4>Permissions</h4>
            <div class="permission-list">
                {permissions}
            </div>
        </div>
        {users_section}
        {assignments_section}
    </div>
</div>
"""

USERS_TABLE_TEMPLATE = """
<div class="fields-list">
    <h4>Assigned Users/Groups ({count})</h4>
    <div class="table-responsive">
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Display Name</th>
                    <th>Type</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
</div>
"""

EFORM_TEMPLATE = """
<div id="eform-{id}" class="item-detail">
    <div class="item-detail-header">
        <span class="expand-icon">&#9660;</span>
        <h3>{name}</h3>
        <span class="badge">{component_count} components</span>
        <span class="id">{guid}</span>
    </div>
    <div class="item-detail-body">
        {ai_summary}
        <div class="property-grid">
            <div class="property">
                <span class="property-label">Form ID</span>
                <span class="property-value"><code>{form_id}</code></span>
            </div>
            <div class="property">
                <span class="property-label">Version</span>
                <span class="property-value">{version}</span>
            </div>
            <div class="property">
                <span class="property-label">Folder</span>
                <span class="property-value">{folder}</span>
            </div>
            <div class="property">
                <span class="property-label">Created</span>
                <span class="property-value">{created_date}</span>
            </div>
            <div class="property">
                <span class="property-label">Created By</span>
                <span class="property-value">{created_by}</span>
            </div>
        </div>
        {components_section}
    </div>
</div>
"""

QUERY_TEMPLATE = """
<div id="query-{id}" class="item-detail">
    <div class="item-detail-header">
        <span class="expand-icon">&#9660;</span>
        <h3>{name}</h3>
        <span class="id">{guid}</span>
    </div>
    <div class="item-detail-body">
        <div class="property-grid">
            <div class="property">
                <span class="property-label">Query ID</span>
                <span class="property-value"><code>{query_id}</code></span>
            </div>
            <div class="property">
                <span class="property-label">Description</span>
                <span class="property-value">{description}</span>
            </div>
            <div class="property">
                <span class="property-label">Category</span>
                <span class="property-value">{category}</span>
            </div>
            <div class="property">
                <span class="property-label">Folder</span>
                <span class="property-value">{folder}</span>
            </div>
        </div>
    </div>
</div>
"""

DICTIONARY_TEMPLATE = """
<div id="dictionary-{id}" class="item-detail">
    <div class="item-detail-header">
        <span class="expand-icon">&#9660;</span>
        <h3>{name}</h3>
        <span class="badge">{keyword_count} keywords</span>
        <span class="id">{guid}</span>
    </div>
    <div class="item-detail-body">
        {ai_summary}
        <div class="property-grid">
            <div class="property">
                <span class="property-label">Description</span>
                <span class="property-value">{description}</span>
            </div>
            <div class="property">
                <span class="property-label">Folder</span>
                <span class="property-value">{folder}</span>
            </div>
        </div>
        {keywords_section}
        {used_by_section}
    </div>
</div>
"""

TREEVIEW_TEMPLATE = """
<div id="treeview-{id}" class="item-detail">
    <div class="item-detail-header">
        <span class="expand-icon">&#9660;</span>
        <h3>{name}</h3>
        <span class="id">{guid}</span>
    </div>
    <div class="item-detail-body">
        <div class="property-grid">
            <div class="property">
                <span class="property-label">Category</span>
                <span class="property-value">{category}</span>
            </div>
            <div class="property">
                <span class="property-label">Folder</span>
                <span class="property-value">{folder}</span>
            </div>
        </div>
        {levels_section}
    </div>
</div>
"""

COUNTER_TEMPLATE = """
<div id="counter-{id}" class="item-detail">
    <div class="item-detail-header">
        <span class="expand-icon">&#9660;</span>
        <h3>{name}</h3>
        <span class="badge">{type_name}</span>
        <span class="id">{guid}</span>
    </div>
    <div class="item-detail-body">
        <div class="property-grid">
            <div class="property">
                <span class="property-label">Format</span>
                <span class="property-value"><code>{format_string}</code></span>
            </div>
        </div>
        {used_by_section}
    </div>
</div>
"""

DATATYPE_TEMPLATE = """
<div id="datatype-{id}" class="item-detail">
    <div class="item-detail-header">
        <span class="expand-icon">&#9660;</span>
        <h3>{name}</h3>
        <span class="badge">{type_group}</span>
        <span class="id">{guid}</span>
    </div>
    <div class="item-detail-body">
        <div class="property-grid">
            <div class="property">
                <span class="property-label">Table Name</span>
                <span class="property-value"><code>{table_name}</code></span>
            </div>
        </div>
        {columns_section}
    </div>
</div>
"""

STAMP_TEMPLATE = """
<div id="stamp-{id}" class="item-detail">
    <div class="item-detail-header">
        <span class="expand-icon">&#9660;</span>
        <h3>{name}</h3>
        <span class="badge">{type_name}</span>
        <span class="id">{guid}</span>
    </div>
    <div class="item-detail-body">
        <div class="property-grid">
            <div class="property">
                <span class="property-label">Filename</span>
                <span class="property-value">{filename}</span>
            </div>
        </div>
    </div>
</div>
"""

SECURITY_AUDIT_TEMPLATE = """
<section id="security-audit" class="section">
    <div class="page-header">
        <h1>Security Audit Report</h1>
        <p class="subtitle">Access Control Analysis</p>
    </div>

    {conflicts_section}
    {unsecured_section}
    {deny_roles_section}
    {overprivileged_section}
    {role_matrix_section}
    {user_access_section}
</section>
"""
