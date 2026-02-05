"""Parser for Therefore configuration XML files."""

import xml.etree.ElementTree as ET
from typing import List, Optional
from pathlib import Path

from .models import (
    Configuration, Category, CaseDefinition, Field, WorkflowProcess, WorkflowTask,
    WorkflowTransition, Folder, User, Role, RoleAssignment, RoleObjectAssignment,
    EForm, EFormComponent, Query, QueryField, KeywordDictionary, Keyword,
    TreeView, TreeViewLevel, Counter, DataType, DataTypeColumn, Stamp,
    CaptureProfile, ContentConnectorSource, RetentionPolicy, RetentionPolicyCategory
)
import json
from .constants import (
    FIELD_TYPES, WORKFLOW_TASK_TYPE, OBJECT_TYPES, USER_TYPE,
    FULLTEXT_MODE, CHECKIN_MODE, AUTO_APPEND_MODE, INDEX_TYPE,
    COUNTER_TYPE, COUNTER_MODE, DATA_TYPE_GROUP, STAMP_TYPE,
    STORAGE_MODE, CAPTURE_DOC_BREAK, CAPTURE_COLOR_MODES,
    CONTENT_CONNECTOR_SOURCE_MODE, TREEVIEW_LEVEL_FUNCTION,
    TREEVIEW_SORT_ORDER, QUERY_FIELD_ALIGNMENT, ROLE_PERMISSION,
    get_lookup_name, decode_flags
)
from ..utils.helpers import (
    get_text_from_tstr, get_element_text, get_element_int,
    get_element_bool, format_date, build_tree_structure
)


class ConfigurationParser:
    """Parser for Therefore configuration XML files."""

    def __init__(self):
        self.config = Configuration()

    def parse(self, xml_path: str) -> Configuration:
        """
        Parse a Therefore configuration XML file.

        Args:
            xml_path: Path to the XML configuration file

        Returns:
            Configuration object with all parsed data
        """
        path = Path(xml_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {xml_path}")

        tree = ET.parse(xml_path)
        root = tree.getroot()

        self.config = Configuration()

        # Parse version
        version_elem = root.find("Version")
        if version_elem is not None:
            self.config.version = version_elem.text or ""
            try:
                self.config.version_int = int(version_elem.text)
            except (ValueError, TypeError):
                self.config.version_int = 0

        # Parse all configuration sections
        self._parse_folders(root)
        self._parse_users(root)
        self._parse_categories(root)
        self._parse_case_definitions(root)
        self._parse_keyword_dictionaries(root)
        self._parse_counters(root)
        self._parse_data_types(root)
        self._parse_workflows(root)
        self._parse_roles(root)
        self._parse_role_assignments(root)
        self._parse_eforms(root)
        self._parse_queries(root)
        self._parse_tree_views(root)
        self._parse_stamps(root)
        self._parse_capture_profiles(root)
        self._parse_content_connector_sources(root)
        self._parse_retention_policies(root)

        # Build lookup maps for cross-referencing
        self.config.build_lookup_maps()

        return self.config

    def parse_string(self, xml_content: str) -> Configuration:
        """
        Parse Therefore configuration from an XML string.

        Args:
            xml_content: XML configuration as a string

        Returns:
            Configuration object with all parsed data
        """
        root = ET.fromstring(xml_content)

        self.config = Configuration()

        # Parse version
        version_elem = root.find("Version")
        if version_elem is not None:
            self.config.version = version_elem.text or ""
            try:
                self.config.version_int = int(version_elem.text)
            except (ValueError, TypeError):
                self.config.version_int = 0

        # Parse all configuration sections
        self._parse_folders(root)
        self._parse_users(root)
        self._parse_categories(root)
        self._parse_case_definitions(root)
        self._parse_keyword_dictionaries(root)
        self._parse_counters(root)
        self._parse_data_types(root)
        self._parse_workflows(root)
        self._parse_roles(root)
        self._parse_role_assignments(root)
        self._parse_eforms(root)
        self._parse_queries(root)
        self._parse_tree_views(root)
        self._parse_stamps(root)
        self._parse_capture_profiles(root)
        self._parse_content_connector_sources(root)
        self._parse_retention_policies(root)

        # Build lookup maps for cross-referencing
        self.config.build_lookup_maps()

        return self.config

    def _parse_folders(self, root: ET.Element) -> None:
        """Parse folder hierarchy."""
        folders_elem = root.find("Folders")
        if folders_elem is None:
            return

        flat_folders = []
        for folder_elem in folders_elem.findall("Folder"):
            folder = self._parse_folder(folder_elem)
            flat_folders.append(folder)

        # Build tree structure
        self.config.folders = build_tree_structure(
            flat_folders, parent_attr="parent_no", id_attr="folder_no"
        )

    def _parse_folder(self, elem: ET.Element) -> Folder:
        """Parse a single folder element."""
        # Try <Parent> first, then fall back to <ParentNo>
        parent_elem = elem.find("Parent")
        if parent_elem is not None:
            parent_no = get_element_int(parent_elem) or None
        else:
            parent_no = get_element_int(elem.find("ParentNo")) or None

        folder = Folder(
            folder_no=get_element_int(elem.find("FolderNo")),
            name=get_text_from_tstr(elem.find("Name")),
            parent_no=parent_no,
            folder_type=get_element_int(elem.find("FolderType")),
            id=get_element_text(elem.find("Id")),
        )

        # Handle 0 as None for parent
        if folder.parent_no == 0:
            folder.parent_no = None

        folder.folder_type_name = get_lookup_name(OBJECT_TYPES, folder.folder_type)
        return folder

    def _parse_users(self, root: ET.Element) -> None:
        """Parse users and groups."""
        users_elem = root.find("Users")
        if users_elem is None:
            return

        for user_elem in users_elem.findall("User"):
            user = self._parse_user(user_elem)
            self.config.users.append(user)

    def _parse_user(self, user_elem: ET.Element) -> User:
        """Parse a single user or group element."""
        # Handle both Therefore export format and standard format
        user_no = get_element_int(user_elem.find("UserNo"))
        if user_no == 0:
            user_no = get_element_int(user_elem.find("ADOSUserNo"))

        user_name = get_element_text(user_elem.find("UserName"))
        if not user_name:
            user_name = get_element_text(user_elem.find("Username"))

        display_name = get_element_text(user_elem.find("DisplayName"))
        if not display_name:
            display_name = get_element_text(user_elem.find("Displayname"))

        user_type = get_element_int(user_elem.find("UserType"))
        if user_type == 0:
            user_type = get_element_int(user_elem.find("Type"))

        user = User(
            user_no=user_no,
            user_name=user_name,
            display_name=display_name,
            user_type=user_type,
            id=get_element_text(user_elem.find("Id")),
            domain=get_element_text(user_elem.find("Domain")),
            email=get_element_text(user_elem.find("SMTPAddress")),
            description=get_element_text(user_elem.find("Description")),
            is_domain_user=get_element_bool(user_elem.find("IsDomainUser")),
        )
        user.user_type_name = get_lookup_name(USER_TYPE, user.user_type)

        # Parse group members (for groups) - UserGroups contains Group elements
        user_groups_elem = user_elem.find("UserGroups")
        if user_groups_elem is not None:
            for group_elem in user_groups_elem.findall("Group"):
                member = self._parse_user(group_elem)
                user.members.append(member)

        return user

    def _parse_categories(self, root: ET.Element) -> None:
        """Parse document categories."""
        categories_elem = root.find("Categories")
        if categories_elem is None:
            return

        for cat_elem in categories_elem.findall("Category"):
            category = self._parse_category(cat_elem)
            self.config.categories.append(category)

    def _parse_category(self, elem: ET.Element) -> Category:
        """Parse a single category element."""
        category = Category(
            category_no=get_element_int(elem.find("CtgryNo")),
            name=get_text_from_tstr(elem.find("Name")),
            title=get_element_text(elem.find("Title")),
            description=get_text_from_tstr(elem.find("Description")),
            width=get_element_int(elem.find("Width")),
            height=get_element_int(elem.find("Height")),
            folder_no=get_element_int(elem.find("FolderNo")) or None,
            fulltext_mode=get_element_int(elem.find("FulltextMode")),
            checkin_mode=get_element_int(elem.find("CheckInMode")),
            auto_append_mode=get_element_int(elem.find("AutoApndMode")),
            empty_doc_mode=get_element_int(elem.find("EmptyDocMode")),
            cover_mode=get_element_int(elem.find("CoverMode")),
            version=get_element_int(elem.find("Version")),
            id=get_element_text(elem.find("Id")),
            belongs_to_case_def=get_element_int(elem.find("BelongsToCaseDef")) or None,
            sub_category_field_no=get_element_int(elem.find("SubCtgryFieldNo")) or None,
            workflow_process_no=get_element_int(elem.find("WFProcessNo")) or None,
        )

        # Handle 0 as None for optional references
        if category.belongs_to_case_def == 0:
            category.belongs_to_case_def = None
        if category.sub_category_field_no == 0:
            category.sub_category_field_no = None
        if category.workflow_process_no == 0:
            category.workflow_process_no = None

        # Resolve type names
        category.fulltext_mode_name = get_lookup_name(FULLTEXT_MODE, category.fulltext_mode)
        category.checkin_mode_name = get_lookup_name(CHECKIN_MODE, category.checkin_mode)
        category.auto_append_mode_name = get_lookup_name(AUTO_APPEND_MODE, category.auto_append_mode)

        # Parse fields
        fields_elem = elem.find("Fields")
        if fields_elem is not None:
            for field_elem in fields_elem.findall("Field"):
                field = self._parse_field(field_elem)
                category.fields.append(field)

        # Sort fields by display order
        category.fields.sort(key=lambda f: (f.disp_order_pos, f.tab_order_pos))

        # Parse sub-categories
        sub_cats_elem = elem.find("SubCategories")
        if sub_cats_elem is not None:
            for sub_elem in sub_cats_elem.findall("SubCategory"):
                sub_category = self._parse_category(sub_elem)
                category.sub_categories.append(sub_category)

        return category

    def _parse_case_definitions(self, root: ET.Element) -> None:
        """Parse case definitions."""
        case_defs_elem = root.find("CaseDefinitions")
        if case_defs_elem is None:
            return

        for cd_elem in case_defs_elem.findall("CaseDefinition"):
            case_def = self._parse_case_definition(cd_elem)
            self.config.case_definitions.append(case_def)

    def _parse_case_definition(self, elem: ET.Element) -> CaseDefinition:
        """Parse a single case definition element."""
        case_def = CaseDefinition(
            case_def_no=get_element_int(elem.find("CaseDefNo")),
            name=get_text_from_tstr(elem.find("Name")),
            title=get_element_text(elem.find("Title")),
            description=get_text_from_tstr(elem.find("Description")),
            width=get_element_int(elem.find("Width")),
            height=get_element_int(elem.find("Height")),
            folder_no=get_element_int(elem.find("FolderNo")) or None,
            checkin_mode=get_element_int(elem.find("CheckInMode")),
            auto_append_mode=get_element_int(elem.find("AutoApndMode")),
            empty_doc_mode=get_element_int(elem.find("EmptyDocMode")),
            cover_mode=get_element_int(elem.find("CoverMode")),
            version=get_element_int(elem.find("Version")),
            id=get_element_text(elem.find("Id")),
            case_def_id=get_element_text(elem.find("CaseDefID")),
            datatype_no=get_element_int(elem.find("DataTypeNo")) or None,
        )

        # Handle 0 as None for folder
        if case_def.folder_no == 0:
            case_def.folder_no = None
        if case_def.datatype_no == 0:
            case_def.datatype_no = None

        # Resolve type names
        case_def.checkin_mode_name = get_lookup_name(CHECKIN_MODE, case_def.checkin_mode)
        case_def.auto_append_mode_name = get_lookup_name(AUTO_APPEND_MODE, case_def.auto_append_mode)

        # Parse fields (similar to category fields)
        fields_elem = elem.find("Fields")
        if fields_elem is not None:
            for field_elem in fields_elem.findall("Field"):
                field = self._parse_field(field_elem)
                case_def.fields.append(field)

        # Sort fields by display order
        case_def.fields.sort(key=lambda f: (f.disp_order_pos, f.tab_order_pos))

        return case_def

    def _parse_field(self, elem: ET.Element) -> Field:
        """Parse a single field element."""
        field = Field(
            field_no=get_element_int(elem.find("FieldNo")),
            field_id=get_element_text(elem.find("FieldID")),
            col_name=get_element_text(elem.find("ColName")),
            caption=get_text_from_tstr(elem.find("Caption")),
            type_no=get_element_int(elem.find("TypeNo")),
            length=get_element_int(elem.find("Length")),
            width=get_element_int(elem.find("Width")),
            height=get_element_int(elem.find("Height")),
            pos_x=get_element_int(elem.find("PosX")),
            pos_y=get_element_int(elem.find("PosY")),
            tab_order_pos=get_element_int(elem.find("TabOrderPos")),
            disp_order_pos=get_element_int(elem.find("DispOrderPos")),
            index_type=get_element_int(elem.find("IndexType")),
            is_mandatory=get_element_bool(elem.find("IsMandatory")),
            default_value=get_element_text(elem.find("DefaultVal")),
            regex_pattern=get_element_text(elem.find("RegEx")),
            regex_help=get_text_from_tstr(elem.find("RegExHelp")),
            counter_no=get_element_int(elem.find("CounterNo")) or None,
            counter_mode=get_element_int(elem.find("CounterMode")),
            dictionary_no=get_element_int(elem.find("DictionaryNo")) or None,
            data_type_no=get_element_int(elem.find("DataTypeNo")) or None,
            id=get_element_text(elem.find("Id")),
        )

        # Resolve type names
        if field.type_no > 0 and field.type_no <= 13:
            field.type_name = get_lookup_name(FIELD_TYPES, field.type_no)
        elif field.type_no < 0:
            # Negative type_no references a keyword dictionary or data type
            # Store it for later resolution after all dictionaries/datatypes are parsed
            field.dictionary_no = field.type_no  # Will be resolved to actual dictionary later
            field.data_type_no = field.type_no   # Might be a datatype reference
            field.type_name = "Reference"  # Will be updated in HTML generator
        else:
            field.type_name = f"User-defined ({field.type_no})"

        field.index_type_name = get_lookup_name(INDEX_TYPE, field.index_type)

        return field

    def _parse_workflows(self, root: ET.Element) -> None:
        """Parse workflow processes."""
        # Try WFProcesses first (Therefore export format)
        workflows_elem = root.find("WFProcesses")
        if workflows_elem is None:
            # Fall back to Workflows (alternative format)
            workflows_elem = root.find("Workflows")
        if workflows_elem is None:
            return

        # Try WFProcess first, then Workflow
        wf_elements = workflows_elem.findall("WFProcess")
        if not wf_elements:
            wf_elements = workflows_elem.findall("Workflow")

        for wf_elem in wf_elements:
            workflow = self._parse_workflow(wf_elem)
            self.config.workflows.append(workflow)

    def _parse_workflow(self, elem: ET.Element) -> WorkflowProcess:
        """Parse a single workflow process."""
        workflow = WorkflowProcess(
            process_no=get_element_int(elem.find("ProcessNo")),
            name=get_text_from_tstr(elem.find("Name")),
            description=get_text_from_tstr(elem.find("Description")),
            version=get_element_int(elem.find("VersionNo")) or get_element_int(elem.find("Version")),
            folder_no=get_element_int(elem.find("FolderNo")) or None,
            category_no=get_element_int(elem.find("CtgryNo")) or None,
            id=get_element_text(elem.find("Id")),
            process_id=get_element_text(elem.find("ProcessID")),
            # Additional process settings
            duration=get_element_int(elem.find("Duration")),
            del_inst_days=get_element_int(elem.find("DelInstDays")),
            attach_history=get_element_bool(elem.find("AttachHistory")),
            allow_manual=get_element_bool(elem.find("AllowManual")),
            notify_on_error=get_element_text(elem.find("NotifyOnError")),
            comments_level=get_element_int(elem.find("CommentsLevel")),
            enabled=get_element_bool(elem.find("Enabled"), default=True),
        )

        # Parse tasks
        tasks_elem = elem.find("Tasks")
        if tasks_elem is not None:
            # Try "T" first (Therefore export format), then "Task"
            task_elements = tasks_elem.findall("T")
            if not task_elements:
                task_elements = tasks_elem.findall("Task")

            for task_elem in task_elements:
                task = self._parse_workflow_task(task_elem, workflow.process_no)
                workflow.tasks.append(task)

        # Sort tasks by sequence position for display
        workflow.tasks.sort(key=lambda t: t.seq_pos)

        return workflow

    def _parse_workflow_task(self, elem: ET.Element, process_no: int) -> WorkflowTask:
        """Parse a single workflow task."""
        task = WorkflowTask(
            task_no=get_element_int(elem.find("TaskNo")),
            task_id=get_element_text(elem.find("TaskId")),
            name=get_text_from_tstr(elem.find("Name")),
            type_no=get_element_int(elem.find("Type")),
            process_no=process_no,
            pos_x=get_element_int(elem.find("PosX")),
            pos_y=get_element_int(elem.find("PosY")),
            duration=get_element_int(elem.find("Duration")),
            seq_pos=get_element_int(elem.find("SeqPos")),
            overdue_mail=get_element_text(elem.find("OverdueMail")),
            notification_mail=get_element_text(elem.find("NotificationMail")),
            delegate_mail=get_element_text(elem.find("DelegateMail")),
            use_checklist=get_element_bool(elem.find("UseChecklist")),
            disable_delegation=get_element_bool(elem.find("DisableDelegation")),
            user_choice=get_element_int(elem.find("UserChoice")),
            id=get_element_text(elem.find("Id")),
            action_type=get_element_text(elem.find("ActionType")),
            script_name=get_element_text(elem.find("ScriptName")),
            params=get_element_text(elem.find("Params")),
        )

        task.type_name = get_lookup_name(WORKFLOW_TASK_TYPE, task.type_no)

        # Extract init script from params if present
        if task.params:
            task.init_script = self._extract_init_script(task.params)
            # Extract REST calls if action type is call rest sequence
            if task.action_type == 'callrestsequence':
                task.rest_calls = self._extract_rest_calls(task.params)

        # Parse notification mail XML to extract subject and message
        if task.notification_mail:
            task.notification_subject, task.notification_message = self._parse_notification_mail(
                task.notification_mail
            )

        # Parse checklist items (They have TStr format)
        checklist_elem = elem.find("Checklist")
        if checklist_elem is not None:
            for cl_elem in checklist_elem.findall("CL"):
                text_elem = cl_elem.find("Text")
                if text_elem is not None:
                    text = get_text_from_tstr(text_elem)
                    if text:
                        task.checklist.append(text)

        # Parse choices - these are not text choices but user assignments
        # The Choices element contains CH elements with assigned users
        choices_elem = elem.find("Choices")
        if choices_elem is not None:
            for ch_elem in choices_elem.findall("CH"):
                user_info = {
                    "user_no": get_element_int(ch_elem.find("UserNo")),
                    "user_name": get_element_text(ch_elem.find("UserName")),
                    "display_name": get_element_text(ch_elem.find("DisplayName")),
                    "user_type": get_element_int(ch_elem.find("UserType")),
                }
                task.assigned_users.append(user_info)

        # Parse transitions
        transitions_elem = elem.find("Transitions")
        if transitions_elem is not None:
            for tr_elem in transitions_elem.findall("TR"):
                transition = self._parse_workflow_transition(tr_elem)
                task.transitions.append(transition)

        return task

    def _extract_init_script(self, params: str) -> str:
        """Extract the InitScript from embedded XML in params."""
        try:
            # The params contain escaped XML - we need to unescape it first
            import html
            unescaped = html.unescape(params)
            # Try to parse the outer XML
            params_root = ET.fromstring(unescaped)
            # Look for InitScript anywhere in the parsed structure
            # After unescaping, the nested ixprofile content becomes actual elements
            init_script_elem = params_root.find(".//InitScript")
            if init_script_elem is not None and init_script_elem.text:
                return init_script_elem.text.strip()
        except Exception:
            pass
        return ""

    def _extract_rest_calls(self, params: str) -> List:
        """Extract REST service call configurations from params."""
        from .models import RestServiceCall
        rest_calls = []
        try:
            # Parse params as XML directly (they're already properly escaped)
            params_root = ET.fromstring(params)

            # Find all call elements
            call_elems = params_root.findall('.//calls/Elem')
            for call_elem in call_elems:
                call = RestServiceCall()

                # Extract basic call info
                call_name_elem = call_elem.find('CallName')
                if call_name_elem is not None and call_name_elem.text:
                    call.call_name = call_name_elem.text

                call_id_elem = call_elem.find('CallId')
                if call_id_elem is not None and call_id_elem.text:
                    call.call_id = call_id_elem.text

                verb_elem = call_elem.find('verb')
                if verb_elem is not None and verb_elem.text:
                    call.http_method = verb_elem.text

                url_elem = call_elem.find('url')
                if url_elem is not None and url_elem.text:
                    call.url = url_elem.text

                cred_elem = call_elem.find('CredentialNo')
                if cred_elem is not None and cred_elem.text:
                    call.credential_no = cred_elem.text

                # Extract body parameters
                body_elems = call_elem.findall('.//body/Elem')
                for body_elem in body_elems:
                    name_elem = body_elem.find('N')
                    value_elem = body_elem.find('V')
                    if name_elem is not None and value_elem is not None:
                        call.body_params.append({
                            'name': name_elem.text or '',
                            'value': value_elem.text or ''
                        })

                # Extract response script (may be long, limit preview)
                resp_script_elem = call_elem.find('RespScript')
                if resp_script_elem is not None and resp_script_elem.text:
                    call.response_script = resp_script_elem.text.strip()

                # Extract document sending options
                doc_to_send_elem = call_elem.find('DocToSend')
                if doc_to_send_elem is not None and doc_to_send_elem.text:
                    call.doc_to_send = doc_to_send_elem.text

                to_pdf_elem = call_elem.find('ToPdf')
                if to_pdf_elem is not None and to_pdf_elem.text == '1':
                    call.to_pdf = True

                part_file_elem = call_elem.find('PartNameFile')
                if part_file_elem is not None and part_file_elem.text:
                    call.part_name_file = part_file_elem.text

                part_meta_elem = call_elem.find('PartNameMetadata')
                if part_meta_elem is not None and part_meta_elem.text:
                    call.part_name_metadata = part_meta_elem.text

                rest_calls.append(call)

        except Exception as e:
            # If parsing fails, return empty list
            pass

        return rest_calls

    def _parse_notification_mail(self, mail_xml: str) -> tuple:
        """Parse notification mail XML to extract subject and message."""
        subject = ""
        message = ""
        try:
            root = ET.fromstring(mail_xml)
            subject_elem = root.find("subject")
            if subject_elem is not None and subject_elem.text:
                subject = subject_elem.text
            message_elem = root.find("message")
            if message_elem is not None and message_elem.text:
                import html
                message = html.unescape(message_elem.text)
        except Exception:
            pass
        return subject, message

    def _parse_workflow_transition(self, elem: ET.Element) -> WorkflowTransition:
        """Parse a single workflow transition."""
        return WorkflowTransition(
            transition_no=get_element_int(elem.find("TransitionNo")),
            name=get_text_from_tstr(elem.find("Name")),
            description=get_text_from_tstr(elem.find("Descr")),
            task_from_no=get_element_int(elem.find("TaskFromNo")),
            task_to_no=get_element_int(elem.find("TaskToNo")),
            is_default=get_element_bool(elem.find("IsDefault")),
            condition=get_element_text(elem.find("Condition")),
            arrow_type=get_element_int(elem.find("ArrowType")),
            seq_pos=get_element_int(elem.find("SeqPos")),
            id=get_element_text(elem.find("Id")),
            action_text=get_text_from_tstr(elem.find("ActionText")),
        )

    def _parse_roles(self, root: ET.Element) -> None:
        """Parse permission roles."""
        roles_elem = root.find("Roles")
        if roles_elem is None:
            return

        for role_elem in roles_elem.findall("Role"):
            role = self._parse_role(role_elem)
            self.config.roles.append(role)

    def _parse_role(self, elem: ET.Element) -> Role:
        """Parse a single role."""
        permission_value = get_element_int(elem.find("Permission"))

        # Name and Description can be in TStr format or plain text
        name = get_text_from_tstr(elem.find("Name"))
        if not name:
            name = get_element_text(elem.find("Name"))

        description = get_text_from_tstr(elem.find("Description"))
        if not description:
            description = get_element_text(elem.find("Description"))

        role = Role(
            role_no=get_element_int(elem.find("RoleNo")),
            name=name,
            description=description,
            permission=permission_value,
            permission_names=decode_flags(ROLE_PERMISSION, permission_value),
            id=get_element_text(elem.find("Id")),
            is_deny=get_element_bool(elem.find("Deny")),
        )

        # Parse role assignments
        assignments_elem = elem.find("Assignments")
        if assignments_elem is not None:
            for assign_elem in assignments_elem.findall("Assignment"):
                assignment = RoleObjectAssignment(
                    object_type=get_element_int(assign_elem.find("ObjectType")),
                    object_no=get_element_int(assign_elem.find("ObjectNo")),
                    object_name=get_element_text(assign_elem.find("ObjectName")),
                    sub_obj_no=get_element_int(assign_elem.find("SubObjNo")),
                )
                assignment.object_type_name = get_lookup_name(OBJECT_TYPES, assignment.object_type)
                role.assignments.append(assignment)

        # Parse role users
        users_elem = elem.find("Users")
        if users_elem is not None:
            for user_elem in users_elem.findall("User"):
                user = User(
                    user_no=get_element_int(user_elem.find("UserNo")),
                    user_name=get_element_text(user_elem.find("UserName")),
                    display_name=get_element_text(user_elem.find("DisplayName")),
                    user_type=get_element_int(user_elem.find("UserType")),
                )
                user.user_type_name = get_lookup_name(USER_TYPE, user.user_type)
                role.users.append(user)

        return role

    def _parse_role_assignments(self, root: ET.Element) -> None:
        """Parse role assignments (object security)."""
        role_assigns_elem = root.find("RoleAssignments")
        if role_assigns_elem is None:
            return

        for ra_elem in role_assigns_elem.findall("RoleAssignment"):
            obj_type = get_element_int(ra_elem.find("ObjType"))
            role_assignment = RoleAssignment(
                role_no=get_element_int(ra_elem.find("RoleNo")),
                obj_type=obj_type,
                obj_type_name=get_lookup_name(OBJECT_TYPES, obj_type),
                obj_no=get_element_int(ra_elem.find("ObjNo")),
                sub_obj_no=get_element_int(ra_elem.find("SubObjNo")),
                user_no=get_element_int(ra_elem.find("UserNo")),
                condition=get_element_text(ra_elem.find("Condition")),
                stop_inheritance=get_element_int(ra_elem.find("StopInh")) == 1,
            )
            self.config.role_assignments.append(role_assignment)

    def _parse_eforms(self, root: ET.Element) -> None:
        """Parse electronic forms."""
        eforms_elem = root.find("EForms")
        if eforms_elem is None:
            return

        for eform_elem in eforms_elem.findall("EForm"):
            definition = get_element_text(eform_elem.find("FDef"))
            eform = EForm(
                form_no=get_element_int(eform_elem.find("FNo")),
                name=get_element_text(eform_elem.find("FName")),
                form_id=get_element_text(eform_elem.find("FormID")),
                version=get_element_int(eform_elem.find("FVer")),
                folder_no=get_element_int(eform_elem.find("FFold")) or None,
                created_date=format_date(get_element_text(eform_elem.find("DCrea"))),
                created_by=get_element_text(eform_elem.find("FCreUsNam")),
                definition=definition,
                id=get_element_text(eform_elem.find("Id")),
            )

            # Parse the JSON definition to extract components
            if definition:
                eform.components = self._parse_eform_definition(definition)

            self.config.eforms.append(eform)

    def _parse_eform_definition(self, definition: str) -> List[EFormComponent]:
        """Parse the eForm JSON definition to extract components."""
        components = []
        try:
            form_def = json.loads(definition)
            if "components" in form_def:
                components = self._parse_eform_components(form_def["components"])
        except json.JSONDecodeError:
            pass
        return components

    def _parse_eform_components(self, components_data: list) -> List[EFormComponent]:
        """Recursively parse eForm components."""
        components = []
        for comp_data in components_data:
            if not isinstance(comp_data, dict):
                continue

            # Extract validation info
            validate = comp_data.get("validate", {})
            conditional = comp_data.get("conditional", {})

            # Extract data source info for selects/lookups
            data_source = ""
            data = comp_data.get("data", {})
            if isinstance(data, dict):
                if "the" in data and isinstance(data["the"], dict):
                    data_source = data["the"].get("label", "")
                elif "theLookup" in data and isinstance(data["theLookup"], dict):
                    data_source = data["theLookup"].get("label", "")

            component = EFormComponent(
                key=comp_data.get("key", ""),
                label=comp_data.get("label", "") or comp_data.get("title", ""),
                type=comp_data.get("type", ""),
                default_value=str(comp_data.get("defaultValue", "")) if comp_data.get("defaultValue") else "",
                custom_default_value=comp_data.get("customDefaultValue", ""),
                calculate_value=comp_data.get("calculateValue", ""),
                validate_custom=validate.get("custom", "") if isinstance(validate, dict) else "",
                validate_required=validate.get("required", False) if isinstance(validate, dict) else False,
                conditional_show=conditional.get("show", "") if isinstance(conditional, dict) else "",
                conditional_when=conditional.get("when", "") if isinstance(conditional, dict) else "",
                conditional_json=conditional.get("json", "") if isinstance(conditional, dict) else "",
                custom_conditional=comp_data.get("customConditional", ""),
                hidden=comp_data.get("hidden", False),
                disabled=comp_data.get("disabled", False),
                data_source=data_source,
                logic=comp_data.get("logic", []),
                properties=comp_data.get("properties", {}),
            )

            # Recursively parse child components
            if "components" in comp_data:
                component.children = self._parse_eform_components(comp_data["components"])

            # Also check columns for nested components
            if "columns" in comp_data:
                for column in comp_data["columns"]:
                    if isinstance(column, dict) and "components" in column:
                        component.children.extend(self._parse_eform_components(column["components"]))

            # Also check rows for data grids
            if "rows" in comp_data and isinstance(comp_data["rows"], list):
                for row in comp_data["rows"]:
                    if isinstance(row, list):
                        for cell in row:
                            if isinstance(cell, dict) and "components" in cell:
                                component.children.extend(self._parse_eform_components(cell["components"]))

            components.append(component)

        return components

    def _parse_queries(self, root: ET.Element) -> None:
        """Parse saved searches/queries and query templates."""
        # Try QueryTemplates first (Therefore export format)
        queries_elem = root.find("QueryTemplates")
        query_tag = "QueryTemplate"
        query_no_tag = "QueryTemplateNo"

        if queries_elem is None:
            # Fall back to Queries (alternative format)
            queries_elem = root.find("Queries")
            query_tag = "Query"
            query_no_tag = "QueryNo"

        if queries_elem is None:
            return

        for query_elem in queries_elem.findall(query_tag):
            query_no = get_element_int(query_elem.find(query_no_tag))
            if query_no == 0:
                query_no = get_element_int(query_elem.find("QueryNo"))

            query = Query(
                query_no=query_no,
                name=get_text_from_tstr(query_elem.find("Name")),
                description=get_text_from_tstr(query_elem.find("Description")),
                category_no=get_element_int(query_elem.find("CtgryNo")) or None,
                folder_no=get_element_int(query_elem.find("FolderNo")) or None,
                version_no=get_element_int(query_elem.find("VersionNo")) or get_element_int(query_elem.find("Version")),
                id=get_element_text(query_elem.find("Id")),
                query_id=get_element_text(query_elem.find("QueryID")),
            )

            # Parse query fields
            fields_elem = query_elem.find("Fields")
            if fields_elem is not None:
                for field_elem in fields_elem.findall("Field"):
                    qfield = QueryField(
                        field_no=get_element_int(field_elem.find("FieldNo")),
                        caption=get_element_text(field_elem.find("Caption")),
                        width=get_element_int(field_elem.find("Width")),
                        alignment=get_element_int(field_elem.find("Alignment")),
                        disp_pos=get_element_int(field_elem.find("DispPos")),
                        visible=get_element_bool(field_elem.find("Visible"), default=True),
                    )
                    qfield.alignment_name = get_lookup_name(QUERY_FIELD_ALIGNMENT, qfield.alignment)
                    query.fields.append(qfield)

            self.config.queries.append(query)

    def _parse_keyword_dictionaries(self, root: ET.Element) -> None:
        """Parse keyword dictionaries."""
        dicts_elem = root.find("KeywordDictionaries")
        if dicts_elem is None:
            return

        # Try Dictionary first (Therefore export format), then KeywordDictionary
        dict_elements = dicts_elem.findall("Dictionary")
        if not dict_elements:
            dict_elements = dicts_elem.findall("KeywordDictionary")

        for dict_elem in dict_elements:
            # Handle both Therefore export format (KeyDicNo/KeyDicName) and standard format
            dictionary_no = get_element_int(dict_elem.find("KeyDicNo"))
            if dictionary_no == 0:
                dictionary_no = get_element_int(dict_elem.find("DictionaryNo"))

            name = get_element_text(dict_elem.find("KeyDicName"))
            if not name:
                name = get_text_from_tstr(dict_elem.find("Name"))

            # Get SingleTypeNo and MulitTypeNo - these are what fields reference
            single_type_no = get_element_int(dict_elem.find("SingleTypeNo"))
            multi_type_no = get_element_int(dict_elem.find("MulitTypeNo"))  # Note: "Mulit" is the actual spelling in Therefore

            dictionary = KeywordDictionary(
                dictionary_no=dictionary_no,
                name=name,
                description=get_text_from_tstr(dict_elem.find("Description")),
                folder_no=get_element_int(dict_elem.find("FolderNo")) or None,
                single_type_no=single_type_no if single_type_no != 0 else None,
                multi_type_no=multi_type_no if multi_type_no != 0 else None,
                id=get_element_text(dict_elem.find("Id")),
            )

            # Parse keywords
            keywords_elem = dict_elem.find("Keywords")
            if keywords_elem is not None:
                # Try KW first, then Keyword
                kw_elements = keywords_elem.findall("KW")
                if not kw_elements:
                    kw_elements = keywords_elem.findall("Keyword")

                for kw_elem in kw_elements:
                    # Handle both formats for keyword value
                    kw_no = get_element_int(kw_elem.find("KeywordNo"))
                    if kw_no == 0:
                        kw_no = get_element_int(kw_elem.find("KWNo"))

                    # Try multiple possible element names for the keyword value
                    value = get_text_from_tstr(kw_elem.find("Keyword"))
                    if not value:
                        value = get_text_from_tstr(kw_elem.find("Value"))
                    if not value:
                        value = get_element_text(kw_elem.find("KWValue"))

                    keyword = Keyword(
                        keyword_no=kw_no,
                        value=value,
                        parent_no=get_element_int(kw_elem.find("ParentNo")) or None,
                        id=get_element_text(kw_elem.find("Id")),
                    )
                    dictionary.keywords.append(keyword)

            self.config.keyword_dictionaries.append(dictionary)

    def _parse_tree_views(self, root: ET.Element) -> None:
        """Parse tree view configurations."""
        treeviews_elem = root.find("TreeViews")
        if treeviews_elem is None:
            return

        for tv_elem in treeviews_elem.findall("TreeView"):
            treeview = TreeView(
                treeview_no=get_element_int(tv_elem.find("TreeViewNo")),
                name=get_text_from_tstr(tv_elem.find("Name")),
                category_no=get_element_int(tv_elem.find("CtgryNo")) or None,
                folder_no=get_element_int(tv_elem.find("FolderNo")) or None,
                id=get_element_text(tv_elem.find("Id")),
            )

            # Parse levels
            levels_elem = tv_elem.find("Levels")
            if levels_elem is not None:
                for level_elem in levels_elem.findall("Level"):
                    level = TreeViewLevel(
                        level_no=get_element_int(level_elem.find("LevelNo")),
                        field_no=get_element_int(level_elem.find("FieldNo")),
                        field_name=get_element_text(level_elem.find("FieldName")),
                        level_function=get_element_int(level_elem.find("LevelFunction")),
                        sort_order=get_element_int(level_elem.find("SortOrder")),
                    )
                    level.level_function_name = get_lookup_name(
                        TREEVIEW_LEVEL_FUNCTION, level.level_function
                    )
                    level.sort_order_name = get_lookup_name(
                        TREEVIEW_SORT_ORDER, level.sort_order
                    )
                    treeview.levels.append(level)

            self.config.tree_views.append(treeview)

    def _parse_counters(self, root: ET.Element) -> None:
        """Parse automatic counters."""
        counters_elem = root.find("Counters")
        if counters_elem is None:
            return

        for counter_elem in counters_elem.findall("Counter"):
            # Handle both Therefore export format (CNo/Format/Type) and standard format
            counter_no = get_element_int(counter_elem.find("CNo"))
            if counter_no == 0:
                counter_no = get_element_int(counter_elem.find("CounterNo"))

            format_string = get_element_text(counter_elem.find("Format"))
            if not format_string:
                format_string = get_element_text(counter_elem.find("FormatString"))

            counter_type = get_element_int(counter_elem.find("Type"))
            if counter_type == 0:
                counter_type = get_element_int(counter_elem.find("CounterType"))

            current_value = get_element_int(counter_elem.find("Next"))
            if current_value == 0:
                current_value = get_element_int(counter_elem.find("CurrentValue"))

            counter = Counter(
                counter_no=counter_no,
                name=get_element_text(counter_elem.find("Name")) or str(abs(counter_no)),
                counter_type=counter_type,
                format_string=format_string,
                current_value=current_value,
                folder_no=get_element_int(counter_elem.find("FolderNo")) or None,
                id=get_element_text(counter_elem.find("Id")),
            )
            counter.counter_type_name = get_lookup_name(COUNTER_TYPE, counter.counter_type)
            self.config.counters.append(counter)

        # Sort counters numerically by counter_no (using absolute value)
        self.config.counters.sort(key=lambda c: abs(c.counter_no))

    def _parse_data_types(self, root: ET.Element) -> None:
        """Parse custom data types."""
        # Try both element name formats
        datatypes_elem = root.find("Datatypes")
        if datatypes_elem is None:
            datatypes_elem = root.find("DataTypes")
        if datatypes_elem is None:
            return

        # Try both child element name formats
        dt_elements = datatypes_elem.findall("Datatype")
        if not dt_elements:
            dt_elements = datatypes_elem.findall("DataType")

        for dt_elem in dt_elements:
            # Try both field name formats for the type number
            datatype_no = get_element_int(dt_elem.find("TypeNo"))
            if datatype_no == 0:
                datatype_no = get_element_int(dt_elem.find("DataTypeNo"))

            datatype = DataType(
                datatype_no=datatype_no,
                name=get_element_text(dt_elem.find("Name")),
                type_group=get_element_int(dt_elem.find("TypeGroup")),
                table_name=get_element_text(dt_elem.find("TableName")),
                dictionary_no=get_element_int(dt_elem.find("DictionaryNo")) or None,
                id=get_element_text(dt_elem.find("Id")),
            )
            datatype.type_group_name = get_lookup_name(DATA_TYPE_GROUP, datatype.type_group)

            # Parse columns
            columns_elem = dt_elem.find("Columns")
            if columns_elem is not None:
                for col_elem in columns_elem.findall("Column"):
                    column = DataTypeColumn(
                        col_no=get_element_int(col_elem.find("ColNo")),
                        col_name=get_element_text(col_elem.find("ColName")),
                        caption=get_element_text(col_elem.find("Caption")),
                        type_no=get_element_int(col_elem.find("TypeNo")),
                        length=get_element_int(col_elem.find("Length")),
                        is_primary=get_element_bool(col_elem.find("IsPrimary")),
                    )
                    column.type_name = get_lookup_name(FIELD_TYPES, column.type_no)
                    datatype.columns.append(column)

            self.config.data_types.append(datatype)

    def _parse_stamps(self, root: ET.Element) -> None:
        """Parse stamp definitions."""
        stamps_elem = root.find("Stamps")
        if stamps_elem is None:
            return

        for stamp_elem in stamps_elem.findall("Stamp"):
            stamp = Stamp(
                stamp_no=get_element_int(stamp_elem.find("StampNo")),
                name=get_element_text(stamp_elem.find("Name")),
                stamp_type=get_element_int(stamp_elem.find("Type")),
                folder_no=get_element_int(stamp_elem.find("Folder")) or None,
                filename=get_element_text(stamp_elem.find("Filename")),
                id=get_element_text(stamp_elem.find("Id")),
            )
            stamp.stamp_type_name = get_lookup_name(STAMP_TYPE, stamp.stamp_type)
            self.config.stamps.append(stamp)

    def _parse_capture_profiles(self, root: ET.Element) -> None:
        """Parse capture profiles."""
        profiles_elem = root.find("CaptureProfiles")
        if profiles_elem is None:
            return

        for profile_elem in profiles_elem.findall("CaptureProfile"):
            profile = CaptureProfile(
                profile_no=get_element_int(profile_elem.find("ProfileNo")),
                name=get_element_text(profile_elem.find("Name")),
                folder_no=get_element_int(profile_elem.find("FolderNo")) or None,
                color_mode=get_element_int(profile_elem.find("ColorMode")),
                doc_break=get_element_int(profile_elem.find("DocBreak")),
                storage_mode=get_element_int(profile_elem.find("StorageMode")),
                id=get_element_text(profile_elem.find("Id")),
            )
            profile.color_mode_name = get_lookup_name(CAPTURE_COLOR_MODES, profile.color_mode)
            profile.doc_break_name = get_lookup_name(CAPTURE_DOC_BREAK, profile.doc_break)
            profile.storage_mode_name = get_lookup_name(STORAGE_MODE, profile.storage_mode)
            self.config.capture_profiles.append(profile)

    def _parse_content_connector_sources(self, root: ET.Element) -> None:
        """Parse content connector sources."""
        sources_elem = root.find("ContentConnectorSources")
        if sources_elem is None:
            return

        for source_elem in sources_elem.findall("Source"):
            source = ContentConnectorSource(
                source_no=get_element_int(source_elem.find("SourceNo")),
                name=get_element_text(source_elem.find("Name")),
                source_mode=get_element_int(source_elem.find("SourceMode")),
                folder_no=get_element_int(source_elem.find("FolderNo")) or None,
                id=get_element_text(source_elem.find("Id")),
            )
            source.source_mode_name = get_lookup_name(
                CONTENT_CONNECTOR_SOURCE_MODE, source.source_mode
            )
            self.config.content_connector_sources.append(source)

    def _parse_retention_policies(self, root: ET.Element) -> None:
        """Parse retention policies."""
        policies_elem = root.find("RetentionPolicies")
        if policies_elem is None:
            return

        for policy_elem in policies_elem.findall("RetentionPolicy"):
            policy = RetentionPolicy(
                policy_no=get_element_int(policy_elem.find("RetentionPolicyNo")),
                name=get_element_text(policy_elem.find("Name")),
                months=get_element_int(policy_elem.find("Months")),
                purge=get_element_bool(policy_elem.find("Purge")),
                delete_disk=get_element_bool(policy_elem.find("DeleteDisk")),
                starting=get_element_text(policy_elem.find("Starting")),
                id=get_element_text(policy_elem.find("Id")),
            )

            # Parse categories that use this retention policy
            sub_ctgrys_elem = policy_elem.find("SubCtgrys")
            if sub_ctgrys_elem is not None:
                for sc_elem in sub_ctgrys_elem.findall("SubCtgry"):
                    cat_assignment = RetentionPolicyCategory(
                        category_no=get_element_int(sc_elem.find("CtgryNo")),
                        sub_category_no=get_element_int(sc_elem.find("SubCtgryNo")),
                        category_name=get_text_from_tstr(sc_elem.find("CtgryName")),
                        no_retention=get_element_bool(sc_elem.find("NoRetention")),
                    )
                    policy.categories.append(cat_assignment)

            self.config.retention_policies.append(policy)
