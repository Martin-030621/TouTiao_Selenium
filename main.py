import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
from urllib.parse import quote
import requests
import os
import random

def download_stealth_js():
    """下载 stealth.min.js 文件"""
    url = "https://raw.githubusercontent.com/requireCool/stealth.min.js/main/stealth.min.js"
    try:
        response = requests.get(url)
        with open("stealth.min.js", "w", encoding='utf-8') as f:
            f.write(response.text)
    except:
        print("stealth.js 下载失败，请检查网络连接")
        return False
    return True

def setup_driver():
    chrome_options = Options()
    
    # 基本设置
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 添加更多的反检测参数
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-web-security')
    
    # 使用真实的 User-Agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # 注入更强的反检测代码
    js_script = """
    // 重写 webdriver 属性
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // 重写 chrome 属性
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
    };
    
    // 重写 permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
    
    // 添加语言和插件
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh', 'en']
    });
    
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {
                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            }
        ]
    });
    
    // 清除自动化标记
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    """
    
    # 注入自定义 JS
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": js_script
    })
    
    # 如果存在 stealth.js，也注入它
    stealth_js_path = "stealth.min.js"
    if os.path.exists(stealth_js_path):
        with open(stealth_js_path, "r", encoding='utf-8') as f:
            stealth_js = f.read()
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": stealth_js
        })
        print("成功注入 stealth.js")
    
    return driver

def get_search_results(driver, keyword, page_num=0, city=None):
    encoded_keyword = quote(keyword)
    # 添加页码参数
    url = f'https://so.toutiao.com/search?dvpf=pc&source=pagination&keyword={encoded_keyword}&pd=synthesis&action_type=pagination&from=search_tab&cur_tab_title=search_tab&filter_vendor=site&index_resource=site&filter_period=all&min_time=0&max_time=1737487088&page_num={page_num}'
    
    try:
        if page_num == 0:  # 只在第一页时执行以下操作
            # 清除所有 cookies
            driver.delete_all_cookies()
            
            # 访问页面前先访问一个正常页面
            driver.get("https://www.toutiao.com")
            time.sleep(3)
            
            # 然后访问搜索页
            driver.get(url)
            print("请在浏览器中完成验证...")
            
            input("验证完成后请按回车键继续...")
        else:
            # 直接访问对应页码
            print(f"\n正在爬取第 {page_num + 1} 页...")
            driver.get(url)
            time.sleep(5)
        
        # 移除切换到综合搜索标签的代码，因为URL已经指定了
        
        # 等待页面加载
        time.sleep(5)
        
        # 尝试查找文章元素
        selectors = [
            '.cs-view-result',
            '.result-content',
            '[data-log-click]'
        ]
        
        articles = []
        seen_titles = set()
        seen_urls = set()
        
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"使用选择器 {selector} 找到 {len(elements)} 个元素")
                for element in elements:
                    try:
                        # 检查是否是不需要的内容类型
                        element_html = element.get_attribute('outerHTML').lower()
                        if any(keyword in element_html for keyword in [
                            '视频', '小视频', '最新资讯', 'video', 
                            '图片', '组图', '图集', 'image', 'photo'
                        ]):
                            continue
                        
                        # 尝试提取链接和标题
                        links = element.find_elements(By.CSS_SELECTOR, 'a[href*="toutiao.com"]')
                        for link in links:
                            url = link.get_attribute('href')
                            if url and not any(keyword in url.lower() for keyword in [
                                'video', 'image', 'photo', 'pic', 'img'
                            ]):
                                title = link.text.strip() or link.get_attribute('title')
                                # 检查标题是否包含城市名称
                                if (title and title not in seen_titles and url not in seen_urls 
                                    and (city in title or f"广东{city}" in title)):  # 添加城市名称检查
                                    articles.append({
                                        'title': title,
                                        'url': url
                                    })
                                    seen_titles.add(title)
                                    seen_urls.add(url)
                                    print(f"找到相关文章: {title}")
                    except Exception as e:
                        continue
                
                if articles:
                    break
        
        return articles
        
    except Exception as e:
        print(f"获取搜索结果时出错: {e}")
        return []

def save_results(articles, filename='search_results.json'):
    try:
        # 读取现有文件内容（如果存在）
        existing_articles = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
                print(f"读取到现有文章 {len(existing_articles)} 篇")
            except json.JSONDecodeError:
                print("现有文件格式错误，将创建新文件")
            except Exception as e:
                print(f"读取现有文件时出错: {e}")
        
        # 合并现有文章和新文章
        all_articles = existing_articles + articles
        
        # 去重（基于URL）
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        # 保存合并后的结果
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(unique_articles, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存到 {filename}")
        print(f"文件中共有 {len(unique_articles)} 篇文章 (新增 {len(articles)} 篇)")
        
    except IOError as e:
        print(f"保存文件时出错: {e}")

def get_article_content(driver, article):
    """获取文章详细内容"""
    try:
        print(f"\n正在爬取文章: {article['title']}")
        driver.get(article['url'])
        time.sleep(3)  # 等待页面加载
        
        # 获取文章内容
        content = ""
        
        # 尝试多个可能的选择器
        content_selectors = [
            'article',
            '.article-content',
            '.article-box',
            '.article__content',
            '.content-article',
            '#article-content',
            '.article'
        ]
        
        for selector in content_selectors:
            try:
                content_element = driver.find_element(By.CSS_SELECTOR, selector)
                if content_element:
                    # 获取所有段落文本
                    paragraphs = content_element.find_elements(By.TAG_NAME, 'p')
                    content = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
                    if content:
                        break
            except:
                continue
        
        if not content:
            # 如果没有找到特定容器，尝试直接获取所有段落
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            content = '\n'.join([p.text.strip() for p in paragraphs if p.text.strip()])
        
        # 如果内容为空，返回False
        if not content:
            print("未能获取到文章内容")
            return False
            
        # 如果内容太短，也返回False
        if len(content) < 100:  # 可以调整这个阈值
            print(f"文章内容太短（{len(content)}字符），可能不是有效文章")
            return False
        
        # 更新文章信息
        article['content'] = content
        
        # 尝试获取更多信息
        try:
            # 获取发布时间
            if not article.get('publish_time'):
                time_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="time"], [class*="date"]')
                for time_element in time_elements:
                    time_text = time_element.text.strip()
                    if time_text and ('发布' in time_text or '20' in time_text):
                        article['publish_time'] = time_text
                        break
            
            # 获取来源
            if not article.get('source'):
                source_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="source"]')
                for source_element in source_elements:
                    source_text = source_element.text.strip()
                    if source_text and len(source_text) < 20:  # 避免获取到太长的无关文本
                        article['source'] = source_text
                        break
        except Exception as e:
            print(f"获取额外信息时出错: {e}")
        
        print(f"成功获取文章内容，长度: {len(content)} 字符")
        return True
        
    except Exception as e:
        print(f"获取文章内容时出错: {e}")
        return False

def get_guangdong_cities():
    """返回广东省所有地级市列表"""
    return [
        "广州", "深圳", "珠海", "汕头", "佛山", "韶关", "湛江", "肇庆", 
        "江门", "茂名", "惠州", "梅州", "汕尾", "河源", "阳江", "清远", 
        "东莞", "中山", "潮州", "揭阳", "云浮"
    ]

def get_max_page(driver):
    """获取搜索结果的最大页数"""
    try:
        # 尝试获取分页信息
        pagination_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="pagination"]')
        for element in pagination_elements:
            # 获取所有页码按钮
            page_buttons = element.find_elements(By.TAG_NAME, 'button')
            if page_buttons:
                # 获取最后一个数字页码
                for button in reversed(page_buttons):
                    text = button.text.strip()
                    if text.isdigit():
                        return int(text)

        # 如果找不到分页元素，尝试其他方法
        total_text = driver.find_element(By.CSS_SELECTOR, '[class*="total"]').text
        # 提取数字
        import re
        numbers = re.findall(r'\d+', total_text)
        if numbers:
            total_results = int(numbers[0])
            # 假设每页10条结果
            return (total_results + 9) // 10

    except Exception as e:
        print(f"获取最大页数时出错: {e}")

    return 520  # 如果无法获取，返回默认值

def get_cache_filename(city):
    """获取缓存文件名"""
    return f'cache_{city}.json'

def load_cache(city):
    """加载缓存数据"""
    cache_file = get_cache_filename(city)
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                print(f"已加载 {city} 的缓存数据")
                return cache_data
    except Exception as e:
        print(f"加载缓存出错: {e}")
    return {'last_page': -1, 'visited_urls': [], 'articles': []}

def save_cache(city, cache_data):
    """保存缓存数据"""
    cache_file = get_cache_filename(city)
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"已更新 {city} 的缓存数据")
    except Exception as e:
        print(f"保存缓存出错: {e}")

def save_batch(articles, batch_num):
    """保存一批文章"""
    batch_file = f'fire_news_batch_{batch_num}.json'
    try:
        # 读取现有文件内容（如果存在）
        existing_articles = []
        if os.path.exists(batch_file):
            try:
                with open(batch_file, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
            except Exception as e:
                print(f"读取现有批次文件出错: {e}")
        
        # 合并文章并去重
        all_articles = existing_articles + articles
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        # 保存合并后的结果
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(unique_articles, f, ensure_ascii=False, indent=2)
        print(f"已保存第 {batch_num} 批文章到 {batch_file}，共 {len(unique_articles)} 篇")
    except Exception as e:
        print(f"保存批次文件时出错: {e}")

def main(start_page=0, start_city_index=0):
    # 下载 stealth.js
    if not os.path.exists("stealth.min.js"):
        if not download_stealth_js():
            print("无法下载 stealth.js，程序退出")
            return

    cities = get_guangdong_cities()

    driver = setup_driver()
    try:
        total_articles = []  # 用于存储所有城市的文章
        current_batch = 1    # 全局批次号
        batch_articles = []  # 当前批次的文章
        
        for city_index in range(start_city_index, len(cities)):
            city = cities[city_index]
            keyword = f"{city}火灾"
            
            # 加载缓存
            cache_data = load_cache(city)
            visited_urls = set(cache_data['visited_urls'])
            last_page = cache_data['last_page']
            city_articles = cache_data['articles']
            
            # 确定起始页
            page = max(start_page if city_index == start_city_index else 0, last_page + 1)
            valid_articles = len(city_articles)
            consecutive_empty_pages = 0

            print(f"\n开始爬取 {city} 的火灾新闻（第 {city_index + 1}/{len(cities)} 个城市）")
            print(f"已有 {valid_articles} 篇缓存文章，从第 {page + 1} 页继续爬取")

            try:
                while True:
                    try:
                        articles = get_search_results(driver, keyword, page, city)
                        
                        if articles:
                            page_valid_articles = 0
                            for article in articles:
                                # 检查URL是否已经访问过
                                if article['url'] in visited_urls:
                                    print(f"跳过已爬取的文章: {article['title']}")
                                    continue
                                    
                                success = get_article_content(driver, article)
                                if success:
                                    article['city'] = city
                                    city_articles.append(article)
                                    batch_articles.append(article)
                                    visited_urls.add(article['url'])
                                    valid_articles += 1
                                    page_valid_articles += 1
                                    
                                    # 每10篇文章保存一次批次
                                    if len(batch_articles) >= 10:
                                        save_batch(batch_articles, current_batch)
                                        batch_articles = []
                                        current_batch += 1
                                    
                                    # 更新缓存
                                    cache_data = {
                                        'last_page': page,
                                        'visited_urls': list(visited_urls),
                                        'articles': city_articles
                                    }
                                    save_cache(city, cache_data)
                                    
                                    wait_time = random.randint(1, 3)
                                    print(f"等待 {wait_time} 秒后继续...")
                                    time.sleep(wait_time)

                            print(f"第 {page + 1} 页成功爬取到 {page_valid_articles} 篇有效文章")
                            if page_valid_articles > 0:
                                consecutive_empty_pages = 0
                            else:
                                consecutive_empty_pages += 1
                        else:
                            print(f"第 {page + 1} 页未找到相关文章")
                            consecutive_empty_pages += 1

                        if consecutive_empty_pages >= 2:
                            print(f"{city} 连续两页未找到有效结果，开始下一个城市")
                            break

                        page += 1
                        wait_time = random.randint(3, 6)
                        print(f"等待 {wait_time} 秒后继续下一页...")
                        time.sleep(wait_time)

                    except Exception as e:
                        print(f"爬取第 {page + 1} 页时出错: {e}")
                        print("尝试继续下一个城市...")
                        break

                # 将当前城市的文章添加到总文章列表
                total_articles.extend(city_articles)
                
                if city_articles:
                    print(f"\n{city}爬取完成，共获取到 {valid_articles} 篇有效文章")
                else:
                    print(f"{city}未爬取到任何有效结果")

                # 保存最后一个不完整的批次
                if batch_articles:
                    save_batch(batch_articles, current_batch)
                    batch_articles = []
                    current_batch += 1

                if city_index < len(cities) - 1:
                    wait_time = random.randint(5, 10)
                    print(f"等待 {wait_time} 秒后开始爬取下一个城市...")
                    time.sleep(wait_time)

            except Exception as e:
                print(f"爬取 {city} 时出错: {e}")
                print("继续下一个城市...")
                continue

        # 保存所有文章到一个总文件
        if total_articles:
            final_file = 'guangdong_fire_news.json'
            with open(final_file, 'w', encoding='utf-8') as f:
                json.dump(total_articles, f, ensure_ascii=False, indent=2)
            print(f"\n所有文章已保存到 {final_file}，共 {len(total_articles)} 篇")
        
        print("\n所有城市爬取完成！")
        
    except Exception as e:
        print(f"主程序执行出错: {e}")
        print(f"出错时正在爬取: {cities[city_index]}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    print("广东省地级市列表：")
    cities = get_guangdong_cities()
    for i, city in enumerate(cities):
        print(f"{i}. {city}")
    
    start_city_index = int(input("\n请输入起始城市序号（0-20）："))
    start_page = int(input("请输入起始页码（第1页请输入0）："))
    
    if 0 <= start_city_index < len(cities):
        main(start_page, start_city_index)
    else:
        print("无效的城市序号！")
