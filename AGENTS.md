# 运行环境与持久化

- 当前运行在 Linux 容器中。命令、路径、工具和 API 均按 Linux 环境选择。宿主机项目挂载为 `/workspace/<目录名>`，媒体挂载为 `/media/<目录名>`；`pwsh` 是 Linux PowerShell，不能使用 `cmd.exe`、`.bat`、`.cmd`、注册表或 Windows 专属 .NET API。
- 需要跨容器保留的容器专属数据使用现有 named volume：模型与下载缓存放 `/root/.cache`（`pi-cache`），仅 Linux 的 uv 环境和 workbench 数据放 `/data`（`pi-data`）。
- `/tmp` 只放一次性数据。项目源码、产物和媒体文件继续放宿主机 bind mount，不要移入 named volume；不要在宿主机仓库中创建或复用容器生成的 `.venv`。

# Git

- `gh` 已登录时，容器 entrypoint 会运行 `gh auth setup-git` 配置 HTTPS 凭据，并另外从 GitHub 账号补齐缺失的 `user.name` 和 `user.email`。正常情况下直接提交或推送；失败时再检查 `gh auth status` 和 `git config --global --list`。需要固定身份时，在启动前设置 `PI_GIT_NAME` 和 `PI_GIT_EMAIL`。
- GitHub issue 的标题和正文使用中文；commit message 使用英文。非琐碎提交必须包含正文，简要说明动机、关键决策和验证结果。使用 scope-based 的 conventional commit message 风格。

# 文档与项目

- 中文文档按自然段保存，一个段落保持一个逻辑行，由编辑器软换行。
- 不使用 emoji 或纯装饰性的 Unicode 符号；状态、箭头、破折号和省略号分别使用 `[x]`、`[ ]`、`ok`、`fail`、`->`、`-` 和 `...`。允许在目录树、层级图等结构化文本中使用 `├──`、`└──`、`│` 等 box-drawing 字符；正常中文标点和中文弯引号也不受此限制。
- 修改中文文本型文档后运行 `autocorrect --fix <文件>`；Markdown 文件随后运行 `uv run --script ~/.pi/agent/scripts/convert_chinese_quotes.py <文件>`，最后检查 diff。二进制文件不运行这些命令。
- 英文 skill 只作为内部工作指令；其生成或修改的用户文档默认使用中文。
- Python 项目统一使用 `uv`。一次性环境通过 `UV_PROJECT_ENVIRONMENT` 放在 `/tmp` 下的独立目录；需要跨容器保留的 Linux 环境放在 `/data` 下。