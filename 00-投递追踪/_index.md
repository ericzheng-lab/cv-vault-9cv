# 简历投递追踪仪表盘

## 统计概览

```dataviewjs
const records = dv.pages('"9_CV/00-投递追踪"').where(p => p.company);

// 统计各状态
dv.table(
  ["状态", "数量"],
  ["待响应", records.where(r => r.status == "待响应").length],
  ["面试中", records.where(r => r.status == "面试中").length],
  ["已拒绝", records.where(r => r.status == "已拒绝").length],
  ["录用", records.where(r => r.status == "录用").length]
);
```

## 最近投递

```dataview
TABLE company AS "公司", position AS "职位", date AS "日期", status AS "状态"
FROM "9_CV/00-投递追踪"
WHERE company
SORT date DESC
LIMIT 10
```

## 按渠道统计

```dataviewjs
const records = dv.pages('"9_CV/00-投递追踪"').where(p => p.company);
const channels = {};
records.forEach(r => {
  const ch = r.channel || "未知";
  channels[ch] = (channels[ch] || 0) + 1;
});

dv.table(
  ["渠道", "投递数"],
  Object.entries(channels).sort((a,b) => b[1] - a[1])
);
```

## 快速操作

- [新建投递记录](_template.md) ← 复制此模板
- [查看 MASTER 版本](../01-MASTER/)
- [查看历史版本](../02-历史版本/)

---

*最后更新：2026-03-24*
