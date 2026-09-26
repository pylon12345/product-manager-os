# 安装与调用

## Codex 全局安装（推荐）

将整个 `product-manager` 目录复制到 Codex skills 目录，保留内部相对路径。

### Windows PowerShell

```powershell
Copy-Item -LiteralPath ".\product-manager" -Destination "$env:USERPROFILE\.codex\skills\product-manager" -Recurse
```

### macOS / Linux

```bash
cp -R ./product-manager "${CODEX_HOME:-$HOME/.codex}/skills/product-manager"
```

若目标目录已存在，先比较版本和自定义内容；不要静默覆盖。安装后在新一轮 Codex 对话中可自动触发，或显式调用：

```text
$product-manager 先评估这个需求，不要直接写 PRD。
```

## Codex 项目级安装

需要项目隔离时复制到：

```text
<project>/.agents/skills/product-manager/
```

目录内必须保留 `SKILL.md`、`agents/`、`references/`、`templates/`、`knowledge/`、`workflows/` 与 `scripts/` 的相对关系。

本地知识库功能需 Python 3，使用标准库；安装 Skill 不会启动抓取任务。知识库数据应放在 Skill 目录外，由使用者显式指定；同步、备份、恢复及周期调度见 `references/knowledge-base-ops.md`。

## Claude Code 或其他 Agent

支持 Skill 目录时，把整个文件夹复制到对应的项目或全局 skills 目录。不支持自动发现时，在项目指令中引用 `product-manager/SKILL.md`，并要求按 Router 只加载当前任务所需的 reference 和 template。

## 验证

包内 `validate.py` 只读取本目录，检查入口、引用、术语库和正式版核心资产（含知识来源白名单）：

```bash
python validate.py
```

成功时输出 `OK`。不要一次性把整个 `knowledge/` 注入上下文。
