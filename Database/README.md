# CV Database 使用指南

## 文件结构

```
Database/
├── Eric-Database.md          # 主文件（人类编辑）
├── Eric-Database.json        # 生成文件（程序读取）
├── submissions.json          # 投递记录（自动生成）
├── sync.py                   # 同步脚本
└── README.md                 # 本文件
```

## 工作流程

### 1. 更新个人经历

编辑 `Eric-Database.md`，按现有格式添加：

```markdown
**职位名称** _公司 | 地点 | 时间_

- **Bullet 标题**: 详细描述...
- **另一个 Bullet**: 描述...
```

### 2. 同步到 JSON

```bash
python3 sync.py
```

或带详细信息：

```bash
python3 sync.py --verbose
```

只检查不生成：

```bash
python3 sync.py --check
```

### 3. Git 提交

```bash
git add Eric-Database.md Eric-Database.json
git commit -m "更新: 添加 XX 项目经历"
```

## 数据格式

### 工作经历 (experiences)

```json
{
  "id": "fir-Jul2017—Dec2025",
  "company": "First Light Films",
  "title": "Founder & Executive Producer",
  "period": "Jul 2017 — Dec 2025",
  "location": "Shanghai / Global",
  "type": "film",
  "bullets": [
    {
      "id": "fir-1",
      "title": "Led Global Co-Production Financing",
      "text": "详细描述...",
      "tags": ["film", "financing", "international"],
      "metrics": ["$2.5M", "60+ territories"]
    }
  ]
}
```

### 项目案例 (projects)

```json
{
  "id": "brief-history-family",
  "title": "Brief History of A Family",
  "when": "2017 – 2024",
  "client": null,
  "budget": "$2.5M",
  "tags": ["film", "festival", "international"]
}
```

### 技能 (skills)

```json
{
  "production": [...],
  "commercial": [...],
  "tools": [...],
  "languages": [...]
}
```

## 标签系统

自动提取的标签：

- `film` - 电影制作
- `financing` - 融资
- `legal` - 法律/合同
- `international` - 国际/跨境
- `post_production` - 后期制作
- `gaming` - 游戏
- `commercial` - 商业广告
- `leadership` - 团队领导
- `operations` - 运营管理
- `cg_animation` - CG/动画
- `ai` - AI 工具

## 投递记录 submissions.json

每次投递后自动记录：

```json
{
  "submissions": [
    {
      "id": "2026-04-06-netflix-producer",
      "date": "2026-04-06",
      "company": "Netflix",
      "position": "Senior Producer",
      "used_experiences": ["fir-1", "fir-3", "fin-2"],
      "used_projects": ["brief-history-family"],
      "result": "interview"
    }
  ]
}
```

## 注意事项

1. **只编辑 .md 文件** - JSON 是自动生成的
2. **定期同步** - 修改后及时运行 sync.py
3. **Git 版本控制** - 每次更新都提交
4. **备份** - 重要修改前先备份

## 故障排除

### 同步后 bullets 为空
- 检查 Markdown 格式是否正确
- 确保使用 `- **标题**: 内容` 格式

### 标签提取不准确
- 在 sync.py 中修改 `extract_tags()` 函数
- 或手动在 JSON 中调整

### 项目解析失败
- 确保项目格式：`**数字. 项目名称**`
- 包含 When/What/Scope/Ownership/Impact

---

*最后更新: 2026-04-06*
