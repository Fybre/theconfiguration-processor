"""
Therefore DB Codes - Lookup tables for integer codes in the Therefore database schema.
Based on "Therefore 2020 DB Codes.pdf"
"""

# Object Type Constants (for use in code instead of magic numbers)
class ObjectType:
    """Constants for Therefore object types."""
    SERVER = 1
    DOCUMENT = 2
    CATEGORY = 3
    CATEGORY_FIELD = 4
    DATATYPE = 5
    QUERY = 10
    USER = 11
    GROUP = 12
    FOLDER = 17
    WORKFLOW_PROCESS = 19
    WORKFLOW_TASK = 20
    KEYWORD_DICTIONARY = 22
    TREE_VIEW = 28
    COUNTER = 32
    CASE_DEFINITION = 37
    STAMP = 40
    EFORM = 47
    ROLE = 51


class UserType:
    """Constants for Therefore user types."""
    USER = 1
    GROUP = 2
    SYSTEM = 3


# TheActno*.TypeNo - Object Types
OBJECT_TYPES = {
    1: "Server",
    2: "Document",
    3: "Category",
    4: "Category Field",
    5: "Datatype",
    6: "Media Pool",
    7: "Media",
    8: "Parser Profile",
    9: "Spool Type",
    10: "Query",
    11: "User",
    12: "Group",
    13: "Capture Profile",
    14: "Preprocessor",
    15: "COLD Form",
    16: "Query Template",
    17: "Folder",
    18: "Document Loader Profile",
    19: "Workflow Process",
    20: "Workflow Task",
    21: "Workflow Instance",
    22: "Keyword Dictionary",
    23: "Storage Policy",
    24: "Device",
    25: "Storage Area",
    26: "Retention Policy",
    27: "MFP Device",
    28: "Tree View",
    29: "Universal Connector Profile",
    30: "Task",
    31: "SharePoint Profile",
    32: "Automatic Counter",
    33: "Data Extractor",
    34: "Content Connector source",
    35: "Replication connection",
    36: "Replication table",
    37: "Case definition",
    38: "Case Header",
    39: "Office Profile",
    40: "Stamp",
    41: "SQL Reporting Definition",
    42: "PowerBI Table",
    43: "PowerBI Dataset",
    44: "SharePoint Connector",
    45: "Cloud Storage",
    46: "Common Script",
    47: "EForm",
    48: "EForm Submission",
    49: "ESignature Provider",
    50: "Dashboard",
    51: "Role",
}

# TheCaptBarcode.BarType - Barcode Types (flags)
BARCODE_TYPES = {
    1: "3 of 9",
    2: "Interleaved 2 of 5",
    4: "Code 128",
    8: "EAN",
    16: "UPC-A",
    32: "UPC-E",
    64: "Codabar",
    128: "Code 93",
    256: "Postnet",
    512: "Linear 2 of 5",
    1024: "Aztec",
    2048: "PDF 417",
    4096: "Datamatrix",
    16384: "QR",
    1048576: "EAN-5 Addon",
}

# TheCaptBarcode.Encoding
BARCODE_ENCODING = {
    0: "Automatic",
    1: "UTF-8",
    2: "UTF-16",
}

# TheCaptBarcode.Frequency
BARCODE_FREQUENCY = {
    0: "None",
    1: "Exactly one page",
    2: "Some pages",
    3: "Each page",
}

# TheCaptBarcode.Orientation (flags)
BARCODE_ORIENTATION = {
    1: "0°",
    2: "90°",
    4: "180°",
    8: "270°",
}

# TheCaptBarcode.Quality
BARCODE_QUALITY = {
    0: "Good",
    1: "Normal",
    2: "Poor",
}

# TheCaptBarcode.Ratio
BARCODE_RATIO = {
    0: "3:1",
    1: "2:1",
}

# TheCaptGrid.TypeNo
CAPTURE_GRID_TYPES = {
    1: "Display the document counter",
    2: "Display the category name",
    3: "Display the page count",
    4: "Display a category field",
    5: "Display information",
}

# TheCaptProfile.ColorMode
CAPTURE_COLOR_MODES = {
    1: "Black & white",
    2: "24-bit Color",
    4: "256 colors",
    8: "256-Level gray",
    16: "16-Level gray",
    32: "4-Level gray",
    64: "3-bit color",
    128: "6-bit color",
    256: "12-bit color",
}

# TheCaptProfile.DocBreak
CAPTURE_DOC_BREAK = {
    1: "Single page documents",
    2: "Use separator pages",
    3: "Manual",
    4: "Barcode/OCR",
    5: "Barcode - skip page with barcode",
}

# TheCaptProfile.ScanDropOutColor
SCAN_DROPOUT_COLOR = {
    0: "None",
    1: "Red",
    2: "Green",
    4: "Blue",
}

# TheCaptProfile.ScanMode
SCAN_MODE = {
    1: "Panel",
    2: "Line",
    4: "Photo",
    8: "Mixed",
}

# TheCaptProfile.ScanRotate
SCAN_ROTATE = {
    0: "None",
    1: "90° (rotate right)",
    2: "180°",
    3: "270° (rotate left)",
}

# TheCaptProfile.ScanSize (flags)
SCAN_SIZE = {
    1: "A0",
    2: "A1",
    4: "A2",
    8: "A3",
    16: "A4",
    32: "A5",
    64: "B",
    128: "Letter",
    256: "B0",
    512: "B1",
    1024: "B2",
    2048: "B3",
    4096: "B4",
    8192: "B5",
    16384: "B6",
    32768: "Legal",
    65536: "Panel",
    131072: "Coupon",
    262144: "Personal",
    524288: "Business",
    4194304: "Maximum",
    33554432: "Minimum",
    67108864: "Auto-Detect",
    134217728: "Custom",
}

# TheCaptProfile.ScanSource
SCAN_SOURCE = {
    1: "Flatbed",
    2: "ADF",
    4: "Panel",
    8: "Manual",
}

# TheCaptProfile.StorageCompression
STORAGE_COMPRESSION = {
    1: "JPEG 2000",
    2: "JPEG",
    3: "Packbits",
    4: "LZW",
    5: "ZIP",
}

# TheCaptProfile.StorageMode
STORAGE_MODE = {
    0: "Original",
    1: "Single TIFF",
    2: "Single PDF",
    3: "Multipage TIFF",
    4: "Multipage PDF",
    5: "Searchable PDF",
    6: "Searchable PDF/A",
    7: "Multipage PDF Jpeg2000",
    8: "Multipage PDF/A",
}

# TheCaptStep.TypeNo
CAPTURE_STEP_TYPES = {
    1: "Scan",
    2: "Barcode",
    3: "OCR",
    4: "Define Category",
    5: "Automatically set index data",
    6: "Set index data via dll",
    7: "Call verification dll",
    8: "Archive",
    9: "Call trigger dll (after archive)",
    10: "Image enhancement",
    11: "Nuance OCR",
}

# TheCaptVerify.VerifyMode
VERIFY_MODE = {
    1: "Ascending",
    2: "Descending",
    3: "Constant",
}

# TheCategory.AutoApndMode
AUTO_APPEND_MODE = {
    0: "Default",
    1: "Insert at beginning",
    2: "Append to end",
    3: "Replace",
    4: "Disabled",
}

# TheCategory.CheckInMode
CHECKIN_MODE = {
    0: "Check-In comment not allowed",
    1: "Check-In comment optional",
    2: "Check-In comment mandatory",
}

# TheCategory.CoverMode
COVER_MODE = {
    0: "Never show cover sheet",
    1: "Cover sheet for empty documents",
    2: "Always show cover sheet",
}

# TheCategory.EmptyDocMode
EMPTY_DOC_MODE = {
    0: "No empty documents allowed",
    1: "Documents can be empty",
    2: "All documents must be empty",
}

# TheCategory.FulltextMode
FULLTEXT_MODE = {
    0: "Full-text indexing disabled",
    1: "Full-text indexing enabled",
    2: "Full-text indexing for newer documents",
}

# TheCategory.WMMode
WATERMARK_MODE = {
    0: "Normal mode",
    1: "Secure mode",
}

# TheCatSpool.Status
SPOOL_STATUS = {
    0: "Original input file archived",
    1: "Preprocessed",
    2: "Processing completed",
    4: "Faulty",
}

# TheCloudStorage.CloudProvider
CLOUD_PROVIDER = {
    1: "Dropbox",
    2: "Google Drive",
    3: "OneDrive",
    4: "Box",
}

# TheCntConnError.Status
CONTENT_CONNECTOR_ERROR_STATUS = {
    -1: "Unknown",
    0: "Normal error status",
    1: "Queued for retry",
    2: "Retry failed - file exists",
    3: "Retry failed - other reasons",
    4: "Too many OCR threads",
}

# TheCntConnSource.SourceMode
CONTENT_CONNECTOR_SOURCE_MODE = {
    1: "Folder",
    2: "Mailbox",
    3: "Signature Provider",
}

# TheCommonScript.ScriptLang
SCRIPT_LANGUAGE = {
    1: "VBScript",
    2: "JScript",
}

# TheCounter.CounterType
COUNTER_TYPE = {
    1: "Integer",
    2: "Text (formatted)",
}

# TheCtgryFields.CounterMode
COUNTER_MODE = {
    1: "Client-side counter",
    2: "Server-side counter",
}

# TheCtgryFields.DependencyMode
DEPENDENCY_MODE = {
    0: "Referenced",
    1: "Synchronized redundant",
    2: "Editable redundant",
}

# TheCtgryFields.IndexType
INDEX_TYPE = {
    0: "None",
    1: "Normal index",
    2: "Unique index",
}

# TheCtgryFields.TypeNo - Field Types
FIELD_TYPES = {
    1: "String",
    2: "Integer",
    3: "Date",
    4: "Label",
    5: "Decimal",
    6: "Logical",
    7: "Datetime",
    8: "Counter (integer)",
    9: "Counter (formatted)",
    10: "Table field",
    11: "Integer (64-bit)",
    12: "Image",
    13: "Tab",
}

# TheDataExtractor.ModeNo
DATA_EXTRACTOR_MODE = {
    1: "Text, line-based",
    2: "Text, page-based",
    3: "PDF",
    4: "XML",
    5: "OCR",
    6: "Existing Doc",
}

# TheDataExtractorItem.DocBreakMode
DATA_EXTRACTOR_DOC_BREAK_MODE = {
    0: "None",
    1: "On change",
    2: "On value",
}

# TheDataExtractorItem.TypeNo
DATA_EXTRACTOR_ITEM_TYPE = {
    1: "Text, line-based",
    2: "Text, page-based",
    3: "PDF zone",
    4: "XML tag",
    5: "OCR",
    6: "PDF attachment",
    7: "PDF signature",
}

# TheDataType.TypeGroup
DATA_TYPE_GROUP = {
    1: "Standard",
    2: "Keyword",
    3: "User defined (integer)",
    4: "User defined (ansi-text)",
    5: "User defined (date)",
    6: "User defined (float)",
    7: "User defined (unicode-text)",
    8: "Case definition",
}

# TheDemigrate.Action (flags)
DEMIGRATE_ACTION = {
    1: "Primary migration scheduled",
    2: "Backup migration scheduled",
    4: "Copy to buffer",
    8: "Delete from primary media",
    16: "Delete from backup media",
    32: "Delete from primary after migration",
    64: "Delete from backup after migration",
    128: "Set MediaNo to 0",
    256: "Set BackMediaNo to 0",
    512: "Set ServerNo to demigrate server",
}

# TheDevice.Type
DEVICE_TYPE = {
    1: "Jukebox (deprecated)",
    2: "RAID (local folder)",
    3: "Optical drive (deprecated)",
    4: "Network Share",
}

# TheDocument.Security
DOCUMENT_SECURITY = {
    0: "Standard security",
    1: "Document ACL only",
    2: "Document ACL with inheritance",
}

# TheEFormSubmission.SubmissionType
EFORM_SUBMISSION_TYPE = {
    1: "Default",
    2: "User",
    3: "Draft",
}

# TheForm.FormType
FORM_TYPE = {
    0: "TIFF",
    3: "Greenbar",
    4: "XML",
}

# TheForm.PageOrder
FORM_PAGE_ORDER = {
    0: "Cyclic",
    1: "Special first and last page",
    2: "Special first page",
    3: "Special last page",
}

# TheFulltextQueue.Action
FULLTEXT_QUEUE_ACTION = {
    1: "Rebuild catalog",
    2: "Remove from catalog",
    3: "Add to catalog",
    4: "Update document",
    5: "Compress catalog",
}

# TheIndexingAssignment.ErrorMode
INDEXING_ERROR_MODE = {
    1: "Abort",
    2: "Ignore",
    3: "Use fall back",
    4: "Report error",
}

# TheIndexingProfile.AutoAppendMode
INDEXING_AUTO_APPEND_MODE = {
    0: "Category default",
    1: "Insert",
    2: "Append",
    3: "Replace",
    4: "No check",
    5: "Error",
    6: "Skip document",
}

# TheIndexingProfile.ModeNo
INDEXING_PROFILE_MODE = {
    1: "File",
    2: "Mail",
    3: "Word",
    4: "Excel",
    5: "Capture Client",
    6: "Office",
    7: "Workflow - update index data",
    8: "Workflow - change category",
    9: "New form",
    10: "Signature",
    11: "Workflow - Update case header",
}

# TheMedia.DirStruct
MEDIA_DIR_STRUCT = {
    1: "Classic",
    2: "Base36CF",
    3: "Buffer",
    6: "UDO",
}

# TheMedia.Status
MEDIA_STATUS = {
    0: "Raw",
    1: "Formatted",
    2: "Assigned",
    4: "Full",
    8: "Damaged",
}

# TheMediaPool.FileSystem
MEDIA_FILE_SYSTEM = {
    1: "FAT",
    2: "NTFS",
    3: "NTFS compressed",
}

# TheMFPDevice.Color
MFP_COLOR = {
    0: "Undefined",
    1: "Black & white",
    2: "Gray",
    4: "Color",
}

# TheMFPDevice.ImageType
MFP_IMAGE_TYPE = {
    0: "Undefined",
    1: "Text",
    2: "Text/image",
    4: "Image",
    8: "Photo",
    16: "Text/photo",
    32: "Text/map/photo",
    64: "Map",
    128: "Second copy",
}

# TheMFPDevice.ScanOrientation
MFP_SCAN_ORIENTATION = {
    0: "Undefined",
    1: "Automatic",
    2: "Long-edge feed",
    4: "Short-edge feed",
}

# TheMFPDevice.ScanSize (flags)
MFP_SCAN_SIZE = {
    0: "Undefined",
    1: "Any",
    2: "A3",
    4: "A4",
    8: "A5",
    16: "A6",
    32: "SRA3",
    64: "B4",
    128: "B5",
    256: "Letter",
    512: "Legal",
    1024: "Statement",
    2048: "K8",
    4096: "K16",
    8192: "Hagaki",
    16384: "12x18 inch",
    32768: "Ledger",
}

# TheMigrate.Action (flags)
MIGRATE_ACTION = {
    1: "Primary migration",
    2: "Backup migration",
    4: "Pre-fetch document",
    8: "Delete from buffer after primary migration",
    16: "Delete from buffer after both migrations",
}

# TheOfficeAction.ActionType
OFFICE_ACTION_TYPE = {
    0: "Undefined",
    1: "Base",
    2: "New document",
    3: "Save",
    4: "Send",
    5: "Print",
    6: "Script",
}

# TheOfficeAssignment.AssignmentType
OFFICE_ASSIGNMENT_TYPE = {
    0: "Undefined",
    1: "Content control",
    2: "Form field",
    3: "Cell",
    4: "Mail basic",
    5: "Mail advanced",
    10: "Document property",
}

# TheOfficeProfile.ProfileType
OFFICE_PROFILE_TYPE = {
    0: "Undefined",
    1: "Word",
    2: "Excel",
    3: "Template only",
    4: "Mail",
}

# ThePowerBITable.FrequencyType
POWERBI_FREQUENCY_TYPE = {
    1: "Hourly",
    2: "Daily",
}

# ThePowerBITable.TableType
POWERBI_TABLE_TYPE = {
    1: "Category",
    2: "Workflow",
}

# TheQuery.VersionNo
QUERY_VERSION = {
    0: "Therefore 2017 or earlier",
    1: "Therefore 2018 or later",
}

# TheQueryField.Alignment
QUERY_FIELD_ALIGNMENT = {
    0: "Default",
    1: "Left",
    2: "Center",
    3: "Right",
}

# TheReplColumn.ColType
REPLICATION_COLUMN_TYPE = {
    1: "Int",
    2: "Date",
    3: "Text",
    4: "Float",
    5: "Short",
    6: "Bool",
    7: "Datetime",
    8: "ANSI text",
    9: "NText",
    10: "Int64",
    11: "GUID",
}

# TheReplConn.DBBrand
REPLICATION_DB_BRAND = {
    1: "SQL Server",
    2: "Oracle",
    6: "SQL Server via ODBC",
}

# TheReporting.EventType
REPORTING_EVENT_TYPE = {
    1: "WF process start",
    2: "WF task start",
    3: "WF instance claimed",
    4: "WF instance unclaimed",
    5: "WF instance delegated",
    6: "WF instance rerouted",
    7: "WF task finished",
    8: "WF process finished",
    9: "WF instance deleted",
}

# TheRetentionQueue.Action
RETENTION_QUEUE_ACTION = {
    1: "Delete single version",
    2: "Delete all versions",
    4: "Ignore media",
}

# TheRole.Permission (flags)
ROLE_PERMISSION = {
    0x01: "Operator",
    0x02: "Administrator",
    0x04: "Set Permissions",
    0x08: "Access/Read",
    0x20: "System Write",
    0x40: "Category/Case: add documents",
    0x80: "Manage searches",
    0x100: "Execute searches",
    0x200: "Manage keyword dictionary",
    0x400: "Document/Case: create tasks",
    0x1000: "Document/Case: view in hit list",
    0x2000: "Document/Case: open and view",
    0x4000: "Document/Case: print",
    0x8000: "Document/Case: export and send",
    0x40000: "Document/Case: view history",
    0x80000: "Document: add annotations",
    0x100000: "Document: delete annotations",
    0x200000: "Document: edit document",
    0x400000: "Document: update index data",
    0x800000: "Document: add file",
    0x1000000: "Document: delete file",
    0x2000000: "Document: delete document",
    0x4000000: "Document: retention protection",
    0x8000000: "Document/Case: manage links",
    0x10000000: "Case: create",
    0x20000000: "Case: delete",
    0x40000000: "Case: close",
    0x80000000: "Read permission",
    0x100000000: "Case: reopen",
    0x200000000: "Workflow: participate",
    0x400000000: "Workflow: add a document",
    0x800000000: "Workflow: view history",
    0x1000000000: "Workflow: delegate",
    0x2000000000: "Workflow: view all",
    0x4000000000: "Workflow: delete",
    0x8000000000: "Workflow: start manually",
    0x10000000000: "Case: update index data",
}

# TheRoleAssignments.SubObjNo for pre-defined folders
PREDEFINED_FOLDERS = {
    1000: "Therefore System",
    1001: "Content Connector",
    1002: "Exchange Connector",
    1004: "SAP Connector",
    1005: "User Management",
    1006: "Portal",
}

# TheSigningStatus.Status
SIGNING_STATUS = {
    0: "Uploaded",
    1: "Completed, ready for download",
    2: "Declined, ready for download",
    3: "Processed",
    4: "Declined",
    5: "Error, completed",
    6: "Error, declined",
    7: "Error, unknown",
}

# TheSPProfile.Conversion
SHAREPOINT_CONVERSION = {
    0: "Original",
    1: "Single-page TIFF",
    2: "Single-page PDF",
    3: "Multi-page TIFF",
    4: "Multi-page PDF",
    5: "Searchable PDF",
    6: "Searchable PDF/A",
    50: "JPEG",
}

# TheSPProfile.Direction
SHAREPOINT_DIRECTION = {
    1: "From SharePoint to Therefore",
    2: "From Therefore to SharePoint",
}

# TheSPProfile.OPMode
SHAREPOINT_OP_MODE = {
    1: "Copy",
    2: "Move",
}

# TheStamp.StampType
STAMP_TYPE = {
    0: "PDF",
    1: "PNG",
}

# TheStatistics.TypeNo
STATISTICS_TYPE = {
    1: "Retrieve",
    2: "Connect",
    4: "Archive",
    8: "COLD processing",
}

# TheStorageFiles.Type
STORAGE_FILE_TYPE = {
    0: "Unknown",
    1: "Thex files (.thex)",
    2: "Content files (.thec)",
    3: "Compressed content file (.zip)",
    4: "ADOS file (.ados)",
}

# TheString.StringType
STRING_TYPE = {
    1: "Category name",
    2: "Category description",
    3: "Category header",
    4: "Category footer",
    5: "Field caption",
    6: "Tab caption",
    7: "Regular expression: help text",
    8: "Workflow process name",
    9: "Workflow process description",
    10: "Workflow task name",
    11: "Workflow transition name",
    12: "Workflow transition: description",
    13: "Workflow transition: condition error text",
    14: "Workflow task: checklist text",
    15: "Keyword dictionary",
    16: "Keyword",
    17: "Folder name",
    18: "Case definition name",
    19: "Query template name",
    20: "Label field caption",
}

# TheTask.TaskMode
TASK_MODE = {
    1: "Complete",
    2: "Complete / decline",
    3: "Approve / reject",
    4: "Yes / No",
}

# TheTaskUser.TaskState
TASK_STATE = {
    1: "Not started",
    2: "In progress",
    3: "Waiting on someone else",
    4: "Deferred",
    5: "Completed",
    6: "Revoked",
}

# TheTreeViewLevel.LevelFunction
TREEVIEW_LEVEL_FUNCTION = {
    0: "No function",
    1: "Month",
    2: "Year",
    3: "Month/Year",
    4: "First character",
    5: "First character grouped",
    6: "Range",
}

# TheTreeViewLevel.SortOrder
TREEVIEW_SORT_ORDER = {
    1: "Ascending",
    2: "Descending",
}

# TheUCAction.ActionFlags (flags)
UC_ACTION_FLAGS = {
    1: "Show index data",
    2: "View document",
    4: "Capture: auto-save",
    8: "Select profile",
    16: "Open on single hit",
}

# TheUCAction.ActionType
UC_ACTION_TYPE = {
    1: "Search",
    2: "Save",
    3: "Scan with Capture client",
    4: "Full-text search",
    5: "Scan with Viewer",
    6: "Cross-category search",
    7: "Search case",
    8: "Run executable",
}

# TheUCControl.CompProps (flags)
UC_CONTROL_PROPS = {
    1: "ID",
    2: "Class",
    4: "Top",
    8: "Left",
    16: "Width",
    32: "Height",
    64: "Position",
    128: "Caption",
}

# TheUCProfile.ClassCompMode
UC_COMP_MODE = {
    1: "Exact",
    2: "Starts with",
    3: "Ends with",
    4: "Contains",
}

# TheUsageStats.StatType
USAGE_STATS_TYPE = {
    1: "Condition in category search",
    2: "Condition in case search",
    3: "Index field when saving into a category",
    4: "Index field when creating a new case",
}

# TheUser.UserType
USER_TYPE = {
    1: "User",
    2: "Group",
    3: "System",
    4: "Portal user",
}

# TheUserSync.SyncState
USER_SYNC_STATE = {
    0: "Synced",
    1: "Dirty",
    2: "Deleted",
    3: "Error after sync dirty",
    4: "Error after sync deleted",
}

# TheWFHistory.Type
WORKFLOW_HISTORY_TYPE = {
    1: "Started",
    2: "Finished",
    3: "Saved",
    4: "Routed",
    5: "Claimed",
    6: "Unclaimed",
    7: "Reclaimed",
    8: "Delegated",
    9: "Document linked to Instance",
    10: "Document link removed from Instance",
    11: "Overdue Mail sent for Instance",
    12: "Overdue transition applied",
    13: "Rerouted",
    14: "Split",
    15: "Merged",
    16: "Exception merge",
    17: "User split",
    18: "Error",
    99: "User defined Entry",
}

# TheWFInstAccess.EntryType
WORKFLOW_INST_ACCESS_TYPE = {
    1: "Instance claimed by user",
    2: "Instance originally assigned to user",
}

# TheWFTasks.Type
WORKFLOW_TASK_TYPE = {
    1: "Start",
    2: "End",
    3: "Manual Task",
    4: "Automatic Task",
}

# TheWFTasks.UserChoice
WORKFLOW_USER_CHOICE = {
    0: "Route to all specified users/groups",
    1: "User chooses one user/group",
}


def get_lookup_name(lookup_table: dict, value: int, default: str = "Unknown") -> str:
    """Get the name for a value from a lookup table."""
    return lookup_table.get(value, f"{default} ({value})")


def decode_flags(flag_table: dict, value: int) -> list:
    """Decode a bitmask value into a list of flag names."""
    flags = []
    for flag_value, flag_name in sorted(flag_table.items()):
        if value & flag_value:
            flags.append(flag_name)
    return flags
