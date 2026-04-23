# 简历定制工作流 - 使用指南

> 版本：v1.0 | 创建时间：2026-03-24

---

## 目录结构

```
9_CV/
├── 00-投递追踪/              # 投递记录 + Dataview 仪表盘
│   ├── _index.md             # 仪表盘（自动统计）
│   ├── _template.md          # 投递记录模板
│   └── YYYY-MM-DD-Company-Position.md  # 每次投递一个文件
│
├── 01-MASTER/                # 基准版本（只读）
│   ├── resume-master.html    # MASTER 简历（从 CV_inventory 复制）
│   └── cover-letter-master.html  # MASTER CL（从 CV_inventory 复制）
│
├── 02-历史版本/              # ✅ 已投递归档（JD + 生成内容合并）
│   └── {company}-{position}/
│       ├── JD.md             # JD 原文
│       ├── analysis.md       # 岗位分析
│       ├── resume.html       # 定制简历
│       ├── cover-letter.html # 定制求职信
│       └── resume.pdf        # 最终投递版
│
├── 03-生成中/                # 当前工作区
│   ├── _resume-template.html     # 简历模板（带编辑提示）
│   ├── _cover-letter-template.html  # CL 模板（带编辑提示）
│   └── {company}-{position}/     # 每次新建一个目录
│       ├── resume.html
│       ├── cover-letter.html
│       └── analysis.md           # 岗位分析
│
├── 04-经验库/                # CL 写作素材
│   └── _index.md             # 按主题分类的叙事素材
│
└── 05_JD/                    # ⚠️ 已废弃，内容合并到 02-历史版本/
```

---

## 工作流步骤

### Step 1: 创建投递记录

1. 复制 `00-投递追踪/_template.md`
2. 重命名为 `YYYY-MM-DD-Company-Position.md`
3. 填写 frontmatter（公司、职位、日期、渠道）
4. 粘贴 JD 原文到文件内

### Step 2: 分析岗位（我来做）

我会读取：
- MASTER 版本（锁定不可变区块）
- 历史版本库（找最相似的岗位类型）
- 经验库（准备 CL 素材）

输出 `analysis.md`：
- 岗位类型匹配（Agency/Tech/Film/Brand）
- 定制化策略（Summary 方向、删减建议、页数策略）
- CL 选材建议（从经验库选 2-3 个）

### Step 3: 生成初稿（我来做）

基于模板生成：
- `resume.html` — 修改可变区块
- `cover-letter.html` — 按策略选材写作

### Step 4: 协作迭代

1. 你查看 HTML 文件（用浏览器打开）
2. 批注修改意见（直接评论或口头说）
3. 我调整，循环直到定稿

### Step 5: 导出 PDF

**Resume：**
- 浏览器打开 `resume.html`
- 打印 → 另存为 PDF
- 检查页数（严格单页 / 弹性 1.2 页）

**Cover Letter：**
- 同上
- 确保单页（300-400 词）

### Step 6: 归档

1. 复制最终 PDF 到 `02-历史版本/{company}-{position}-{date}/`
2. 更新投递记录状态
3. 设置跟进提醒

---

## 快速参考

### 不可变区块（严格锁定）
- 个人信息（姓名/邮箱/地区/身份）
- 教育背景（学校/学位/年份）
- 工作日期 + 公司名 + 职位名

### 可变区块（根据岗位调整）
- Professional Summary（完全重写）
- Core Competencies（重新排序）
- 每个 bullet point 的描述（突出不同侧重点）
- Technical Skills（增减工具）

### 页数策略
| 场景 | 策略 |
|------|------|
| ATS 投递（Amazon/BBC） | 严格单页，删减早期经历 |
| 邮件直投（小公司） | 弹性 1.2 页，完整展示 |
| 面试携带 | 完整版 + 作品附录 |

### CL 写作策略
| JD 偏离 | 策略 |
|---------|------|
| 小 | 直接改写简历 bullets |
| 中 | 从经验库选 2-3 个，STAR 结构展开 |
| 大 | 深度重构，找可迁移技能 |

---

## 示例：完整流程

**场景**：看到 Netflix 的 Senior Producer 岗位

1. **你**：创建 `00-投递追踪/2026-03-24-Netflix-Senior-Producer.md`，粘贴 JD
2. **我**：分析 → Tech 类型，偏离中等，建议强调 Operations + Scale + Tools
3. **我**：生成 `03-生成中/Netflix-Senior-Producer/` 目录，包含 resume.html + cover-letter.html
4. **你**：浏览器打开查看，说"Summary 太 film-heavy，需要 more tech operations"
5. **我**：调整 Summary，增加 Jira/Asana 工具前置
6. **你**：确认 OK
7. **我**：导出 PDF，归档到 `02-历史版本/`
8. **你**：投递，更新状态为"待响应"

---

## 注意事项

- **不要直接修改 MASTER** — 总是复制到 `03-生成中/` 再改
- **保留所有历史版本** — 方便未来参考和复用
- **及时更新投递记录** — Dataview 仪表盘依赖这些文件
- **CL 保持单页** — Resume 可以弹性，CL 严格控制

---

*有问题随时问。开始用吧！*
