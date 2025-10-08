"""
数据提取模块
从小红书创作者平台提取笔记数据
"""

import time
import platform
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from locators import Locators


class XiaohongshuScraper:
    """小红书数据提取器"""
    
    def __init__(self, headless: bool = False):
        """
        初始化爬虫
        
        Args:
            headless: 是否使用无头模式
        """
        self.driver = None
        self.wait = None
        self.headless = headless
        self.base_url = "https://creator.xiaohongshu.com/new/note-manager"
    
    def setup_driver(self) -> None:
        """设置WebDriver，支持复用现有Chrome会话"""
        # 首先尝试连接到现有的Chrome会话
        if self._try_connect_existing_chrome():
            return
        
        # 如果没有找到现有会话，启动新的Chrome
        print("未找到现有Chrome会话，启动新的Chrome浏览器...")
        self._launch_new_chrome()
    
    def _try_connect_existing_chrome(self) -> bool:
        """
        尝试连接到现有的Chrome会话
        
        Returns:
            是否成功连接到现有会话
        """
        try:
            # 检查是否有Chrome进程在使用相同的用户数据目录
            import os
            user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
            
            # 检查用户数据目录是否存在
            if not os.path.exists(user_data_dir):
                return False
            
            # 检查是否有SingletonLock文件（Chrome正在运行的标志）
            lock_file = os.path.join(user_data_dir, "SingletonLock")
            if not os.path.exists(lock_file):
                return False
            
            print("检测到现有Chrome会话，尝试连接...")
            
            # 尝试连接到现有的Chrome实例
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.wait = WebDriverWait(self.driver, 10)
                print("✓ 成功连接到现有Chrome会话")
                
                # 测试连接是否有效
                try:
                    self.driver.current_url
                    print("✓ Chrome会话连接正常")
                    return True
                except Exception:
                    print("现有Chrome会话无法正常响应，将启动新会话")
                    self.driver = None
                    return False
                    
            except Exception as e:
                print(f"连接现有Chrome会话失败: {e}")
                return False
                
        except Exception as e:
            print(f"检测现有Chrome会话时出错: {e}")
            return False
    
    def _launch_new_chrome(self) -> None:
        """启动新的Chrome浏览器"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")  # 启用远程调试端口
        
        # 添加cookie持久化功能
        import os
        user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # 根据操作系统设置合适的User-Agent
        system = platform.system()
        if system == "Windows":
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        elif system == "Darwin":  # macOS
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        else:  # Linux
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            # 直接使用系统ChromeDriver
            print("使用系统ChromeDriver启动新会话...")
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✓ ChromeDriver启动成功")
            
        except Exception as e:
            print(f"系统ChromeDriver启动失败: {e}")
            print("请确保已安装Chrome浏览器并且ChromeDriver在系统PATH中")
            print("下载地址: https://chromedriver.chromium.org/")
            raise e
        
        self.wait = WebDriverWait(self.driver, 10)
    
    def login_if_needed(self) -> bool:
        """
        检查是否需要登录
        
        Returns:
            是否已登录
        """
        try:
            # 访问页面
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # 检查是否跳转到登录页面
            current_url = self.driver.current_url
            if "login" in current_url.lower() or "auth" in current_url.lower():
                print("检测到需要登录，请在浏览器中手动完成登录...")
                print("登录完成后，按回车键继续...")
                input("按回车键继续...")
                
                # 重新检查登录状态
                self.driver.get(self.base_url)
                time.sleep(3)
                current_url = self.driver.current_url
                if "login" in current_url.lower() or "auth" in current_url.lower():
                    print("登录验证失败，请重新尝试")
                    return False
                else:
                    print("✓ 登录成功")
            
            # 无论是否刚登录，都给用户时间确认页面加载完成
            print("程序将自动滚动加载所有笔记，请稍候...")
            print("如果页面没有正确加载，请按Ctrl+C终止程序")
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"登录检查失败: {e}")
            return False
    
    def extract_notes(self) -> List[Dict]:
        """
        提取所有笔记数据
        
        Returns:
            笔记列表
        """
        notes = []
        
        if not self.login_if_needed():
            print("登录失败，无法提取笔记")
            return notes
        
        try:
            print("开始提取笔记数据...")
            
            # 尝试找到笔记元素
            note_elements = self._find_note_elements()
            if not note_elements:
                print("未找到笔记元素，尝试调试页面结构...")
                self._debug_page_structure()
                return notes
            
            print(f"找到 {len(note_elements)} 个笔记元素")
            
            for i, element in enumerate(note_elements):
                try:
                    note_data = self._extract_note_data(element, i)
                    if note_data:
                        notes.append(note_data)
                        print(f"成功提取笔记 {i+1}: {note_data['title'][:30]}...")
                except Exception as e:
                    print(f"提取笔记数据失败: {e}")
                    continue
            
            print(f"成功提取 {len(notes)} 条笔记")
            
        except Exception as e:
            print(f"提取笔记时发生错误: {e}")
        
        return notes
    
    def _find_note_elements(self) -> List:
        """尝试多种选择器找到笔记元素"""
        for selector in Locators.NOTE_ITEM_SELECTORS:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                    return elements
            except Exception as e:
                continue
        
        # 如果CSS选择器都失败，尝试XPath
        xpath_selectors = [
            "//div[contains(@class, 'note')]",
            "//div[contains(@class, 'item')]",
            "//li[contains(@class, 'note')]",
            "//article",
            "//div[contains(@data-note-id, '')]"
        ]
        
        for xpath in xpath_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements:
                    print(f"使用XPath '{xpath}' 找到 {len(elements)} 个元素")
                    return elements
            except Exception as e:
                continue
        
        return []
    
    def _extract_note_data(self, element, index: int) -> Optional[Dict]:
        """
        提取单个笔记的数据
        
        Args:
            element: 笔记元素
            index: 元素索引
            
        Returns:
            笔记数据字典
        """
        try:
            # 使用索引作为ID，这样可以在后续操作中通过索引找到元素
            note_id = f"note_index_{index}"
            
            # 提取标题
            title = "无标题"
            for selector in Locators.NOTE_TITLE_SELECTORS:
                try:
                    title_element = element.find_element(By.CSS_SELECTOR, selector)
                    title = title_element.text.strip()
                    if title:
                        break
                except NoSuchElementException:
                    continue
            
            # 如果没找到标题，尝试获取元素的文本内容作为标题
            if title == "无标题":
                text = element.text.strip()
                if text:
                    title = text[:50] + "..." if len(text) > 50 else text
            
            # 提取日期
            date = ""
            for selector in Locators.NOTE_DATE_SELECTORS:
                try:
                    date_element = element.find_element(By.CSS_SELECTOR, selector)
                    date = date_element.text.strip()
                    if date:
                        break
                except NoSuchElementException:
                    continue
            
            # 检查权限设置按钮是否存在
            has_permission_button = False
            for selector in Locators.PERMISSION_BUTTON_SELECTORS:
                try:
                    permission_btn = element.find_element(By.CSS_SELECTOR, selector)
                    if permission_btn.is_displayed() and permission_btn.is_enabled():
                        has_permission_button = True
                        break
                except NoSuchElementException:
                    continue
            
            return {
                'note_id': note_id,
                'title': title,
                'date': date,
                'has_permission_button': has_permission_button,
                'element_index': index,  # 保存元素索引
                'element': element  # 保存元素引用，后续操作时使用
            }
            
        except Exception as e:
            print(f"提取笔记数据时发生错误: {e}")
            return None
    
    def _debug_page_structure(self) -> None:
        """调试页面结构，输出有用的信息"""
        try:
            print("=== 页面调试信息 ===")
            print(f"当前URL: {self.driver.current_url}")
            print(f"页面标题: {self.driver.title}")
            
            # 获取页面源码长度
            page_source_length = len(self.driver.page_source)
            print(f"页面源码长度: {page_source_length}")
            
            # 查找所有可能的容器元素
            possible_containers = [
                ".container", ".main", ".content", ".list", ".grid",
                ".notes", ".feed", ".items", ".cards"
            ]
            
            for container in possible_containers:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, container)
                    if elements:
                        print(f"找到容器 '{container}': {len(elements)} 个")
                except:
                    continue
            
            # 输出前10个div元素的class属性
            divs = self.driver.find_elements(By.TAG_NAME, "div")[:10]
            print("前10个div元素的class:")
            for i, div in enumerate(divs):
                class_attr = div.get_attribute('class') or '无class'
                print(f"  {i+1}. {class_attr}")
            
            print("===================")
            
        except Exception as e:
            print(f"调试页面结构时发生错误: {e}")
    
    def close(self) -> None:
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        """上下文管理器入口"""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def _find_scroll_container(self) -> Optional:
        """
        查找可滚动的容器元素
        
        Returns:
            滚动容器元素或None
        """
        try:
            # 根据HTML结构，优先查找.panel容器
            print("查找滚动容器...")
            
            # 首先尝试找到主要的panel容器
            panel_selectors = [
                ".panel",                    # 主要的笔记管理面板
                ".content",                 # 内容区域
                ".notes-container",         # 笔记容器
                ".note-management",         # 笔记管理
                ".content-area",            # 内容区域
                ".main-content"
            ]
            
            for selector in panel_selectors:
                try:
                    container = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # 检查容器是否真的可滚动
                    scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", container)
                    client_height = self.driver.execute_script("return arguments[0].clientHeight", container)
                    
                    print(f"检查容器 {selector}: 滚动高度={scroll_height}, 客户端高度={client_height}")
                    
                    if scroll_height > client_height + 100:  # 留100px缓冲
                        print(f"✓ 找到可滚动容器: {selector}")
                        return container
                        
                except NoSuchElementException:
                    continue
                except Exception as e:
                    print(f"检查容器 {selector} 时出错: {e}")
                    continue
            
            # 如果没找到特定的滚动容器，尝试查找body
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                scroll_height = self.driver.execute_script("return document.body.scrollHeight")
                client_height = self.driver.execute_script("return window.innerHeight")
                
                if scroll_height > client_height:
                    print("使用body作为滚动容器")
                    return body
            except:
                pass
            
            print("未找到可滚动的容器")
            return None
            
        except Exception as e:
            print(f"查找滚动容器时发生错误: {e}")
            return None
    
    def _scroll_container(self, container, scroll_step: int = 2000) -> bool:
        """
        在指定容器内滚动
        
        Args:
            container: 滚动容器元素
            scroll_step: 每次滚动的像素数
            
        Returns:
            是否成功滚动
        """
        try:
            # 获取当前滚动位置和总高度
            current_scroll = self.driver.execute_script("return arguments[0].scrollTop", container)
            max_scroll = self.driver.execute_script("return arguments[0].scrollHeight - arguments[0].clientHeight", container)
            
            # 如果已经到底部，返回False
            if current_scroll >= max_scroll - 50:  # 留50px的缓冲
                print(f"已滚动到底部: {current_scroll} >= {max_scroll - 50}")
                return False
            
            # 计算新的滚动位置，确保实际滚动距离
            new_scroll = min(current_scroll + scroll_step, max_scroll)
            
            # 执行滚动
            self.driver.execute_script("arguments[0].scrollTop = arguments[1]", container, new_scroll)
            
            # 等待一小段时间让滚动生效
            time.sleep(0.3)
            
            # 验证滚动是否真的生效了
            actual_scroll = self.driver.execute_script("return arguments[0].scrollTop", container)
            actual_distance = actual_scroll - current_scroll
            
            # 如果实际滚动距离太小，尝试直接滚动到更远的位置
            if actual_distance < scroll_step * 0.5:  # 如果实际滚动距离小于期望的50%
                print(f"滚动距离不足，尝试大步长滚动: 实际{actual_distance}px, 期望{scroll_step}px")
                # 尝试滚动到更远的位置
                target_scroll = min(current_scroll + scroll_step * 2, max_scroll)
                self.driver.execute_script("arguments[0].scrollTop = arguments[1]", container, target_scroll)
                time.sleep(0.5)
                
                # 再次验证
                final_scroll = self.driver.execute_script("return arguments[0].scrollTop", container)
                final_distance = final_scroll - current_scroll
                print(f"大步长滚动结果: {current_scroll} -> {final_scroll} (距离: {final_distance}px)")
            else:
                print(f"快速滚动: {current_scroll} -> {new_scroll} (距离: {actual_distance}px, 最大: {max_scroll})")
            
            # 额外等待时间让虚拟滚动加载内容
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"容器滚动时发生错误: {e}")
            return False
    
    def _auto_scroll_content_area(self) -> None:
        """
        自动滚动内容区域以加载所有笔记，无滚动次数限制
        """
        try:
            print("开始无限制自动滚动内容区域...")
            
            # 查找滚动容器
            scroll_container = self._find_scroll_container()
            if not scroll_container:
                print("未找到可滚动的容器，跳过滚动")
                return
            
            scroll_count = 0
            no_new_content_count = 0
            last_note_count = 0
            stable_count = 0
            max_stable_count = 8  # 增加到8次，确保加载完所有内容
            
            # 先进行几次快速滚动，跳过初始加载
            print("执行初始快速滚动...")
            for i in range(3):
                if self._scroll_container(scroll_container, scroll_step=5000):  # 增加到5000px
                    time.sleep(0.3)  # 进一步减少等待时间
                    scroll_count += 1
                else:
                    break
            
            while True:  # 无限制滚动，直到真正没有新内容
                # 记录滚动前的笔记数量
                current_notes = self._find_note_elements()
                current_note_count = len(current_notes)
                
                # 滚动容器
                if not self._scroll_container(scroll_container):
                    print("已滚动到底部")
                    break
                
                scroll_count += 1
                
                # 检查是否有新内容加载
                if current_note_count == last_note_count:
                    no_new_content_count += 1
                    stable_count += 1
                    
                    # 如果连续多次没有新内容，使用更激进的策略
                    if stable_count >= 2:
                        print("连续无新内容，尝试大步长滚动...")
                        # 尝试一次大步长滚动
                        if self._scroll_container(scroll_container, scroll_step=4000):
                            time.sleep(1)  # 稍长等待
                            # 再次检查是否有新内容
                            check_notes = self._find_note_elements()
                            if len(check_notes) > current_note_count:
                                print(f"大步长滚动后发现新内容: {current_note_count} -> {len(check_notes)}")
                                stable_count = 0
                                no_new_content_count = 0
                                last_note_count = len(check_notes)
                                continue
                    
                    if no_new_content_count >= max_stable_count:  # 连续8次没有新内容
                        print(f"连续{max_stable_count}次滚动没有新内容，进行最后冲刺...")
                        # 进行最后几次大步长滚动尝试
                        for last_attempt in range(3):
                            print(f"最后冲刺第{last_attempt + 1}次...")
                            if self._scroll_container(scroll_container, scroll_step=6000):
                                time.sleep(1.5)  # 更长等待时间
                                final_check = self._find_note_elements()
                                if len(final_check) > current_note_count:
                                    print(f"最后冲刺成功！发现新内容: {current_note_count} -> {len(final_check)}")
                                    current_note_count = len(final_check)
                                    no_new_content_count = 0
                                    stable_count = 0
                                    last_note_count = current_note_count
                                    break
                                else:
                                    print(f"最后冲刺第{last_attempt + 1}次无新内容")
                            else:
                                print(f"最后冲刺第{last_attempt + 1}次无法滚动")
                                break
                        else:
                            print("最后冲刺完成，仍未发现新内容，停止滚动")
                            break
                else:
                    no_new_content_count = 0
                    stable_count = 0
                    print(f"发现新内容，笔记数量: {last_note_count} -> {current_note_count}")
                
                last_note_count = current_note_count
                
                # 检查是否有加载更多按钮
                load_more_btn = self._find_load_more_button()
                if load_more_btn:
                    try:
                        print("点击加载更多按钮...")
                        load_more_btn.click()
                        time.sleep(2)  # 减少等待时间
                    except Exception:
                        pass
                
                # 检查是否到了页面底部
                if self._check_no_more_notes():
                    print("检测到没有更多笔记")
                    break
            
            # 最终检查
            final_notes = self._find_note_elements()
            print(f"快速滚动完成，共滚动 {scroll_count} 次，最终找到 {len(final_notes)} 条笔记")
            
        except Exception as e:
            print(f"自动滚动时发生错误: {e}")
    
    def _find_load_more_button(self) -> Optional:
        """查找加载更多按钮"""
        try:
            for selector in Locators.LOAD_MORE_BUTTON_SELECTORS:
                try:
                    btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if btn.is_displayed() and btn.is_enabled():
                        return btn
                except NoSuchElementException:
                    continue
            return None
        except Exception:
            return None
    
    def _check_no_more_notes(self) -> bool:
        """检查是否没有更多笔记"""
        try:
            for selector in Locators.NO_MORE_NOTES_SELECTORS:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        return True
                except NoSuchElementException:
                    continue
            return False
        except Exception:
            return False
    
    def extract_notes_with_auto_scroll(self) -> List[Dict]:
        """
        提取笔记数据，包含自动滚动功能
        
        Returns:
            笔记列表
        """
        notes = []
        
        if not self.login_if_needed():
            print("登录失败，无法提取笔记")
            return notes
        
        try:
            print("开始自动滚动加载笔记...")
            self._auto_scroll_content_area()
            
            print("开始提取笔记数据...")
            
            # 提取笔记
            note_elements = self._find_note_elements()
            if not note_elements:
                print("未找到笔记元素")
                return notes
            
            print(f"找到 {len(note_elements)} 个笔记元素")
            
            for i, element in enumerate(note_elements):
                try:
                    note_data = self._extract_note_data(element, i)
                    if note_data:
                        notes.append(note_data)
                        print(f"成功提取笔记 {i+1}: {note_data['title'][:30]}...")
                except Exception as e:
                    print(f"提取笔记数据失败: {e}")
                    continue
            
            print(f"成功提取 {len(notes)} 条笔记")
            
        except Exception as e:
            print(f"提取笔记时发生错误: {e}")
        
        return notes
