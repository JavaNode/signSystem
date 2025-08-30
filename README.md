# 联盟杯内训师大赛管理系统

一个专为银行内训师比赛设计的全功能管理系统，支持签到、分组、抽签、打分、统计等完整流程。

## 🎯 系统特色

- **扫码签到**: 参赛者扫描专属二维码，输入手机后四位+姓名完成身份验证
- **智能分组**: 按单位进行分组，同一单位成员在同一组
- **移动评分**: 评委使用手机进行0-10分评分，操作简单直观
- **实时统计**: 签到状态、评分情况、排名等数据实时更新
- **数据导出**: 支持签到表、成绩单等各类报表导出

## 🏗️ 技术架构

### 后端技术栈
- **Python 3.8+** - 主要开发语言
- **FastAPI** - 现代高性能Web框架
- **SQLAlchemy** - ORM数据库操作
- **SQLite** - 轻量级数据库
- **Pydantic** - 数据验证
- **qrcode** - 二维码生成

### 前端技术栈
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript
- **Element Plus** - Vue 3组件库
- **Vite** - 现代前端构建工具
- **Pinia** - Vue状态管理
- **Axios** - HTTP客户端

## 📁 项目结构

```
signSystem/
├── backend/                 # Python后端
│   ├── app/                # 应用核心代码
│   │   ├── models/         # 数据模型
│   │   ├── api/            # API路由
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── simple_app.py       # 简化版应用(用于快速测试)
│   ├── requirements.txt    # Python依赖
│   └── run.py             # 启动脚本
├── frontend/               # Vue3前端
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面组件
│   │   ├── api/            # API接口
│   │   ├── stores/         # 状态管理
│   │   └── utils/          # 工具函数
│   ├── package.json        # 前端依赖
│   └── vite.config.ts      # Vite配置
├── data/                   # 数据文件
│   ├── photos/             # 参赛者照片
│   └── exports/            # 导出文件
├── start.bat              # Windows启动脚本
├── start.sh               # Linux/Mac启动脚本
└── README.md              # 项目说明
```

## 🚀 快速开始

### 方式一：一键启动（推荐）

**Windows系统：**
```bash
# 双击运行或在命令行执行
start.bat
```

**Linux/Mac系统：**
```bash
# 在终端执行
./start.sh
```

### 方式二：手动启动

**1. 启动后端服务**
```bash
cd backend
pip install -r requirements.txt
python simple_app.py
```

**2. 启动前端服务**
```bash
cd frontend
npm install
npm run dev
```

### 访问地址

- **前端管理界面**: http://localhost:3000
- **后端API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 👥 默认账号

### 管理员账号
- 用户名: `admin`
- 密码: `admin123`

### 评委账号
- 用户名: `judge01`
- 密码: `123456`

### 测试参赛者
系统预置了5个测试参赛者，二维码ID分别为：QR001-QR005

## 📱 使用流程

### 1. 比赛前准备
1. 管理员登录系统导入参赛者名单
2. 系统自动按单位进行分组
3. 为每个参赛者生成专属签到二维码
4. 设置评委账号和评分规则

### 2. 比赛当天签到
1. 参赛者使用手机扫描个人二维码
2. 输入手机号后四位 + 真实姓名进行身份验证
3. 验证成功后自动完成签到
4. 可查看比赛安排和组员信息

### 3. 评委打分
1. 评委使用手机登录评分系统
2. 选择参赛者进行0-10分评分
3. 支持滑块精确评分和按钮快速评分
4. 实时查看评分统计和排名

### 4. 数据统计
1. 实时查看签到率和各单位签到情况
2. 评分分布和平均分统计
3. 自动计算排名和获奖名单
4. 一键导出各类报表

## 🔧 系统配置

### 环境要求
- **Python**: 3.8或更高版本
- **Node.js**: 16.0或更高版本
- **浏览器**: Chrome 80+, Firefox 75+, Safari 13+

### 数据库配置
系统默认使用SQLite数据库，数据文件位于 `data/simple_data.json`

### 自定义配置
- 修改 `backend/simple_app.py` 中的端口和配置
- 修改 `frontend/src/api/index.ts` 中的API地址
- 在 `data/photos/` 目录放置参赛者照片

## 📊 功能模块

### 管理端功能
- ✅ 参赛者信息管理
- ✅ 分组管理和调整
- ✅ 签到状态监控
- ✅ 评分情况统计
- ✅ 实时数据大屏
- ✅ 数据导出功能

### 移动端功能
- ✅ 扫码签到验证
- ✅ 个人信息查看
- ✅ 比赛安排查看
- ✅ 评委登录打分
- ✅ 评分历史查看

### 数据统计
- ✅ 签到率统计
- ✅ 各单位签到情况
- ✅ 评分分布图表
- ✅ 实时排行榜
- ✅ 活动时间线

## 🛠️ 开发说明

### 后端开发
```bash
cd backend
# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 初始化数据库
python init_db.py
```

### 前端开发
```bash
cd frontend
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### API文档
启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档

## 📝 更新日志

### v1.0.0 (2024-09-24)
- ✨ 初始版本发布
- ✨ 完整的签到、分组、评分功能
- ✨ 移动端适配和响应式设计
- ✨ 实时数据统计和可视化
- ✨ 一键启动和部署脚本

## 🤝 技术支持

如有问题或建议，请联系开发团队：

- 📧 邮箱: support@example.com
- 📱 电话: 400-xxx-xxxx
- 💬 微信: xxxxxxxx

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

**联盟杯内训师大赛管理系统** - 让比赛管理更简单、更高效！