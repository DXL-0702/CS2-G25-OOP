# 项目协作流程规范

> 本项目为 JC1503 OOP 五人小组项目，统一使用 GitHub Fork + Issue + Pull Request 工作流。
> 除我以外，组员均使用 Windows 电脑，终端统一按 **Windows cmd / Command Prompt** 编写命令。
> 所有成员必须严格遵循此流程，以保证代码质量、协作效率和最终提交稳定性。

---

## 0. 重要说明：本文命令全部适配 Windows cmd

本文所有终端命令默认在 **Windows cmd** 中执行，不是 macOS/Linux 终端，也不是 Git Bash。

如果使用 VS Code：

1. 打开 VS Code 终端。
2. 点击终端右上角下拉菜单。
3. 选择 **Command Prompt** 或 **cmd**。
4. 不要选择 Git Bash，避免命令格式不一致。

命令复制注意事项：

- 不要复制提示符，例如 `C:\Users\xxx>`。
- 代码块中的 `YOUR_GITHUB_USERNAME` 需要替换成自己的 GitHub 用户名。
- 代码块中的 `issue-5-account-model` 是示例分支名，实际按自己的 issue 编号修改。
- 如果路径中有空格，必须使用英文双引号包起来。
- 本文统一使用 `main` 作为默认分支名；如果 GitHub 仓库默认分支是 `master`，则把命令中的 `main` 全部替换为 `master`。

---

## 1. 仓库结构

```text
上游仓库:  https://github.com/DXL-0702/CS2-G25-OOP
forked 仓库（每个组员自己的 GitHub 账号下）:  https://github.com/YOUR_GITHUB_USERNAME/CS2-G25-OOP
本地工作目录（推荐）:  C:\Users\YOUR_WINDOWS_USERNAME\projects\CS2-G25-OOP
```

解释：

- **上游仓库 upstream**：原始项目仓库，由 DXL-0702 维护。
- **个人 fork origin**：每个组员复制到自己 GitHub 账号下的仓库。
- **本地仓库 local**：组员电脑上的代码目录。

---

## 2. 整体工作流程概览

```text
发现问题 / 分配任务
        │
        ▼
创建 Issue（问题或任务）
        │
        ▼
Fork 上游仓库到个人 GitHub 账号
        │
        ▼
Clone 个人 fork 到本地电脑
        │
        ▼
关联上游仓库 upstream
        │
        ▼
同步 upstream/main 最新代码
        │
        ▼
创建功能分支（推荐）
        │
        ▼
本地开发、测试、提交 commit
        │
        ▼
推送分支到个人 fork
        │
        ▼
发起 Pull Request（PR）
        │
        ▼
其他成员或 DXL-0702 Code Review
        │
        ▼
Review 通过后合并到上游 main 分支
```

---

## 3. 组员首次配置（每个组员只做一次）

### 3.1 安装并检查 Git

组员需要先安装 Git for Windows。

安装完成后，打开 cmd，执行：

```cmd
git --version
```

如果能看到类似下面的输出，说明 Git 已安装成功：

```text
git version 2.xx.x.windows.x
```

### 3.2 Fork 上游仓库

在浏览器中打开上游仓库：

```text
https://github.com/DXL-0702/CS2-G25-OOP
```

然后点击右上角 **Fork**，把仓库复制到自己的 GitHub 账号下。

Fork 后，每个组员会得到自己的仓库：

```text
https://github.com/YOUR_GITHUB_USERNAME/CS2-G25-OOP
```

### 3.3 Clone 自己的 fork 到本地

打开 Windows cmd，执行：

```cmd
REM 创建本地 projects 文件夹；如果已经存在，不会重复创建
if not exist "%USERPROFILE%\projects" mkdir "%USERPROFILE%\projects"

REM 进入 projects 文件夹
cd /d "%USERPROFILE%\projects"

REM 克隆自己的 fork；把 YOUR_GITHUB_USERNAME 替换成自己的 GitHub 用户名
git clone https://github.com/YOUR_GITHUB_USERNAME/CS2-G25-OOP.git

REM 进入项目目录
cd CS2-G25-OOP
```

### 3.4 添加上游仓库 upstream

在项目目录中执行：

```cmd
REM 添加上游仓库；只需要执行一次
git remote add upstream https://github.com/DXL-0702/CS2-G25-OOP.git

REM 查看远程仓库配置
git remote -v
```

正确结果应类似：

```text
origin    https://github.com/YOUR_GITHUB_USERNAME/CS2-G25-OOP.git (fetch)
origin    https://github.com/YOUR_GITHUB_USERNAME/CS2-G25-OOP.git (push)
upstream  https://github.com/DXL-0702/CS2-G25-OOP.git (fetch)
upstream  https://github.com/DXL-0702/CS2-G25-OOP.git (push)
```

如果执行 `git remote add upstream ...` 时提示 upstream 已存在，执行下面命令修正即可：

```cmd
git remote set-url upstream https://github.com/DXL-0702/CS2-G25-OOP.git
git remote -v
```

### 3.5 配置 Git 用户信息

首次使用 Git 的组员需要配置自己的名字和邮箱：

```cmd
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

检查配置：

```cmd
git config --global user.name
git config --global user.email
```

---

## 4. 日常开发流程（每次开始新任务都按这个流程）

### 4.1 在 GitHub 上创建 Issue

在上游仓库的 **Issues** 页面点击 **New issue**，填写：

- **Title**：简洁描述问题或任务，例如 `实现 Account 模型类` 或 `修复余额计算精度`。
- **Labels**：选择合适标签，例如 `enhancement`、`bug`、`documentation`、`test`。
- **Assignees**：指定负责的组员（这个我来看看）。
- **Projects**：如果使用项目面板，则关联到对应项目。

建议 issue 标题加上阶段编号：

```text
[Phase 1] 实现 Account 模型类
[Phase 2] 实现 Stack 数据结构
[Phase 4] 实现区块链式审计日志
```

### 4.2 每次开发前同步上游最新代码

每次开始任务前，必须先让自己的本地 `main` 与上游仓库同步。

```cmd
REM 切换到 main 分支
git checkout main

REM 拉取上游仓库信息
git fetch upstream

REM 把上游 main 合并到本地 main
git merge upstream/main

REM 把同步后的 main 推送到自己的 fork
git push origin main
```

如果仓库默认分支叫 `master`，则使用：

```cmd
git checkout master
git fetch upstream
git merge upstream/master
git push origin master
```

### 4.3 创建功能分支（推荐）

推荐每个 issue 使用一个单独分支，命名方式：

```text
issue-编号-简短英文描述
```

示例：处理 issue #5，实现 Account 模型类：

```cmd
git checkout -b issue-5-account-model
```

说明：

- 推荐使用功能分支，方便 PR、review 和回滚。
- 如果组员确实不熟悉分支，可以在自己 fork 的 `main` 或 `master` 上完成简单改动后提交 PR，但一次只能处理一个 issue。
- 禁止直接向上游仓库 `DXL-0702/CS2-G25-OOP` 的 `main` 推送代码。

### 4.4 本地开发后查看改动

开发完成后，先查看当前改动：

```cmd
git status
```

查看最近提交记录：

```cmd
git log --oneline -5
```

### 4.5 添加文件并提交 commit

推荐使用简单、清晰的一行 commit message。详细说明写在 PR 描述里，不强制写多行 commit。

```cmd
REM 添加所有改动文件
git add .

REM 提交改动
git commit -m "feat(models): 实现 Account 模型类"
```

常用 commit 类型：

| 类型 | 使用场景 | 示例 |
|---|---|---|
| `feat` | 新增功能 | `feat(models): 实现 Account 类` |
| `fix` | 修复 bug | `fix(storage): 修复 JSON 加载错误` |
| `refactor` | 重构代码，不改变功能 | `refactor(cli): 简化菜单结构` |
| `test` | 添加或修改测试 | `test(models): 添加 Account 测试` |
| `docs` | 修改文档 | `docs(progress): 更新协作流程` |
| `chore` | 配置、依赖、杂项 | `chore: 添加 requirements.txt` |

如果想补充更多说明，可以使用两个 `-m`：

```cmd
git commit -m "feat(models): 实现 Account 模型类" -m "关联 issue #5，新增 deposit 和 withdraw 方法。"
```

### 4.6 推送分支到个人 fork

如果使用功能分支，例如 `issue-5-account-model`：

```cmd
git push -u origin issue-5-account-model
```

如果使用自己 fork 的 `main` 分支：

```cmd
git push origin main
```

如果使用自己 fork 的 `master` 分支：

```cmd
git push origin master
```

### 4.7 发起 Pull Request

1. 浏览器打开自己的 fork 仓库：

   ```text
   https://github.com/YOUR_GITHUB_USERNAME/CS2-G25-OOP
   ```

2. GitHub 通常会自动提示 **Compare & pull request**，点击它。
3. 确认 PR 方向：

   ```text
   base repository: DXL-0702/CS2-G25-OOP
   base branch: main
   head repository: YOUR_GITHUB_USERNAME/CS2-G25-OOP
   compare branch: issue-5-account-model
   ```

4. 填写 PR 信息：
   - **Title**：例如 `feat(models): 实现 Account 模型类 closes #5`
   - **Description**：说明改了什么、如何测试、是否影响其他模块。
   - **Reviewers**：指定 DXL-0702 或其他需要 review 的成员。
   - **Labels**：添加相关标签。
   - **Development**：关联对应 issue，例如 `Closes #5`。
5. 点击 **Create pull request**。

### 4.8 Code Review 与修改

Review 流程：

- Reviewer 在 GitHub PR 页面查看代码。
- Reviewer 可以评论、要求修改或批准。
- 如果需要修改，开发者在本地原分支继续改，不需要重新开 PR。
- 修改后再次提交并 push，PR 会自动更新。

根据 review 修改后的 cmd 命令示例：

```cmd
git status
git add .
git commit -m "fix(models): 根据 review 调整 Account 校验逻辑"
git push
```

Review 通过后，由我在 GitHub 上点击 **Merge pull request** 合并到上游 `main`。

### 4.9 PR 合并后清理本地分支

PR 合并后，组员本地可以清理已完成分支：

```cmd
REM 切回 main
git checkout main

REM 同步上游最新 main
git fetch upstream
git merge upstream/main

REM 更新自己的 fork main
git push origin main

REM 删除本地功能分支
git branch -d issue-5-account-model

REM 可选：删除自己 fork 上的远程功能分支
git push origin --delete issue-5-account-model
```

如果你使用的是 `master` 分支，把上面所有 `main` 替换成 `master`。

---

## 5. 冲突处理

### 5.1 本地同步时出现冲突

当执行 `git merge upstream/main` 后出现冲突，cmd 会提示有文件冲突。

处理步骤：

1. 执行 `git status` 查看冲突文件。
2. 用 VS Code 打开冲突文件。
3. 找到类似下面的标记：

```text
<<<<<<< HEAD
你的本地代码
=======
上游 main 的代码
>>>>>>> upstream/main
```

4. 手动决定保留哪部分代码，删除 `<<<<<<<`、`=======`、`>>>>>>>` 这些标记。
5. 保存文件。
6. 回到 cmd，执行：

```cmd
git status
git add .
git commit -m "merge: 解决与 upstream/main 的冲突"
git push origin main
```

### 5.2 PR 页面提示有冲突

如果 GitHub PR 页面显示 `This branch has conflicts that must be resolved`，在本地执行：

```cmd
REM 切换到自己的功能分支
git checkout issue-5-account-model

REM 获取上游最新代码
git fetch upstream

REM 合并上游 main
git merge upstream/main
```

如果出现冲突，按 5.1 的方法手动解决。解决完成后：

```cmd
git add .
git commit -m "merge: 解决 PR 与 upstream/main 的冲突"
git push
```

PR 页面会自动更新。

---

## 6. 分支管理规范

| 分支 | 用途 | 谁可以操作 | 说明 |
|---|---|---|---|
| 上游 `main` | 稳定可运行代码 | 只由我合并 PR | 禁止组员直接 push |
| 个人 fork 的 `main` / `master` | 组员自己的默认分支 | 组员本人 | 可用于同步上游；简单任务可用，但不推荐直接开发 |
| `issue-编号-描述` | 单个 issue 的开发分支 | 组员本人 | 推荐方式，便于 PR 和 review |

规则：

- 禁止直接向上游仓库 `DXL-0702/CS2-G25-OOP` 的 `main` 推送代码。
- 推荐一个 issue 对应一个分支。
- 推荐一个 PR 只解决一个 issue。
- 不要在一个 PR 中混入多个不相关功能。
- 功能分支合并后可以删除，保持仓库干净。

---

## 7. Commit 提交规范

### 7.1 提交时机

- 每完成一个独立的小功能或修复，就提交一次。
- 不要等到全部写完才一次性提交大量改动。
- 每次提交应尽量能说明一个明确目的。

### 7.2 简化版提交格式

对本项目组员，推荐使用简化格式：

```text
类型(模块): 简短描述
```

示例：

```text
feat(models): 新增 Transaction 基类
fix(storage): 修复读取空 JSON 文件时报错
refactor(cli): 简化账户菜单流程
test(audit): 添加审计链完整性测试
docs(progress): 更新 Windows cmd 协作流程
```

### 7.3 可选：共同作者标记

如果某个 commit 是两个人一起完成的，可以在 PR 描述中写清楚共同贡献。commit 中不强制写 `Co-Authored-By`，避免格式复杂。

---

## 8. Issue 写作规范

### 8.1 创建 issue 的时机

- 发现 bug 或功能缺陷时。
- 接到新的开发任务时。
- 有疑问或需要讨论设计问题时。
- 任务完成后发现新的后续问题时。

### 8.2 Issue 模板

建议 issue 内容按下面结构填写：

```markdown
## 问题或任务描述
[清晰描述需要做什么或发生了什么问题]

## 复现步骤（Bug 必填）
1.
2.
3.

## 预期行为
[描述期望的结果]

## 实际行为
[描述实际发生的情况]

## 负责人员
@组员用户名

## 相关文件
[列出涉及的文件或模块]

## 备注
[任何其他相关信息]
```

---

## 9. PR 写作规范

### 9.1 PR 描述模板

```markdown
## 改动概述
[一句话描述这个 PR 做什么]

## 改动详情
- [改动点 1]
- [改动点 2]

## 影响范围
[这个改动会影响哪些模块，是否需要其他成员注意]

## 测试情况
- [ ] 已运行 `python -m pytest`，全部通过
- [ ] 新增或更新了相关测试

## 关联 Issue
Closes #编号
```

### 9.2 提交 PR 前自检清单

- [ ] 代码可以正常运行。
- [ ] 已在 Windows cmd 中运行过相关命令。
- [ ] 已运行 `python -m pytest`，并确认测试通过。
- [ ] 没有遗留无意义的调试输出。
- [ ] 提交信息能看出本次改动目的。
- [ ] 已同步上游最新 `main` 或 `master`。
- [ ] PR 只对应一个 issue 或一个明确任务。

---

## 10. Windows 环境配置与依赖管理

### 10.1 检查 Python 版本

项目统一使用 **Python 3.10+**。

在 Windows cmd 中执行：

```cmd
python --version
```

如果 `python` 命令无效，尝试：

```cmd
py -3 --version
```

如果两个命令都无效，需要先安装 Python，并在安装时勾选 **Add Python to PATH**。

### 10.2 创建并激活虚拟环境

进入项目目录后执行：

```cmd
REM 创建虚拟环境
python -m venv venv

REM 激活虚拟环境
venv\Scripts\activate.bat
```

激活成功后，cmd 前面通常会出现：

```text
(venv) C:\Users\xxx\projects\CS2-G25-OOP>
```

如果 `python -m venv venv` 失败，可以尝试：

```cmd
py -3 -m venv venv
venv\Scripts\activate.bat
```

### 10.3 安装依赖

```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 10.4 运行测试

```cmd
python -m pytest
```

### 10.5 运行程序

```cmd
python main.py
```

如果项目入口后续调整，以 README 或 issue 中说明为准。

### 10.6 退出虚拟环境

```cmd
deactivate
```

### 10.7 requirements.txt 规范

```text
pytest>=7.0.0
```

可选工具暂时不强制，避免增加组员环境配置难度。

---

## 11. 我的职责

我除开发外，还承担以下职责：

1. **维护上游仓库**：确保上游 `main` 分支始终处于可运行状态。
2. **创建和分配 Issue**：根据项目阶段和成员能力拆分任务。
3. **审核 PR**：检查代码质量、功能完整性、是否影响其他模块。
4. **协助解决冲突**：当 PR 出现冲突时，帮助组员定位和处理。
5. **控制开发范围**：避免项目偏离 OOP 作业要求或过度复杂化。
6. **发布阶段版本**：在重要阶段完成后，打 tag 或整理 release。

---

## 12. 组员协作礼仪

- **开始任务前先看 issue**：明确自己负责什么，不要随意修改无关文件。
- **开发前先同步上游**：减少冲突。
- **PR 尽量小而清楚**：一个 PR 解决一个问题。
- **及时响应 review**：被要求修改后尽快处理。
- **遇到问题及时说明**：不要卡住很久不沟通。
- **不要覆盖别人的代码**：不确定时先在 issue 或群里问。
- **记录重要决定**：设计变化、功能取舍要写在 issue 或 PR 描述中。

---

## 13. Windows cmd 快速命令卡

### 13.1 首次配置

```cmd
if not exist "%USERPROFILE%\projects" mkdir "%USERPROFILE%\projects"
cd /d "%USERPROFILE%\projects"
git clone https://github.com/YOUR_GITHUB_USERNAME/CS2-G25-OOP.git
cd CS2-G25-OOP
git remote add upstream https://github.com/DXL-0702/CS2-G25-OOP.git
git remote -v
```

### 13.2 每次开始新任务

```cmd
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
git checkout -b issue-5-account-model
```

### 13.3 开发过程中提交

```cmd
git status
git add .
git commit -m "feat(models): 实现 Account 模型类"
git push -u origin issue-5-account-model
```

之后同一个分支继续 push 时，只需要：

```cmd
git push
```

### 13.4 PR 合并后清理

```cmd
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
git branch -d issue-5-account-model
git push origin --delete issue-5-account-model
```

### 13.5 查看状态

```cmd
git status
git remote -v
git branch -a
git log --oneline -10
```

### 13.6 Python 环境

```cmd
python --version
python -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m pytest
python main.py
```

---

## 14. 常见问题 FAQ

### Q1：我输入 `git remote add upstream ...` 后提示 upstream 已存在，怎么办？

执行：

```cmd
git remote set-url upstream https://github.com/DXL-0702/CS2-G25-OOP.git
git remote -v
```

### Q2：我的 fork 落后上游很多，怎么同步？

推荐使用安全同步方式：

```cmd
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

如果出现冲突，按第 5 节处理。不要随意使用 `reset --hard` 或 `--force`，避免误删自己的代码。

### Q3：一个分支可以同时处理两个 issue 吗？

不推荐。最好一个 issue 一个分支，一个 PR 一个任务。这样 review 更简单，也更容易定位问题。

### Q4：我不小心在自己 fork 的 main 上开发了，怎么办？

如果只是一个小任务，可以直接从自己的 `main` 向上游 `main` 提 PR。之后完成任务后，尽快同步上游并回到规范流程。

如果改动很多，建议先创建新分支保存当前内容：

```cmd
git checkout -b issue-5-account-model
git push -u origin issue-5-account-model
```

然后用这个分支发起 PR。

### Q5：PR 被要求修改，应该重新开 PR 吗？

不需要。继续在原来的分支修改、commit、push 即可，原 PR 会自动更新。

```cmd
git status
git add .
git commit -m "fix: 根据 review 修改问题"
git push
```

### Q6：运行 `python` 提示不是内部或外部命令怎么办？

先尝试：

```cmd
py -3 --version
```

如果可用，则把文档中的 `python` 临时替换为 `py -3` 使用。例如：

```cmd
py -3 -m pytest
py -3 main.py
```

如果 `py -3` 也不可用，需要重新安装 Python，并勾选 **Add Python to PATH**。

### Q7：测试失败了怎么办？

先在本地运行：

```cmd
python -m pytest
```

根据报错定位问题，修复后重新提交。不要在测试明显失败的状态下请求合并 PR。

### Q8：我不知道当前在哪个分支，怎么办？

执行：

```cmd
git branch
```

带 `*` 的就是当前分支。

### Q9：我不知道当前代码有没有改动，怎么办？

执行：

```cmd
git status
```

如果显示 `nothing to commit, working tree clean`，说明当前没有未提交改动。
