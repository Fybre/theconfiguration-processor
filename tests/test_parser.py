"""Tests for the Therefore configuration parser."""

import pytest
from pathlib import Path
import tempfile
import os

from src.parser import ConfigurationParser, Configuration
from src.parser.models import Category, Field, WorkflowProcess
from src.parser.constants import (
    FIELD_TYPES, WORKFLOW_TASK_TYPE, OBJECT_TYPES, get_lookup_name, decode_flags,
    ROLE_PERMISSION
)
from src.utils.helpers import (
    get_text_from_tstr, format_date, escape_html, slugify, decode_flags as helper_decode_flags
)
from src.generator import HTMLGenerator


# Sample XML for testing
SAMPLE_XML = """<?xml version="1.0" encoding="utf-8"?>
<Configuration>
    <Version>123456</Version>
    <NewImportExport>1</NewImportExport>
    <Categories>
        <Category>
            <CtgryNo>-1</CtgryNo>
            <Name UPT="1"><TStr><T><L>1033</L><S>Test Category</S></T></TStr></Name>
            <Title>Test Category Title</Title>
            <Description UPT="1"><TStr><T><L>1033</L><S>Test description</S></T></TStr></Description>
            <Width>200</Width>
            <Height>100</Height>
            <FolderNo>-10</FolderNo>
            <FulltextMode>1</FulltextMode>
            <CheckInMode>1</CheckInMode>
            <Version>1</Version>
            <Id>TEST-GUID-001</Id>
            <Fields>
                <Field>
                    <FieldNo>-101</FieldNo>
                    <FieldID>test_field</FieldID>
                    <ColName>TestField</ColName>
                    <Caption UPT="1"><TStr><T><L>1033</L><S>Test Field</S></T></TStr></Caption>
                    <TypeNo>1</TypeNo>
                    <Length>50</Length>
                    <Width>100</Width>
                    <Height>20</Height>
                    <PosX>10</PosX>
                    <PosY>10</PosY>
                    <TabOrderPos>1</TabOrderPos>
                    <DispOrderPos>1</DispOrderPos>
                    <IndexType>1</IndexType>
                    <Id>FIELD-GUID-001</Id>
                </Field>
                <Field>
                    <FieldNo>-102</FieldNo>
                    <FieldID>date_field</FieldID>
                    <Caption UPT="1"><TStr><T><L>1033</L><S>Date Field</S></T></TStr></Caption>
                    <TypeNo>3</TypeNo>
                    <TabOrderPos>2</TabOrderPos>
                    <DispOrderPos>2</DispOrderPos>
                    <Id>FIELD-GUID-002</Id>
                </Field>
            </Fields>
        </Category>
    </Categories>
    <Workflows>
        <Workflow>
            <ProcessNo>-5</ProcessNo>
            <Name UPT="1"><TStr><T><L>1033</L><S>Test Workflow</S></T></TStr></Name>
            <Description UPT="1"><TStr><T><L>1033</L><S>Test workflow description</S></T></TStr></Description>
            <FolderNo>-10</FolderNo>
            <Id>WF-GUID-001</Id>
            <Tasks>
                <Task>
                    <TaskNo>-50</TaskNo>
                    <TaskId>start_task</TaskId>
                    <Name UPT="1"><TStr><T><L>1033</L><S>Start</S></T></TStr></Name>
                    <Type>1</Type>
                    <PosX>100</PosX>
                    <PosY>50</PosY>
                    <Id>TASK-GUID-001</Id>
                    <Transitions>
                        <TR>
                            <TransitionNo>-500</TransitionNo>
                            <Name UPT="1"><TStr><T><L>1033</L><S>To Review</S></T></TStr></Name>
                            <TaskFromNo>-50</TaskFromNo>
                            <TaskToNo>-51</TaskToNo>
                            <IsDefault>1</IsDefault>
                            <Id>TR-GUID-001</Id>
                        </TR>
                    </Transitions>
                </Task>
                <Task>
                    <TaskNo>-51</TaskNo>
                    <TaskId>review_task</TaskId>
                    <Name UPT="1"><TStr><T><L>1033</L><S>Review</S></T></TStr></Name>
                    <Type>3</Type>
                    <PosX>200</PosX>
                    <PosY>50</PosY>
                    <Duration>24</Duration>
                    <Id>TASK-GUID-002</Id>
                    <Users>
                        <User>
                            <UserNo>1</UserNo>
                            <UserName>admin</UserName>
                            <DisplayName>Administrator</DisplayName>
                            <UserType>1</UserType>
                        </User>
                    </Users>
                </Task>
            </Tasks>
        </Workflow>
    </Workflows>
    <Folders>
        <Folder>
            <FolderNo>-10</FolderNo>
            <Name UPT="1"><TStr><T><L>1033</L><S>Root Folder</S></T></TStr></Name>
            <ParentNo>0</ParentNo>
            <FolderType>17</FolderType>
            <Id>FOLDER-GUID-001</Id>
        </Folder>
        <Folder>
            <FolderNo>-11</FolderNo>
            <Name UPT="1"><TStr><T><L>1033</L><S>Sub Folder</S></T></TStr></Name>
            <ParentNo>-10</ParentNo>
            <FolderType>17</FolderType>
            <Id>FOLDER-GUID-002</Id>
        </Folder>
    </Folders>
    <Users>
        <User>
            <UserNo>1</UserNo>
            <UserName>admin</UserName>
            <DisplayName>Administrator</DisplayName>
            <UserType>1</UserType>
            <Id>USER-GUID-001</Id>
        </User>
        <User>
            <UserNo>2</UserNo>
            <UserName>users</UserName>
            <DisplayName>All Users</DisplayName>
            <UserType>2</UserType>
            <Id>USER-GUID-002</Id>
        </User>
    </Users>
    <Roles>
        <Role>
            <RoleNo>-1</RoleNo>
            <Name>Admin Role</Name>
            <Description>Full administrator access</Description>
            <Permission>3</Permission>
            <Id>ROLE-GUID-001</Id>
            <Users>
                <User>
                    <UserNo>1</UserNo>
                    <UserName>admin</UserName>
                    <DisplayName>Administrator</DisplayName>
                    <UserType>1</UserType>
                </User>
            </Users>
        </Role>
    </Roles>
    <EForms>
        <EForm>
            <FNo>-1</FNo>
            <FName>Test Form</FName>
            <FormID>test_form</FormID>
            <FVer>1</FVer>
            <FFold>-10</FFold>
            <DCrea>20240115120000000</DCrea>
            <FCreUsNam>admin</FCreUsNam>
            <FDef>{}</FDef>
            <Id>EFORM-GUID-001</Id>
        </EForm>
    </EForms>
    <Queries>
        <Query>
            <QueryNo>-1</QueryNo>
            <Name UPT="1"><TStr><T><L>1033</L><S>Test Query</S></T></TStr></Name>
            <CtgryNo>-1</CtgryNo>
            <FolderNo>-10</FolderNo>
            <Id>QUERY-GUID-001</Id>
        </Query>
    </Queries>
    <KeywordDictionaries>
        <KeywordDictionary>
            <DictionaryNo>-1</DictionaryNo>
            <Name UPT="1"><TStr><T><L>1033</L><S>Status Values</S></T></TStr></Name>
            <FolderNo>-10</FolderNo>
            <Id>DICT-GUID-001</Id>
            <Keywords>
                <KW>
                    <KeywordNo>-100</KeywordNo>
                    <Value UPT="1"><TStr><T><L>1033</L><S>Active</S></T></TStr></Value>
                    <Id>KW-GUID-001</Id>
                </KW>
                <KW>
                    <KeywordNo>-101</KeywordNo>
                    <Value UPT="1"><TStr><T><L>1033</L><S>Inactive</S></T></TStr></Value>
                    <Id>KW-GUID-002</Id>
                </KW>
            </Keywords>
        </KeywordDictionary>
    </KeywordDictionaries>
    <Counters>
        <Counter>
            <CounterNo>-1</CounterNo>
            <Name>Document Counter</Name>
            <CounterType>2</CounterType>
            <FormatString>DOC-{0:0000}</FormatString>
            <CurrentValue>100</CurrentValue>
            <FolderNo>-10</FolderNo>
            <Id>COUNTER-GUID-001</Id>
        </Counter>
    </Counters>
    <Stamps>
        <Stamp>
            <StampNo>-1</StampNo>
            <Name>Approved</Name>
            <Type>0</Type>
            <Filename>approved.pdf</Filename>
            <Id>STAMP-GUID-001</Id>
        </Stamp>
    </Stamps>
</Configuration>
"""


@pytest.fixture
def sample_xml_file():
    """Create a temporary sample XML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(SAMPLE_XML)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def parsed_config(sample_xml_file):
    """Parse the sample XML and return the configuration."""
    parser = ConfigurationParser()
    return parser.parse(sample_xml_file)


class TestConstants:
    """Tests for constants module."""

    def test_field_types(self):
        """Test field type lookup."""
        assert FIELD_TYPES[1] == "String"
        assert FIELD_TYPES[3] == "Date"
        assert FIELD_TYPES[6] == "Logical"

    def test_workflow_task_types(self):
        """Test workflow task type lookup."""
        assert WORKFLOW_TASK_TYPE[1] == "Start"
        assert WORKFLOW_TASK_TYPE[2] == "End"
        assert WORKFLOW_TASK_TYPE[3] == "Manual Task"

    def test_object_types(self):
        """Test object type lookup."""
        assert OBJECT_TYPES[3] == "Category"
        assert OBJECT_TYPES[17] == "Folder"
        assert OBJECT_TYPES[19] == "Workflow Process"

    def test_get_lookup_name(self):
        """Test lookup name helper."""
        assert get_lookup_name(FIELD_TYPES, 1) == "String"
        assert get_lookup_name(FIELD_TYPES, 999) == "Unknown (999)"
        assert get_lookup_name(FIELD_TYPES, 999, "Custom") == "Custom (999)"

    def test_decode_flags(self):
        """Test flag decoding."""
        # Test role permissions (Operator=1, Administrator=2)
        flags = decode_flags(ROLE_PERMISSION, 3)
        assert "Operator" in flags
        assert "Administrator" in flags

        # Test empty flags
        flags = decode_flags(ROLE_PERMISSION, 0)
        assert flags == []


class TestHelpers:
    """Tests for helper functions."""

    def test_format_date(self):
        """Test date formatting."""
        assert format_date("20240115120000000") == "2024-01-15 12:00:00"
        assert format_date("20240115") == "2024-01-15"
        assert format_date("") == ""
        assert format_date("0") == ""
        assert format_date("invalid") == "invalid"

    def test_escape_html(self):
        """Test HTML escaping."""
        assert escape_html("<script>") == "&lt;script&gt;"
        assert escape_html("a & b") == "a &amp; b"
        assert escape_html('"quote"') == "&quot;quote&quot;"
        assert escape_html("") == ""

    def test_slugify(self):
        """Test slugification."""
        assert slugify("Test Category") == "test-category"
        assert slugify("Test  Multiple   Spaces") == "test-multiple-spaces"
        assert slugify("Special!@#Characters") == "specialcharacters"
        assert slugify("") == ""


class TestParser:
    """Tests for the configuration parser."""

    def test_parse_version(self, parsed_config):
        """Test version parsing."""
        assert parsed_config.version == "123456"

    def test_parse_categories(self, parsed_config):
        """Test category parsing."""
        assert len(parsed_config.categories) == 1
        category = parsed_config.categories[0]
        assert category.category_no == -1
        assert category.name == "Test Category"
        assert category.title == "Test Category Title"
        assert category.description == "Test description"
        assert category.folder_no == -10
        assert category.fulltext_mode == 1
        assert category.id == "TEST-GUID-001"

    def test_parse_fields(self, parsed_config):
        """Test field parsing."""
        category = parsed_config.categories[0]
        assert len(category.fields) == 2

        field1 = category.fields[0]
        assert field1.field_no == -101
        assert field1.field_id == "test_field"
        assert field1.caption == "Test Field"
        assert field1.type_no == 1
        assert field1.type_name == "String"
        assert field1.length == 50
        assert field1.index_type == 1

        field2 = category.fields[1]
        assert field2.caption == "Date Field"
        assert field2.type_no == 3
        assert field2.type_name == "Date"

    def test_parse_workflows(self, parsed_config):
        """Test workflow parsing."""
        assert len(parsed_config.workflows) == 1
        workflow = parsed_config.workflows[0]
        assert workflow.process_no == -5
        assert workflow.name == "Test Workflow"
        assert workflow.description == "Test workflow description"
        assert len(workflow.tasks) == 2

    def test_parse_workflow_tasks(self, parsed_config):
        """Test workflow task parsing."""
        workflow = parsed_config.workflows[0]

        start_task = workflow.tasks[0]
        assert start_task.task_no == -50
        assert start_task.name == "Start"
        assert start_task.type_no == 1
        assert start_task.type_name == "Start"
        assert len(start_task.transitions) == 1

        review_task = workflow.tasks[1]
        assert review_task.name == "Review"
        assert review_task.type_no == 3
        assert review_task.type_name == "Manual Task"
        assert review_task.duration == 24
        assert len(review_task.assigned_users) == 1

    def test_parse_transitions(self, parsed_config):
        """Test transition parsing."""
        workflow = parsed_config.workflows[0]
        start_task = workflow.tasks[0]
        transition = start_task.transitions[0]

        assert transition.transition_no == -500
        assert transition.name == "To Review"
        assert transition.task_from_no == -50
        assert transition.task_to_no == -51
        assert transition.is_default is True

    def test_parse_folders(self, parsed_config):
        """Test folder parsing with hierarchy."""
        # Root folders
        assert len(parsed_config.folders) == 1
        root_folder = parsed_config.folders[0]
        assert root_folder.folder_no == -10
        assert root_folder.name == "Root Folder"
        assert root_folder.parent_no is None

        # Child folder
        assert len(root_folder.children) == 1
        child_folder = root_folder.children[0]
        assert child_folder.folder_no == -11
        assert child_folder.name == "Sub Folder"
        assert child_folder.parent_no == -10

    def test_parse_users(self, parsed_config):
        """Test user parsing."""
        assert len(parsed_config.users) == 2

        admin = parsed_config.users[0]
        assert admin.user_no == 1
        assert admin.user_name == "admin"
        assert admin.display_name == "Administrator"
        assert admin.user_type == 1
        assert admin.user_type_name == "User"

        group = parsed_config.users[1]
        assert group.user_type == 2
        assert group.user_type_name == "Group"

    def test_parse_roles(self, parsed_config):
        """Test role parsing."""
        assert len(parsed_config.roles) == 1
        role = parsed_config.roles[0]
        assert role.role_no == -1
        assert role.name == "Admin Role"
        assert role.permission == 3
        assert "Operator" in role.permission_names
        assert "Administrator" in role.permission_names
        assert len(role.users) == 1

    def test_parse_eforms(self, parsed_config):
        """Test EForm parsing."""
        assert len(parsed_config.eforms) == 1
        eform = parsed_config.eforms[0]
        assert eform.form_no == -1
        assert eform.name == "Test Form"
        assert eform.form_id == "test_form"
        assert eform.created_by == "admin"
        assert "2024-01-15" in eform.created_date

    def test_parse_queries(self, parsed_config):
        """Test query parsing."""
        assert len(parsed_config.queries) == 1
        query = parsed_config.queries[0]
        assert query.query_no == -1
        assert query.name == "Test Query"
        assert query.category_no == -1

    def test_parse_keyword_dictionaries(self, parsed_config):
        """Test keyword dictionary parsing."""
        assert len(parsed_config.keyword_dictionaries) == 1
        dictionary = parsed_config.keyword_dictionaries[0]
        assert dictionary.dictionary_no == -1
        assert dictionary.name == "Status Values"
        assert len(dictionary.keywords) == 2
        assert dictionary.keywords[0].value == "Active"
        assert dictionary.keywords[1].value == "Inactive"

    def test_parse_counters(self, parsed_config):
        """Test counter parsing."""
        assert len(parsed_config.counters) == 1
        counter = parsed_config.counters[0]
        assert counter.counter_no == -1
        assert counter.name == "Document Counter"
        assert counter.counter_type == 2
        assert counter.counter_type_name == "Text (formatted)"
        assert counter.format_string == "DOC-{0:0000}"
        assert counter.current_value == 100

    def test_parse_stamps(self, parsed_config):
        """Test stamp parsing."""
        assert len(parsed_config.stamps) == 1
        stamp = parsed_config.stamps[0]
        assert stamp.stamp_no == -1
        assert stamp.name == "Approved"
        assert stamp.stamp_type == 0
        assert stamp.stamp_type_name == "PDF"
        assert stamp.filename == "approved.pdf"


class TestConfigurationModel:
    """Tests for the Configuration model."""

    def test_build_lookup_maps(self, parsed_config):
        """Test lookup map building."""
        # Maps should be built during parsing
        assert parsed_config.get_category(-1) is not None
        assert parsed_config.get_folder(-10) is not None
        assert parsed_config.get_user(1) is not None

    def test_get_folder_path(self, parsed_config):
        """Test folder path resolution."""
        path = parsed_config.get_folder_path(-11)
        assert "Root Folder" in path
        assert "Sub Folder" in path

    def test_get_statistics(self, parsed_config):
        """Test statistics calculation."""
        stats = parsed_config.get_statistics()
        assert stats["categories"] == 1
        assert stats["fields"] == 2
        assert stats["workflows"] == 1
        assert stats["workflow_tasks"] == 2
        assert stats["users"] == 1  # Only user type 1
        assert stats["groups"] == 1  # Only user type 2
        assert stats["roles"] == 1


class TestHTMLGenerator:
    """Tests for the HTML generator."""

    def test_generate_html(self, parsed_config):
        """Test HTML generation."""
        generator = HTMLGenerator(parsed_config, title="Test Documentation")
        html = generator._generate_html()

        # Check basic structure
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html
        assert "Test Documentation" in html

        # Check sections exist
        assert 'id="overview"' in html
        assert 'id="categories"' in html
        assert 'id="workflows"' in html
        assert 'id="folders"' in html

    def test_generate_file(self, parsed_config):
        """Test file generation."""
        generator = HTMLGenerator(parsed_config)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_output.html"
            result = generator.generate(str(output_path))

            assert Path(result).exists()
            content = Path(result).read_text()
            assert "<!DOCTYPE html>" in content

    def test_category_in_output(self, parsed_config):
        """Test that categories appear in output."""
        generator = HTMLGenerator(parsed_config)
        html = generator._generate_html()

        assert "Test Category" in html
        assert "Test Field" in html
        assert "Date Field" in html

    def test_workflow_in_output(self, parsed_config):
        """Test that workflows appear in output."""
        generator = HTMLGenerator(parsed_config)
        html = generator._generate_html()

        assert "Test Workflow" in html
        assert "Start" in html
        assert "Review" in html


class TestIntegration:
    """Integration tests using real sample file if available."""

    @pytest.fixture
    def real_sample_file(self):
        """Get path to real sample file if it exists."""
        sample_path = Path(__file__).parent.parent / "samples" / "TheConfiguration.xml"
        if sample_path.exists():
            return str(sample_path)
        pytest.skip("Real sample file not available")

    def test_parse_real_sample(self, real_sample_file):
        """Test parsing the real sample file."""
        parser = ConfigurationParser()
        config = parser.parse(real_sample_file)

        assert config.version is not None
        assert len(config.categories) > 0
        # The real file should have data
        stats = config.get_statistics()
        assert stats["categories"] > 0

    def test_generate_from_real_sample(self, real_sample_file):
        """Test generating documentation from real sample."""
        parser = ConfigurationParser()
        config = parser.parse(real_sample_file)
        generator = HTMLGenerator(config, title="Real Sample Test")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "real_sample_output.html"
            result = generator.generate(str(output_path))

            assert Path(result).exists()
            content = Path(result).read_text()
            # Check it's valid HTML with content
            assert len(content) > 1000
            assert "<!DOCTYPE html>" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
