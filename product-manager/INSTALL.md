# 安装、升级与调用确认

适用版本：v1.1.1｜核对日期：2026-10-01。

安装对象是**完整的 `product-manager/` 目录**。只复制 `SKILL.md` 会丢失引用的模板、模式和工具。

## 1. 准备条件

- 支持目录型 Skills，或能按需读取本地指令的 Agent 环境。
- 完整源码或发行 ZIP；克隆需要 Git。
- Python 3.10+ 用于包校验、离线测试和可选知识库工具；纯指令工作流不运行这些工具时无须 Python。
- 核心 Skill 不要求 API Key；浏览、仓库读取等能力由宿主的工具与权限决定。

```bash
git clone https://github.com/pylon12345/product-manager-os.git
cd product-manager-os
python product-manager/validate.py
```

输出 `OK` 表示包校验通过。发行 ZIP 解压后应看到 `product-manager/SKILL.md`，以下复制命令在其父目录执行。

## 2. Codex 用户级安装

当前官方本地发现目录为用户级 `~/.agents/skills` 和仓库级 `.agents/skills`，见 [OpenAI 官方 Build skills](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills)（核对日期：2026-10-01）。

### Windows PowerShell

在仓库根目录或发行包解压目录执行：

```powershell
$pmSkillsDir = Join-Path $env:USERPROFILE '.agents/skills'
$pmTargetDir = Join-Path $pmSkillsDir 'product-manager'
if (Test-Path -LiteralPath $pmTargetDir) {
    throw '同名 Skill 已存在，请先备份和比较。'
}
New-Item -ItemType Directory -Force -Path $pmSkillsDir | Out-Null
Copy-Item -LiteralPath './product-manager' -Destination $pmSkillsDir -Recurse
```

### macOS / Linux

```bash
pm_skills_dir="$HOME/.agents/skills"
mkdir -p "$pm_skills_dir"
if [ -e "$pm_skills_dir/product-manager" ]; then
  echo "同名 Skill 已存在，请先备份和比较。" >&2
  exit 1
fi
cp -R ./product-manager "$pm_skills_dir/"
```

部分既有环境仍在 `~/.codex/skills` 发现 Skill。如果当前环境已加载该目录，可更新原安装；不要为了迁移同时保留多个同名副本。新安装以官方当前目录与宿主实际设置为准。

## 3. Codex 项目级安装

团队随项目管理时，安装到：

```text
<project>/.agents/skills/product-manager/
```

Windows 示例：从下载仓库根目录，复制到一个**已确认的项目绝对路径**。

```powershell
$pmProjectRoot = 'C:/path/to/your-project'
if (-not (Test-Path -LiteralPath $pmProjectRoot -PathType Container)) {
    throw '请先替换为实际项目目录。'
}
$pmProjectSkills = Join-Path $pmProjectRoot '.agents/skills'
$pmProjectTarget = Join-Path $pmProjectSkills 'product-manager'
if (Test-Path -LiteralPath $pmProjectTarget) { throw '同名 Skill 已存在。' }
New-Item -ItemType Directory -Force -Path $pmProjectSkills | Out-Null
Copy-Item -LiteralPath './product-manager' -Destination $pmProjectSkills -Recurse
```

选择用户级或项目级中的适当范围。同名副本不会自动合并，排查时核对实际加载路径。

## 4. 确认加载与调用

Codex CLI／IDE 可用 `/skills` 查看，或用 `$` 选择；桌面环境按技能选择器操作，也可写“调用 product-manager”。显式调用与自动匹配规则见 [OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills#how-codex-uses-skills)。

```text
$product-manager 先评估这个需求是否值得做。
请说明你读取的 SKILL.md 路径和版本，区分事实与假设，给最小验证与下一动作。
项目和需求：……
```

确认实际读取路径与主文件 `v1.1.1` 标题，而非仅回复“已调用”。未显示时先新开任务，仍无变化则重启 Codex，并检查权限、重复安装或宿主禁用配置。

## 5. 其他 Agent

其他宿主支持目录型 Skill 时，按其官方发现位置安装完整文件夹；不支持自动发现时，在项目指令中引用 `product-manager/SKILL.md`，要求按 Router 加载相应 reference 和 template。

`agents/openai.yaml` 是 Codex 元数据。此仓库不声称已对 Claude Code、Cursor、Windsurf 等环境完成统一兼容性验收；工具、语法和发现规则需在目标环境确认。没有文件读取能力的对话环境无法直接运行完整包。

## 6. 从旧版升级

1. 记录当前加载路径与版本，备份原 Skill 目录，保留自定义模式、提示词和白名单。
2. 下载候选版本到独立目录，检查 [CHANGELOG](CHANGELOG.md)，运行包校验和离线测试。
3. 比较目录并保留定制，不混装旧入口与新引用。
4. 替换经过核验的完整目录；备份放在发现目录之外，避免重复加载。
5. 新任务确认路径与版本，执行一个熟悉的任务；需要回退时恢复完整旧目录。

v1.1.1 不迁移、清空或重抓包外知识库，不更新已有调度。移动安装目录后，维护者需核对调度中写死的脚本路径。安装备份与知识库备份是两件事。

升级前先核对目标、备份和定制，再替换；不要静默覆盖已有安装。

## 7. 安装后验证

从源码仓库根目录运行：

```bash
python product-manager/validate.py
python -m unittest discover -s product-manager/tests -p "test_*.py"
python -m unittest discover -s product-manager/tests/behavior -p "test_*.py"
python product-manager/tests/behavior/score.py --check
```

在 Skill 根目录运行时去掉 `product-manager/` 前缀。检查含义及模型评估方法见 [USER_GUIDE](USER_GUIDE.md)。

## 8. 故障排查

| 表现 | 检查与处理 |
|---|---|
| 找不到 Skill | 发现目录、权限、禁用配置；必要时重启 |
| 读取了旧版 | 核对实际路径，排查用户级／项目级同名副本 |
| 引用找不到 | 是否只复制入口，或丢失目录结构 |
| Python 找不到 | 安装 Python 3.10+；系统命令为 python3 时替换命令名 |
| 浏览或仓库访问被阻止 | 核对宿主权限，记录缺失证据，不编造结论 |
| 同步部分失败 | 查看 status；保留有效快照，不绕过访问限制 |
| 希望停止周期任务 | 停用外部调度；卸载 Skill 不等于取消调度 |
