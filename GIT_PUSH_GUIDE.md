# Git 推送操作指南

## 基本推送流程

### 1. 查看当前状态
```bash
git status
```
这会显示所有修改、新增和删除的文件。

### 2. 添加文件到暂存区
```bash
# 添加所有更改
git add -A

# 或者添加特定文件
git add <文件路径>

# 或者添加特定目录
git add <目录路径>
```

### 3. 提交更改
```bash
git commit -m "提交信息描述"
```

提交信息建议格式：
- 简短描述（50字符内）
- 空一行
- 详细说明（如果需要）

### 4. 推送到远程仓库
```bash
# 推送到main分支
git push

# 首次推送新分支
git push -u origin <分支名>

# 强制推送（谨慎使用）
git push -f
```

## 常见场景

### 场景1：提交所有更改并推送
```bash
git add -A
git commit -m "描述本次更改的内容"
git push
```

### 场景2：查看提交历史
```bash
# 查看最近5条提交
git log -5 --oneline

# 查看详细提交历史
git log
```

### 场景3：查看文件差异
```bash
# 查看未暂存的更改
git diff

# 查看已暂存的更改
git diff --cached

# 查看统计信息
git diff --stat
```

### 场景4：撤销操作
```bash
# 撤销工作区的修改（未add）
git restore <文件>

# 取消暂存（已add但未commit）
git restore --staged <文件>

# 修改最近一次提交信息
git commit --amend -m "新的提交信息"
```

## 推送大文件注意事项

当推送包含大量文件或大文件时：

1. **耐心等待**：推送可能需要几分钟甚至更长时间
2. **检查进度**：
   ```bash
   # 查看git push进程是否还在运行
   ps aux | grep "git push" | grep -v grep
   ```
3. **考虑使用 .gitignore**：排除不需要版本控制的文件
   - `results/` - 分析结果文件
   - `Intermediate/` - 中间临时文件
   - `*.pyc` - Python编译文件
   - `__pycache__/` - Python缓存目录

### 创建 .gitignore 文件
```bash
# 在项目根目录创建
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
.pytest_cache/

# 临时文件
Intermediate/

# 如果不想推送分析结果，取消下面的注释
# results/

# 环境变量
.env
*.env

# IDE
.vscode/
.idea/
*.swp
*.swo
EOF
```

## 分支管理

### 创建新分支
```bash
# 创建并切换到新分支
git checkout -b <新分支名>

# 推送新分支到远程
git push -u origin <新分支名>
```

### 切换分支
```bash
git checkout <分支名>
```

### 查看所有分支
```bash
# 本地分支
git branch

# 远程分支
git branch -r

# 所有分支
git branch -a
```

## 同步远程仓库

### 拉取最新代码
```bash
# 拉取并合并
git pull

# 仅拉取不合并
git fetch
```

## 常见问题排查

### 推送失败：远程有更新
```bash
# 先拉取远程更新
git pull

# 解决冲突后再推送
git push
```

### 推送超时
```bash
# 增加超时时间
git config --global http.postBuffer 524288000

# 使用SSH代替HTTPS（如果配置了SSH密钥）
git remote set-url origin git@github.com:用户名/仓库名.git
```

### 查看推送进度
```bash
# 使用verbose模式
git push -v
```

## 快速参考

| 命令 | 说明 |
|------|------|
| `git status` | 查看状态 |
| `git add -A` | 添加所有更改 |
| `git commit -m "msg"` | 提交 |
| `git push` | 推送 |
| `git pull` | 拉取 |
| `git log` | 查看历史 |
| `git diff` | 查看差异 |
| `git branch` | 查看分支 |

## 建议的工作流程

1. 开始工作前：`git pull` 拉取最新代码
2. 进行修改
3. 定期提交：`git add` + `git commit`
4. 工作结束后：`git push` 推送到远程
5. 重复以上流程
