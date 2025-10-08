"""
小红书页面元素定位器定义
"""

class Locators:
    """页面元素定位器"""
    
    # 笔记列表相关 - 基于实际HTML结构更新
    NOTE_ITEM_SELECTORS = [
        ".note",                     # 实际的笔记元素class
        ".note-item",
        ".note-card", 
        "[data-note-id]",
        "[note-info]",               # 笔记信息属性
        ".content-item",
        ".feed-item"
    ]
    
    NOTE_ID_ATTR = "data-note-id"
    NOTE_TITLE_SELECTORS = [
        ".title",
        ".note-title",
        ".content-title",
        "h3",
        "h4",
        ".text-title"
    ]
    
    NOTE_DATE_SELECTORS = [
        ".date",
        ".time",
        ".publish-time",
        ".create-time",
        "[data-time]"
    ]
    
    # 权限设置相关
    PERMISSION_BUTTON_SELECTORS = [
        ".control.data-perm",
        ".permission-btn",
        ".settings-btn",
        ".more-btn",
        ".dropdown-btn",
        "[data-action='permission']",
        ".ellipsis",
        ".control-btn",
        ".menu-btn",
        ".options-btn",
        ".control-item",
        ".note-control",
        ".action-btn",
        ".perm-control",
        "[class*='permission']",
        "[class*='control']",
        ".icon-btn",
        ".more-options"
    ]
    
    DELETE_BUTTON_SELECTORS = [
        ".control.data-del",
        ".delete-btn",
        ".remove-btn",
        ".trash-btn",
        "[data-action='delete']",
        ".control-delete",
        ".delete-control",
        ".remove-control"
    ]
    
    DELETE_CONFIRM_BUTTON = "//button[contains(text(), '删除')]"
    DELETE_CONFIRM_ALTERNATIVES = [
        "//button[contains(text(), '确认删除')]",
        "//button[contains(text(), '确定删除')]",
        "//button[contains(text(), '确认')]",
        "//button[contains(text(), '确定')]",
        "//button[contains(@class, 'delete')]",
        "//button[contains(@class, 'confirm')]"
    ]
    
    PERMISSION_OPTION_PRIVATE = "//div[contains(@class, 'custom-option')]//div[contains(text(), '仅自己可见')]"
    PERMISSION_OPTION_PUBLIC = "//div[contains(@class, 'custom-option')]//div[contains(text(), '公开可见')]"
    PERMISSION_CONFIRM_BUTTON = "//button[contains(@class, 'confirm')]"
    
    # 可见性选项的更精确选择器
    VISIBILITY_OPTIONS = [
        "//div[contains(@class, 'custom-option') and .//div[contains(text(), '公开可见')]]",
        "//div[contains(@class, 'custom-option') and .//div[contains(text(), '仅自己可见')]]",
        "//div[contains(@class, 'custom-option') and .//div[contains(text(), '仅互关好友可见')]]",
        "//div[contains(@class, 'custom-option') and .//div[contains(text(), '部分人可见')]]",
        "//div[contains(@class, 'custom-option') and .//div[contains(text(), '部分人不可见')]]"
    ]
    
    # 分页相关
    LOAD_MORE_BUTTON_SELECTORS = [
        ".load-more",
        ".more-btn",
        "[data-action='load-more']",
        ".next-page"
    ]
    
    NO_MORE_NOTES_SELECTORS = [
        ".no-more",
        ".no-data",
        ".end-list",
        "[data-status='no-more']"
    ]
    
    # 登录相关
    LOGIN_BUTTON = ".login-btn"
    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    
    # 通用元素
    LOADING_SPINNER = ".loading"
    TOAST_MESSAGE = ".toast"
    
    # 页面布局相关
    CONTENT_AREA_SELECTORS = [
        ".note-management",
        ".content-area",
        ".main-content",
        ".note-list-container",
        ".notes-container",
        ".scrollable-content",
        ".note-container",
        "[data-role='content']",
        ".el-main",
        ".main-panel",
        ".content-wrapper"
    ]
    
    # 滚动相关 - 基于实际HTML结构更新
    SCROLL_CONTAINER_SELECTORS = [
        ".panel",                    # 主要的笔记管理面板
        ".notes-container",          # 笔记容器
        ".content",                  # 内容区域
        ".note-management",          # 笔记管理
        ".content-area", 
        ".main-content",
        ".note-list-container",
        ".scrollable-content",
        ".el-scrollbar__wrap",
        ".scrollbar-wrap",
        "[class*='scroll']",
        "[class*='container']"
    ]
