# GitHub Pages 落地页

页面源码：`site/index.html`、`site/style.css` 和 `site/script.js`。纯静态页面，无需 Node 或后端。
部署工作流仅上传页面和两张品牌图片，不上传程序、数据库或其他文档。

## 发布

1. 将页面与 `.github/workflows/pages.yml` 提交并推送至 GitHub 的 `main`。
2. 仓库 Settings → Pages → Build and deployment → Source 选择 **GitHub Actions**。
3. 在 Actions 中手动运行 **Deploy landing page**（后续页面更新会自动运行）。
4. 部署成功后访问 `https://vinono.github.io/1D1T/`。

若账号配置了自定义 Pages 域名，以 Actions 的实际 `page_url` 为准。

## 本地预览

```sh
mkdir -p dist/pages/assets
cp site/index.html site/style.css site/script.js dist/pages/
cp assets/terminal-welcome-concept.png assets/1d1t-icon.png dist/pages/assets/
python3 -m http.server 8080 --bind 127.0.0.1 --directory dist/pages
```

访问 `http://127.0.0.1:8080`。

## 名称

- `1D1T`：对外品牌、仓库及页面名称。
- `1d1t`：用户输入的命令。
- `oneDayOneThing`：Python 内部包名。Python 的普通 `import` 语法要求标识符不能以数字开头，此名称满足该要求。
