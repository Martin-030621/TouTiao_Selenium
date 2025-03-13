# 今日头条搜索引擎以及新闻详情页爬虫（Selenium）

## 📝 项目简介
本项目是一个用于爬取今日头条的爬虫程序（本项目以广东火灾为例）。通过今日头条搜索接口，自动获取广东省21个地级市的火灾新闻信息，并将数据以结构化的方式保存。该项目主要用于火灾新闻数据分析和研究。

## 🚀 特色功能
- ✨ 支持广东省21个地级市的火灾新闻爬取
- 🛡️ 智能反爬处理，模拟真实用户行为
- 🔄 断点续爬功能，确保数据完整性
- ⚡ 多线程并发爬取，提升效率
- 🧹 自动数据清洗和结构化存储
- 📊 完善的日志记录系统

## 🛠️ 技术栈
- **Python 3.x**: 主要开发语言
- **Selenium**: 网页自动化操作
- **ChromeDriver**: 浏览器自动化支持
- **BeautifulSoup4**: HTML解析
- **pandas**: 数据处理
- **requests**: HTTP请求
- **fake-useragent**: User-Agent池
- **logging**: 日志管理
- **concurrent.futures**: 多线程支持

## 📊 数据字段
| 字段 | 说明 |
|------|------|
| 标题 | 新闻标题 |
| 发布时间 | 新闻发布的具体时间 |
| 新闻链接 | 原文URL |
| 新闻来源 | 发布媒体 |
| 正文内容 | 新闻主体内容 |
| 发生地点 | 事件发生位置 |
| 关键词 | 新闻标签 |
| 阅读量 | 文章阅读数据（如有） |
| 评论数 | 评论互动数据（如有） |

## 💻 运行环境
- Python 3.8+
- Chrome浏览器
- ChromeDriver（需与Chrome版本匹配）
- 4GB及以上内存
- 稳定网络连接

## 🔧 安装部署

### 1. 获取代码
git clone https://github.com/yourusername/guangdong-fire-news-crawler.git
cd guangdong-fire-news-crawler

### 2. 环境配置
# 创建虚拟环境
python -m venv venv

# Windows激活
venv\Scripts\activate

# Linux/Mac激活
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

## 📈 使用指南

### 配置参数
在`config.py`中设置爬取参数：
CITIES = ['广州', '深圳', '珠海', ...]  # 目标城市
DATE_RANGE = ('2023-01-01', '2024-03-20')  # 时间范围
KEYWORDS = ['火灾', '起火']  # 关键词

### 启动爬虫
python main.py

## ⚖️ 声明

1. 本项目只用于学习测试，严禁用于非法操作！
2. 本项目只用于学习测试，严禁用于非法操作！
3. 本项目只用于学习测试，严禁用于非法操作！

## ⚠️ 注意事项

1. 合理设置爬取频率，避免IP封禁
2. 推荐使用代理IP池
3. 定期更新ChromeDriver
4. 遵守网站robots协议
5. 建议先进行小规模测试

## 📄 许可证
MIT License

## 📞 联系方式
- 作者：XiaoChen
- GitHub：[XiaoChen](https://github.com/Martin-030621)
- INDEX：[个人主页](https://www.aiyuye.cn)

## 🤝 贡献指南
欢迎提交Issue和Pull Request来帮助改进项目。

## 📋 更新日志
### v1.0.0 (2025-01-22)
- 初始版本发布
- 支持基础新闻爬取功能
- 实现多线程并发爬取
