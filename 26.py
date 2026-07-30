mkdir my-first-git-project
cd my-first-git-project
git init                     # 初始化一个仓库
echo "Hello Git" > README.md
git add README.md
git commit -m "我的第一次提交"
git log                      # 查看提交历史