"""Security audit section generation for HTML generator."""

from ..analyzer.security_analyzer import SecurityAnalyzer


def generate_security_audit_section(generator) -> str:
    """Generate the security audit report section.
    
    Args:
        generator: HTMLGenerator instance
        
    Returns:
        HTML string for security audit section
    """
    from ..utils.helpers import escape_html
    from .templates import SECURITY_AUDIT_TEMPLATE
    
    analyzer = SecurityAnalyzer(generator.config)
    
    # Generate all security analysis
    conflicts = analyzer.get_permission_conflicts()
    unsecured = analyzer.get_unsecured_objects()
    deny_roles = analyzer.get_deny_role_analysis()
    overprivileged = analyzer.get_overprivileged_users()
    role_matrix = analyzer.get_role_access_matrix()
    user_access = analyzer.get_user_access_summary()
    
    # Build conflicts section
    conflicts_html = ""
    if conflicts:
        conflicts_items = []
        for conflict in conflicts:
            allow_roles_html = ', '.join([f"{r['role']} ({r['permission']})" for r in conflict['allow_roles']])
            deny_roles_html = ', '.join([f"{r['role']} ({r['permission']})" for r in conflict['deny_roles']])
            
            conflicts_items.append(f'''
            <tr>
                <td>{escape_html(conflict['type'])}</td>
                <td><strong>{escape_html(conflict['object'])}</strong></td>
                <td><span class="badge badge-success">{escape_html(allow_roles_html)}</span></td>
                <td><span class="badge badge-danger">{escape_html(deny_roles_html)}</span></td>
            </tr>
            ''')
        
        conflicts_html = f'''
        <div class="card">
            <div class="card-header">
                <h2>⚠️ Permission Conflicts</h2>
                <span class="badge badge-warning">{len(conflicts)}</span>
            </div>
            <div class="card-body">
                <p>Objects with both allow and deny permissions:</p>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Object</th>
                            <th>Allow Roles</th>
                            <th>Deny Roles</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(conflicts_items)}
                    </tbody>
                </table>
            </div>
        </div>
        '''
    
    # Build unsecured objects section
    unsecured_html = ""
    total_unsecured = sum(len(objects) for objects in unsecured.values())
    if total_unsecured > 0:
        unsecured_items = []
        for obj_type, objects in unsecured.items():
            if objects:
                objects_html = '<br>'.join([escape_html(obj) for obj in objects[:10]])
                if len(objects) > 10:
                    objects_html += f'<br><em>...and {len(objects) - 10} more</em>'
                
                unsecured_items.append(f'''
                <tr>
                    <td><strong>{obj_type.capitalize()}</strong></td>
                    <td><span class="badge">{len(objects)}</span></td>
                    <td>{objects_html}</td>
                </tr>
                ''')
        
        unsecured_html = f'''
        <div class="card">
            <div class="card-header">
                <h2>🔓 Unsecured Objects</h2>
                <span class="badge badge-warning">{total_unsecured}</span>
            </div>
            <div class="card-body">
                <p>Objects without any role assignments (publicly accessible):</p>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Count</th>
                            <th>Objects</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(unsecured_items)}
                    </tbody>
                </table>
            </div>
        </div>
        '''
    
    # Build deny roles section
    deny_roles_html = ""
    if deny_roles:
        deny_items = []
        for role in deny_roles:
            blocks_html = []
            for block_type, objects in role['blocks'].items():
                if objects:
                    blocks_html.append(f"<strong>{block_type.capitalize()}:</strong> {', '.join([escape_html(o) for o in objects[:5]])}")
                    if len(objects) > 5:
                        blocks_html.append(f"<em>...and {len(objects) - 5} more</em>")
            
            users_html = ', '.join([escape_html(u) for u in role['affected_users'][:5]])
            if role['user_count'] > 5:
                users_html += f", <em>...and {role['user_count'] - 5} more</em>"
            
            deny_items.append(f'''
            <tr>
                <td><strong>{escape_html(role['name'])}</strong><br><small>{escape_html(role['description'])}</small></td>
                <td><span class="badge badge-danger">{role['user_count']}</span></td>
                <td>{users_html}</td>
                <td>{'<br>'.join(blocks_html)}</td>
            </tr>
            ''')
        
        deny_roles_html = f'''
        <div class="card">
            <div class="card-header">
                <h2>🚫 Deny Roles</h2>
                <span class="badge badge-danger">{len(deny_roles)}</span>
            </div>
            <div class="card-body">
                <p>Roles that explicitly block access:</p>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Role</th>
                            <th>Affected Users</th>
                            <th>Users/Groups</th>
                            <th>Blocks Access To</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(deny_items)}
                    </tbody>
                </table>
            </div>
        </div>
        '''
    
    # Build overprivileged users section
    overprivileged_html = ""
    if overprivileged:
        overprivileged_items = []
        for user in overprivileged[:10]:  # Show top 10
            roles_html = ', '.join([f"{r['role']} ({r['permission']})" for r in user['roles']])
            
            overprivileged_items.append(f'''
            <tr>
                <td><strong>{escape_html(user['name'])}</strong></td>
                <td><span class="badge badge-warning">{user['role_count']}</span></td>
                <td>{escape_html(roles_html)}</td>
            </tr>
            ''')
        
        overprivileged_html = f'''
        <div class="card">
            <div class="card-header">
                <h2>👥 Users with Multiple Roles</h2>
                <span class="badge">{len(overprivileged)}</span>
            </div>
            <div class="card-body">
                <p>Users/groups assigned to 3 or more roles:</p>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>User/Group</th>
                            <th>Role Count</th>
                            <th>Roles</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(overprivileged_items)}
                    </tbody>
                </table>
            </div>
        </div>
        '''
    
    # Build role access matrix
    role_matrix_html = ""
    if role_matrix:
        matrix_rows = []
        for role_name, access in sorted(role_matrix.items()):
            total_access = sum(len(objects) for objects in access.values())
            if total_access > 0:  # Only show roles with assignments
                categories_count = len(access.get('categories', []))
                folders_count = len(access.get('folders', []))
                workflows_count = len(access.get('workflows', []))
                
                matrix_rows.append(f'''
                <tr>
                    <td><strong>{escape_html(role_name)}</strong></td>
                    <td><span class="badge">{categories_count}</span></td>
                    <td><span class="badge">{folders_count}</span></td>
                    <td><span class="badge">{workflows_count}</span></td>
                    <td><span class="badge badge-primary">{total_access}</span></td>
                </tr>
                ''')
        
        role_matrix_html = f'''
        <div class="card">
            <div class="card-header">
                <h2>📊 Role Access Matrix</h2>
            </div>
            <div class="card-body">
                <p>Summary of role assignments by object type:</p>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Role</th>
                            <th>Categories</th>
                            <th>Folders</th>
                            <th>Workflows</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(matrix_rows)}
                    </tbody>
                </table>
            </div>
        </div>
        '''
    
    # Build user access summary
    user_access_html = ""
    if user_access:
        user_rows = []
        for user in user_access[:20]:  # Show top 20
            roles_html = ', '.join([escape_html(r) for r in user['roles']])
            cat_count = len(user['categories'])
            folder_count = len(user['folders'])
            deny_badge = '<span class="badge badge-danger">DENY</span>' if user['is_deny'] else ''
            
            user_rows.append(f'''
            <tr>
                <td><strong>{escape_html(user['name'])}</strong> {deny_badge}</td>
                <td>{escape_html(roles_html)}</td>
                <td><span class="badge">{cat_count}</span></td>
                <td><span class="badge">{folder_count}</span></td>
            </tr>
            ''')
        
        user_access_html = f'''
        <div class="card">
            <div class="card-header">
                <h2>👤 User Access Summary</h2>
                <span class="badge">{len(user_access)}</span>
            </div>
            <div class="card-body">
                <p>What each user/group can access:</p>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>User/Group</th>
                            <th>Roles</th>
                            <th>Categories</th>
                            <th>Folders</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(user_rows)}
                    </tbody>
                </table>
            </div>
        </div>
        '''
    
    return SECURITY_AUDIT_TEMPLATE.format(
        conflicts_section=conflicts_html,
        unsecured_section=unsecured_html,
        deny_roles_section=deny_roles_html,
        overprivileged_section=overprivileged_html,
        role_matrix_section=role_matrix_html,
        user_access_section=user_access_html
    )
