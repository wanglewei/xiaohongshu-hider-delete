"""
权限修改模块
处理小红书笔记的权限设置修改
"""

import time
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from locators import Locators


class PermissionManager:
    """权限管理器"""
    
    def __init__(self, driver: webdriver.Chrome):
        """
        初始化权限管理器
        
        Args:
            driver: WebDriver实例
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def hide_note(self, note_element) -> bool:
        """
        隐藏单个笔记（设置为仅自己可见）
        
        Args:
            note_element: 笔记元素
            
        Returns:
            是否成功隐藏
        """
        return self._set_note_visibility(note_element, "private")
    
    def hide_notes_batch(self, notes: List[Dict], delay: float = 2.0) -> Dict[str, int]:
        """
        批量隐藏笔记
        
        Args:
            notes: 笔记列表
            delay: 操作间隔时间（秒）
            
        Returns:
            操作结果统计
        """
        results = {
            'success': 0,
            'failed': 0,
            'total': len(notes)
        }
        
        print(f"开始批量隐藏 {len(notes)} 条笔记...")
        
        # 首先检查WebDriver连接
        if not self._check_driver_connection():
            print("❌ WebDriver连接已断开，无法执行批量操作")
            print("请重新启动程序并确保浏览器没有被关闭")
            results['failed'] = len(notes)
            return results
        
        for i, note in enumerate(notes, 1):
            print(f"处理第 {i}/{len(notes)} 条笔记: {note['title'][:30]}...")
            
            try:
                # 在每次操作前检查连接
                if not self._check_driver_connection():
                    print("❌ WebDriver连接断开，停止批量操作")
                    print(f"已处理 {i-1} 条笔记，成功 {results['success']} 条，失败 {results['failed']} 条")
                    break
                
                # 重新获取笔记元素（避免元素过期）
                note_element = self._refresh_note_element(note['note_id'])
                if not note_element:
                    print(f"❌ 无法找到笔记元素: {note['note_id']}")
                    results['failed'] += 1
                    continue
                
                # 隐藏笔记
                if self.hide_note(note_element):
                    results['success'] += 1
                    print(f"✓ 成功隐藏")
                else:
                    results['failed'] += 1
                    print(f"✗ 隐藏失败")
                
                # 操作间隔
                if i < len(notes):
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"❌ 处理笔记时发生错误: {e}")
                results['failed'] += 1
                
                # 如果是连接错误，停止批量操作
                if "Connection refused" in str(e) or "Max retries exceeded" in str(e):
                    print("❌ 检测到连接问题，停止批量操作")
                    print(f"已处理 {i-1} 条笔记，成功 {results['success']} 条，失败 {results['failed']} 条")
                    break
        
        print(f"批量操作完成: 成功 {results['success']} 条，失败 {results['failed']} 条")
        
        # 如果有失败的操作，提供建议
        if results['failed'] > 0:
            print("\n⚠️ 部分操作失败，可能的原因：")
            print("1. 浏览器连接断开 - 请重新启动程序")
            print("2. 页面结构变化 - 请更新选择器")
            print("3. 网络问题 - 请检查网络连接")
            print("4. 权限问题 - 请确保有足够的权限")
        
        return results
    
    def _check_driver_connection(self) -> bool:
        """
        检查WebDriver连接是否正常
        
        Returns:
            连接是否正常
        """
        try:
            # 尝试获取当前URL来测试连接
            self.driver.current_url
            return True
        except Exception as e:
            print(f"WebDriver连接检查失败: {e}")
            return False
    
    def _refresh_note_element(self, note_id: str) -> Optional[webdriver.remote.webelement.WebElement]:
        """
        刷新笔记元素引用
        
        Args:
            note_id: 笔记ID
            
        Returns:
            新的笔记元素或None
        """
        try:
            # 首先检查WebDriver连接
            if not self._check_driver_connection():
                print("WebDriver连接已断开，无法刷新元素")
                return None
            
            # 如果note_id包含note_index_，使用索引匹配
            if note_id.startswith("note_index_"):
                try:
                    index = int(note_id.split("_")[-1])
                    print(f"使用索引查找笔记: {note_id} (索引: {index})")
                    
                    # 重新查找所有笔记元素
                    for selector in Locators.NOTE_ITEM_SELECTORS:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            print(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                            
                            if index < len(elements):
                                print(f"✓ 通过索引 {index} 找到元素")
                                return elements[index]
                        except (NoSuchElementException, Exception) as e:
                            print(f"使用选择器 {selector} 查找元素失败: {e}")
                            continue
                    
                    print(f"❌ 索引 {index} 超出范围")
                    return None
                    
                except (ValueError, IndexError) as e:
                    print(f"解析索引失败: {e}")
                    # 继续尝试其他方法
            
            # 原有的ID匹配逻辑作为备用
            search_id = note_id
            if note_id.startswith("note_"):
                search_id = note_id[5:]  # 移除note_前缀
            
            print(f"正在查找笔记ID: {note_id} (搜索ID: {search_id})")
            
            # 尝试多种选择器重新查找元素
            for selector in Locators.NOTE_ITEM_SELECTORS:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                    
                    for i, element in enumerate(elements):
                        # 获取所有可能的ID属性
                        element_id = element.get_attribute('data-note-id') or element.get_attribute('id') or element.get_attribute('data-id')
                        
                        # 尝试多种匹配方式
                        if element_id == note_id:
                            print(f"✓ 完全匹配找到元素: {element_id}")
                            return element
                        elif element_id == search_id:
                            print(f"✓ 去前缀匹配找到元素: {element_id}")
                            return element
                        elif element_id and search_id in element_id:
                            print(f"✓ 部分匹配找到元素: {element_id}")
                            return element
                        
                        # 如果没有ID属性，尝试通过标题匹配（作为备用方案）
                        if not element_id:
                            try:
                                title_element = element.find_element(By.CSS_SELECTOR, ".title, .note-title, h3, h4")
                                title_text = title_element.text.strip()
                                # 这里可以添加标题匹配逻辑，但需要先获取笔记标题
                            except:
                                pass
                                
                except (NoSuchElementException, Exception) as e:
                    print(f"使用选择器 {selector} 查找元素失败: {e}")
                    continue
            
            print(f"❌ 未找到笔记ID为 {note_id} 的元素")
            return None
        except Exception as e:
            print(f"刷新笔记元素时发生错误: {e}")
            return None
    
    def _wait_for_operation_complete(self) -> None:
        """等待操作完成"""
        try:
            # 等待加载提示消失
            self.wait.until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, Locators.LOADING_SPINNER))
            )
        except TimeoutException:
            pass
        
        # 额外等待时间确保操作完成
        time.sleep(1)
    
    def get_note_id(self, note_element) -> Optional[str]:
        """
        获取笔记ID
        
        Args:
            note_element: 笔记元素
            
        Returns:
            笔记ID或None
        """
        try:
            import re
            
            # 首先尝试从data-note-id属性获取
            note_id = note_element.get_attribute('data-note-id')
            if note_id and re.match(r'^[a-f0-9]{24}$', note_id):
                print(f"✓ 从data-note-id获取到有效ID: {note_id}")
                return note_id
            
            # 尝试从其他属性获取
            for attr in ['id', 'data-id', 'note-id']:
                note_id = note_element.get_attribute(attr)
                if note_id and re.match(r'^[a-f0-9]{24}$', note_id):
                    print(f"✓ 从{attr}属性获取到有效ID: {note_id}")
                    return note_id
            
            # 尝试从链接中提取
            try:
                link_element = note_element.find_element(By.TAG_NAME, "a")
                href = link_element.get_attribute('href')
                if href:
                    print(f"找到链接: {href}")
                    # 从URL中提取笔记ID，支持多种格式
                    patterns = [
                        r'/notes?/([a-f0-9]{24})',  # /note/ 或 /notes/ + 24位十六进制
                        r'/explore/([a-f0-9]{24})',  # /explore/ + 24位十六进制
                        r'noteId=([a-f0-9]{24})',    # 参数中的noteId
                        r'id=([a-f0-9]{24})'         # 参数中的id
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, href)
                        if match:
                            note_id = match.group(1)
                            print(f"✓ 从链接提取到有效ID: {note_id}")
                            return note_id
            except NoSuchElementException:
                pass
            
            # 尝试从note-info属性中提取
            note_info = note_element.get_attribute('note-info')
            if note_info:
                print(f"找到note-info属性: {note_info}")
                # 尝试解析JSON格式的note-info
                try:
                    import json
                    info_dict = json.loads(note_info)
                    if 'id' in info_dict:
                        note_id = info_dict['id']
                        if re.match(r'^[a-f0-9]{24}$', note_id):
                            print(f"✓ 从note-info JSON提取到有效ID: {note_id}")
                            return note_id
                except:
                    pass
                
                # 尝试从note-info字符串中提取ID
                match = re.search(r'[a-f0-9]{24}', note_info)
                if match:
                    note_id = match.group(0)
                    print(f"✓ 从note-info字符串提取到有效ID: {note_id}")
                    return note_id
            
            print("❌ 未能获取到有效的笔记ID")
            return None
            
        except Exception as e:
            print(f"获取笔记ID时发生错误: {e}")
            return None

    def check_note_visibility(self, note_element) -> Optional[str]:
        """
        检查笔记的当前可见性状态
        
        Args:
            note_element: 笔记元素
            
        Returns:
            可见性状态或None
        """
        try:
            # 这里需要根据实际页面结构来判断笔记的可见性
            # 可能需要检查权限按钮的文本、图标或其他指示器
            permission_btn = note_element.find_element(By.CSS_SELECTOR, Locators.PERMISSION_BUTTON)
            btn_text = permission_btn.text.strip()
            
            if "仅自己可见" in btn_text or "私密" in btn_text:
                return "private"
            elif "公开" in btn_text or "所有人可见" in btn_text:
                return "public"
            else:
                return "unknown"
                
        except Exception as e:
            print(f"检查笔记可见性时发生错误: {e}")
            return None
    
    def show_note(self, note_element) -> bool:
        """
        显示单个笔记（设置为所有人可见）
        
        Args:
            note_element: 笔记元素
            
        Returns:
            是否成功显示
        """
        return self._set_note_visibility(note_element, "public")
    
    def show_notes_batch(self, notes: List[Dict], delay: float = 2.0) -> Dict[str, int]:
        """
        批量显示笔记
        
        Args:
            notes: 笔记列表
            delay: 操作间隔时间（秒）
            
        Returns:
            操作结果统计
        """
        results = {
            'success': 0,
            'failed': 0,
            'total': len(notes)
        }
        
        print(f"开始批量显示 {len(notes)} 条笔记...")
        
        # 首先检查WebDriver连接
        if not self._check_driver_connection():
            print("❌ WebDriver连接已断开，无法执行批量操作")
            print("请重新启动程序并确保浏览器没有被关闭")
            results['failed'] = len(notes)
            return results
        
        for i, note in enumerate(notes, 1):
            print(f"处理第 {i}/{len(notes)} 条笔记: {note['title'][:30]}...")
            
            try:
                # 在每次操作前检查连接
                if not self._check_driver_connection():
                    print("❌ WebDriver连接断开，停止批量操作")
                    print(f"已处理 {i-1} 条笔记，成功 {results['success']} 条，失败 {results['failed']} 条")
                    break
                
                # 重新获取笔记元素（避免元素过期）
                note_element = self._refresh_note_element(note['note_id'])
                if not note_element:
                    print(f"❌ 无法找到笔记元素: {note['note_id']}")
                    results['failed'] += 1
                    continue
                
                # 显示笔记
                if self.show_note(note_element):
                    results['success'] += 1
                    print(f"✓ 成功显示")
                else:
                    results['failed'] += 1
                    print(f"✗ 显示失败")
                
                # 操作间隔
                if i < len(notes):
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"❌ 处理笔记时发生错误: {e}")
                results['failed'] += 1
                
                # 如果是连接错误，停止批量操作
                if "Connection refused" in str(e) or "Max retries exceeded" in str(e):
                    print("❌ 检测到连接问题，停止批量操作")
                    print(f"已处理 {i-1} 条笔记，成功 {results['success']} 条，失败 {results['failed']} 条")
                    break
        
        print(f"批量操作完成: 成功 {results['success']} 条，失败 {results['failed']} 条")
        
        # 如果有失败的操作，提供建议
        if results['failed'] > 0:
            print("\n⚠️ 部分操作失败，可能的原因：")
            print("1. 浏览器连接断开 - 请重新启动程序")
            print("2. 页面结构变化 - 请更新选择器")
            print("3. 网络问题 - 请检查网络连接")
            print("4. 权限问题 - 请确保有足够的权限")
        
        return results
    
    def _set_note_visibility(self, note_element, visibility: str) -> bool:
        """
        设置笔记可见性
        
        Args:
            note_element: 笔记元素
            visibility: 可见性类型 ("private" 或 "public")
            
        Returns:
            是否成功设置
        """
        try:
            # 检查WebDriver连接
            if not self._check_driver_connection():
                print("WebDriver连接已断开")
                return False
            
            # 滚动到笔记位置
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", note_element)
            time.sleep(1)
            
            # 查找权限设置按钮 - 尝试多种选择器
            permission_btn = None
            for selector in Locators.PERMISSION_BUTTON_SELECTORS:
                try:
                    permission_btn = note_element.find_element(By.CSS_SELECTOR, selector)
                    if permission_btn.is_displayed() and permission_btn.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if not permission_btn:
                print("未找到可用的权限设置按钮")
                return False
            
            # 点击权限设置按钮
            try:
                permission_btn.click()
            except ElementClickInterceptedException:
                # 如果点击被拦截，尝试JavaScript点击
                self.driver.execute_script("arguments[0].click();", permission_btn)
            
            time.sleep(2)
            
            # 根据可见性类型选择选项
            if visibility == "private":
                option_text = "仅自己可见"
                alternative_options = [
                    "//div[contains(text(), '私密')]",
                    "//span[contains(text(), '仅自己')]",
                    "//button[contains(text(), '仅自己可见')]",
                    "//label[contains(text(), '仅自己可见')]"
                ]
            else:  # public
                option_text = "所有人可见"
                alternative_options = [
                    "//div[contains(text(), '公开')]",
                    "//span[contains(text(), '所有人')]",
                    "//button[contains(text(), '所有人可见')]",
                    "//label[contains(text(), '所有人可见')]"
                ]
            
            # 等待权限选项出现并点击相应选项
            try:
                # 首先等待一下让选项加载
                time.sleep(2)
                
                # 使用更精确的XPath定位选项
                if visibility == "private":
                    # 查找包含"仅自己可见"文本的div元素
                    xpath = "//div[contains(@class, 'custom-option') and .//div[contains(text(), '仅自己可见')]]"
                else:
                    # 查找包含"公开可见"文本的div元素  
                    xpath = "//div[contains(@class, 'custom-option') and .//div[contains(text(), '公开可见')]]"
                
                print(f"使用XPath查找选项: {xpath}")
                options = self.driver.find_elements(By.XPATH, xpath)
                
                if options:
                    print(f"找到 {len(options)} 个匹配的选项")
                    # 使用JavaScript点击第一个匹配的选项
                    target_option = options[0]
                    self.driver.execute_script("arguments[0].click();", target_option)
                    time.sleep(1)
                    print(f"✓ 成功点击'{option_text}'选项")
                else:
                    print(f"未找到'{option_text}'选项，尝试备用方式...")
                    
                    # 尝试其他可能的选项文本
                    for option_xpath in alternative_options:
                        try:
                            target_option = self.driver.find_element(By.XPATH, option_xpath)
                            if target_option.is_displayed():
                                self.driver.execute_script("arguments[0].click();", target_option)
                                time.sleep(1)
                                print(f"✓ 通过备用XPath成功点击选项")
                                break
                        except NoSuchElementException:
                            continue
                    else:
                        print("❌ 所有方式都无法找到选项")
                        return False
                
            except Exception as e:
                print(f"选择可见性选项时发生错误: {e}")
                return False
            
            # 点击确认按钮
            try:
                confirm_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, Locators.PERMISSION_CONFIRM_BUTTON))
                )
                confirm_btn.click()
                time.sleep(2)
                print("✓ 成功点击确认按钮")
            except TimeoutException:
                print("未找到确认按钮，尝试JavaScript点击...")
                try:
                    confirm_btn = self.driver.find_element(By.XPATH, Locators.PERMISSION_CONFIRM_BUTTON)
                    self.driver.execute_script("arguments[0].click();", confirm_btn)
                    time.sleep(2)
                    print("✓ 通过JavaScript成功点击确认按钮")
                except NoSuchElementException:
                    print("❌ 无法找到确认按钮")
                    return False
            
            # 等待操作完成
            self._wait_for_operation_complete()
            
            return True
            
        except Exception as e:
            print(f"设置笔记可见性时发生错误: {e}")
            return False
    
    def delete_note(self, note_element) -> bool:
        """
        删除单个笔记
        
        Args:
            note_element: 笔记元素
            
        Returns:
            是否成功删除
        """
        return self._delete_note_operation(note_element)
    
    def delete_notes_batch(self, notes: List[Dict], delay: float = 2.0) -> Dict[str, int]:
        """
        批量删除笔记
        
        Args:
            notes: 笔记列表
            delay: 操作间隔时间（秒）
            
        Returns:
            操作结果统计
        """
        results = {
            'success': 0,
            'failed': 0,
            'total': len(notes)
        }
        
        print(f"开始批量删除 {len(notes)} 条笔记...")
        
        # 首先检查WebDriver连接
        if not self._check_driver_connection():
            print("❌ WebDriver连接已断开，无法执行批量操作")
            print("请重新启动程序并确保浏览器没有被关闭")
            results['failed'] = len(notes)
            return results
        
        for i, note in enumerate(notes, 1):
            print(f"处理第 {i}/{len(notes)} 条笔记: {note['title'][:30]}...")
            
            try:
                # 在每次操作前检查连接
                if not self._check_driver_connection():
                    print("❌ WebDriver连接断开，停止批量操作")
                    print(f"已处理 {i-1} 条笔记，成功 {results['success']} 条，失败 {results['failed']} 条")
                    break
                
                # 重新获取笔记元素（避免元素过期）
                note_element = self._refresh_note_element(note['note_id'])
                if not note_element:
                    print(f"❌ 无法找到笔记元素: {note['note_id']}")
                    results['failed'] += 1
                    continue
                
                # 删除笔记
                if self.delete_note(note_element):
                    results['success'] += 1
                    print(f"✓ 成功删除")
                else:
                    results['failed'] += 1
                    print(f"✗ 删除失败")
                
                # 操作间隔
                if i < len(notes):
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"❌ 处理笔记时发生错误: {e}")
                results['failed'] += 1
                
                # 如果是连接错误，停止批量操作
                if "Connection refused" in str(e) or "Max retries exceeded" in str(e):
                    print("❌ 检测到连接问题，停止批量操作")
                    print(f"已处理 {i-1} 条笔记，成功 {results['success']} 条，失败 {results['failed']} 条")
                    break
        
        print(f"批量操作完成: 成功 {results['success']} 条，失败 {results['failed']} 条")
        
        # 如果有失败的操作，提供建议
        if results['failed'] > 0:
            print("\n⚠️ 部分操作失败，可能的原因：")
            print("1. 浏览器连接断开 - 请重新启动程序")
            print("2. 页面结构变化 - 请更新选择器")
            print("3. 网络问题 - 请检查网络连接")
            print("4. 权限问题 - 请确保有足够的权限")
        
        return results
    
    def _delete_note_operation(self, note_element) -> bool:
        """
        执行删除笔记操作
        
        Args:
            note_element: 笔记元素
            
        Returns:
            是否成功删除
        """
        try:
            # 检查WebDriver连接
            if not self._check_driver_connection():
                print("WebDriver连接已断开")
                return False
            
            # 滚动到笔记位置
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", note_element)
            time.sleep(1)
            
            # 查找删除按钮 - 尝试多种选择器
            delete_btn = None
            for selector in Locators.DELETE_BUTTON_SELECTORS:
                try:
                    delete_btn = note_element.find_element(By.CSS_SELECTOR, selector)
                    if delete_btn.is_displayed() and delete_btn.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if not delete_btn:
                print("未找到可用的删除按钮")
                return False
            
            # 点击删除按钮
            try:
                delete_btn.click()
            except ElementClickInterceptedException:
                # 如果点击被拦截，尝试JavaScript点击
                self.driver.execute_script("arguments[0].click();", delete_btn)
            
            time.sleep(2)
            
            # 点击确认删除按钮
            try:
                confirm_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, Locators.DELETE_CONFIRM_BUTTON))
                )
                confirm_btn.click()
                time.sleep(2)
                print("✓ 成功点击删除确认按钮")
            except TimeoutException:
                print("未找到删除确认按钮，尝试备用选择器...")
                # 尝试其他可能的确认按钮
                for confirm_xpath in Locators.DELETE_CONFIRM_ALTERNATIVES:
                    try:
                        confirm_btn = self.driver.find_element(By.XPATH, confirm_xpath)
                        if confirm_btn.is_displayed():
                            # 尝试普通点击
                            try:
                                confirm_btn.click()
                                print(f"✓ 通过选择器 {confirm_xpath} 成功点击删除确认按钮")
                            except ElementClickInterceptedException:
                                # 如果被遮挡，使用JavaScript点击
                                self.driver.execute_script("arguments[0].click();", confirm_btn)
                                print(f"✓ 通过JavaScript点击删除确认按钮")
                            time.sleep(2)
                            break
                    except NoSuchElementException:
                        continue
                else:
                    print("❌ 无法找到删除确认按钮")
                    return False
            
            # 等待操作完成
            self._wait_for_operation_complete()
            
            return True
            
        except Exception as e:
            print(f"删除笔记时发生错误: {e}")
            return False
    
    def get_notes_visibility_status(self, notes: List[Dict]) -> Dict[str, str]:
        """
        获取多个笔记的可见性状态
        
        Args:
            notes: 笔记列表
            
        Returns:
            笔记ID到可见性状态的映射
        """
        status_map = {}
        
        for note in notes:
            try:
                note_element = self._refresh_note_element(note['note_id'])
                if note_element:
                    status = self.check_note_visibility(note_element)
                    status_map[note['note_id']] = status or "unknown"
                else:
                    status_map[note['note_id']] = "not_found"
            except Exception as e:
                print(f"获取笔记 {note['note_id']} 状态时发生错误: {e}")
                status_map[note['note_id']] = "error"
        
        return status_map
