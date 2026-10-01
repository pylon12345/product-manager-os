# 安装、升级与调用确认

适用版本：v1.1.1｜核对日期：2026-10-02。

安装对象是**完整的 `product-manager/` 目录**。只复制 `SKILL.md` 会丢失引用的模板、模式和工具。

## 安装方式速查

| 使用环境 | 安装入口 | 调用方式 |
|---|---|---|
| Codex | 用户级或项目级 `.agents/skills/` | `$product-manager` 或技能选择器 |
| Claude Code | [个人或项目 `.claude/skills/`](#claude-code) | `/product-manager` |
| Claude 网页／桌面端 | [Customize → Skills 上传 ZIP](#claude) | 选择技能或自然语言指定 |
| WorkBuddy | [技能 → 添加技能 → 上传技能](#workbuddy) | 启用后自然语言指定 |

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

<a id="claude-code"></a>

## 5. Claude Code 安装

Claude Code 使用个人目录 `~/.claude/skills/product-manager/`，或项目目录 `<project>/.claude/skills/product-manager/`。安装后可直接用 `/product-manager` 调用，见 [Claude Code 官方 Skills 文档](https://code.claude.com/docs/en/skills)（核对日期：2026-10-02）。

### 个人安装：Windows PowerShell

在下载仓库根目录或技能 ZIP 解压后的父目录执行：

```powershell
$pmClaudeSkills = Join-Path $env:USERPROFILE '.claude/skills'
$pmClaudeTarget = Join-Path $pmClaudeSkills 'product-manager'
if (Test-Path -LiteralPath $pmClaudeTarget) {
    throw '同名 Skill 已存在，请先备份和比较。'
}
New-Item -ItemType Directory -Force -Path $pmClaudeSkills | Out-Null
Copy-Item -LiteralPath './product-manager' -Destination $pmClaudeSkills -Recurse
```

### 个人安装：macOS / Linux

```bash
pm_claude_skills="$HOME/.claude/skills"
mkdir -p "$pm_claude_skills"
if [ -e "$pm_claude_skills/product-manager" ]; then
  echo "同名 Skill 已存在，请先备份和比较。" >&2
  exit 1
fi
cp -R ./product-manager "$pm_claude_skills/"
```

### 项目安装

将完整 `product-manager/` 复制到目标项目的 `.claude/skills/` 下，最终入口是：

```text
<project>/.claude/skills/product-manager/SKILL.md
```

例如从下载仓库根目录向一个已确认的项目复制：

```powershell
$pmClaudeProject = 'C:/path/to/your-project'
if (-not (Test-Path -LiteralPath $pmClaudeProject -PathType Container)) {
    throw '请先替换为实际项目目录。'
}
$pmClaudeProjectSkills = Join-Path $pmClaudeProject '.claude/skills'
$pmClaudeProjectTarget = Join-Path $pmClaudeProjectSkills 'product-manager'
if (Test-Path -LiteralPath $pmClaudeProjectTarget) { throw '同名 Skill 已存在。' }
New-Item -ItemType Directory -Force -Path $pmClaudeProjectSkills | Out-Null
Copy-Item -LiteralPath './product-manager' -Destination $pmClaudeProjectSkills -Recurse
```

### 调用确认

在目标项目启动 Claude Code，查看 `/skills` 或输入 `/` 查找 `product-manager`，然后执行：

```text
/product-manager
评估一个电商售前与售后 AI 客服想法。
目前没有真实咨询数据，先给关键假设、最小验证与停止条件，不编造数据。
```

核对实际读取的入口路径、版本和相关 reference；若未出现，重开会话并检查完整目录、同名副本与禁用设置。

<a id="claude"></a>

## 6. Claude 网页／桌面端安装

Claude 账号内的自定义 Skill 通过 ZIP 上传，见 [Claude 官方使用说明](https://support.claude.com/en/articles/12512180-use-skills-in-claude)（核对日期：2026-10-02）。

1. 从 [Releases](https://github.com/pylon12345/product-manager-os/releases/tag/v1.1.1) 下载 `product-manager-v1.1.1.zip`。
2. 在 Claude 中确认已启用代码执行与文件创建能力；团队账号按组织策略启用 Skills。
3. 打开 **Customize → Skills**，选择 **+ → Create skill → Upload a skill**。
4. 上传技能 ZIP，在列表中启用 `product-manager`。
5. 新开对话，请求“使用 product-manager 技能评估这个产品想法”，检查是否加载相关指令。

不要直接上传 GitHub 的整个源码 ZIP。技能包的顶层目录应为 `product-manager/`，其中直接包含 `SKILL.md` 与配套目录，见 [Claude 官方打包要求](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)。

```text
product-manager-v1.1.1.zip
└─ product-manager/
   ├─ SKILL.md
   ├─ references/
   ├─ templates/
   ├─ workflows/
   ├─ knowledge/
   └─ scripts/
```

本地 Claude Code 个人目录与账号上传是不同安装入口；Cowork 使用账号启用的技能，不会直接读取本机个人技能目录，依据见 [Claude Code 官方说明](https://code.claude.com/docs/en/skills#use-skills-in-cowork-and-cloud-sessions)。

在 Claude 托管执行环境中，知识库数据目录也位于该环境，不能把本机路径视为可访问或永久保存。需要长期本地知识库时，使用已获授权的本地运行环境。

<a id="workbuddy"></a>

## 7. WorkBuddy 安装

WorkBuddy 的官方入口是 **技能 → 添加技能 → 上传技能**，导入后在 **已安装** 中管理启用状态，见 [WorkBuddy 官方技能说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)（核对日期：2026-10-02）。

1. 下载 [本仓库技能 ZIP](https://github.com/pylon12345/product-manager-os/releases/download/v1.1.1/product-manager-v1.1.1.zip)，保留完整包。
2. 在 WorkBuddy 打开技能页面，选择 **添加技能 → 上传技能**。
3. 拖入 ZIP 或点击 **选择文件** 导入；若客户端提示格式错误，先核对其当前文件类型要求和上面的包结构。
4. 在 **已安装** 中搜索 `product-manager`（显示名称也可能为 AI Product Manager OS），确认已启用。
5. 新建任务，用自然语言指定已安装技能：

```text
请使用已安装的 product-manager 技能。
我要设计电商售前与售后 AI 客服，目前没有真实咨询数据。
请先评估问题、首版范围与最小验证，区分事实与假设。
读取本技能相关 references 后再回答，本轮先不要修改项目文件。
```

确认任务记录中加载了本技能及相关参考；若列表中找不到，先检查导入结果和启用状态。需要读取项目时，在 WorkBuddy 中授权对应工作目录。

本说明采用官方文档明确给出的本地包导入入口；界面名称与文件格式要求以当前客户端为准。

## 8. 其他 Agent

其他宿主支持目录型 Skill 时，按其官方发现位置安装完整文件夹；不支持自动发现时，在项目指令中引用 `product-manager/SKILL.md`，要求按 Router 加载相应 reference 和 template。

`agents/openai.yaml` 是 Codex 展示元数据，不是其他宿主的安装入口。本轮依据官方资料核对安装方式与包结构，尚未在 Claude 或 WorkBuddy 账号中完成实际导入和任务验收；工具、权限、语言理解与结果质量仍需在目标环境验证。

## 9. 从旧版升级

1. 记录当前加载路径与版本，备份原 Skill 目录，保留自定义模式、提示词和白名单。
2. 下载候选版本到独立目录，检查 [CHANGELOG](CHANGELOG.md)，运行包校验和离线测试。
3. 比较目录并保留定制，不混装旧入口与新引用。
4. 替换经过核验的完整目录；备份放在发现目录之外，避免重复加载。
5. 新任务确认路径与版本，执行一个熟悉的任务；需要回退时恢复完整旧目录。

v1.1.1 不迁移、清空或重抓包外知识库，不更新已有调度。移动安装目录后，维护者需核对调度中写死的脚本路径。安装备份与知识库备份是两件事。

升级前先核对目标、备份和定制，再替换；不要静默覆盖已有安装。

## 10. 安装后验证

从源码仓库根目录运行：

```bash
python product-manager/validate.py
python -m unittest discover -s product-manager/tests -p "test_*.py"
python -m unittest discover -s product-manager/tests/behavior -p "test_*.py"
python product-manager/tests/behavior/score.py --check
```

在 Skill 根目录运行时去掉 `product-manager/` 前缀。检查含义及模型评估方法见 [USER_GUIDE](USER_GUIDE.md)。

## 11. 故障排查

| 表现 | 检查与处理 |
|---|---|
| 找不到 Skill | 发现目录、权限、禁用配置；必要时重启 |
| 读取了旧版 | 核对实际路径，排查用户级／项目级同名副本 |
| Claude 上传无技能入口 | 检查代码执行、组织 Skills 策略和账号权限 |
| Claude ZIP 上传失败 | 是否使用技能发行包，顶层目录与 name 是否一致 |
| WorkBuddy 已安装但未调用 | 检查启用开关，明确技能名称并检查加载记录 |
| 引用找不到 | 是否只复制入口，或丢失目录结构 |
| Python 找不到 | 安装 Python 3.10+；系统命令为 python3 时替换命令名 |
| 浏览或仓库访问被阻止 | 核对宿主权限，记录缺失证据，不编造结论 |
| 同步部分失败 | 查看 status；保留有效快照，不绕过访问限制 |
| 希望停止周期任务 | 停用外部调度；卸载 Skill 不等于取消调度 |

## 12. 官方来源与适用日期

新增 Claude、Claude Code 和 WorkBuddy 说明核对日期为 2026-10-02；Codex 说明沿用 2026-10-01 的已核对资料。入口随产品版本变化时，请以本节链接的官方资料与当前客户端为准。本次只更新安装文档，Skill 运行版本仍为 v1.1.1。
