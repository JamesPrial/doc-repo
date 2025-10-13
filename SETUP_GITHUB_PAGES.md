# GitHub Pages Setup Guide

This guide will help you enable and test your new documentation website powered by Docsify.

## Quick Setup (5 minutes)

### Step 1: Push Changes to GitHub

```bash
git add docs/
git commit -m "feat: add GitHub Pages site with Docsify"
git push origin main
```

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub: https://github.com/jamesprial/doc-repo
2. Click **Settings** (top navigation)
3. Scroll down to **Pages** (left sidebar)
4. Under **Source**, select:
   - **Branch**: `main`
   - **Folder**: `/docs`
5. Click **Save**

GitHub will now build and deploy your site. This takes 1-2 minutes.

### Step 3: Access Your Site

Your site will be available at:
```
https://jamesprial.github.io/doc-repo/
```

You'll see a green banner in Settings → Pages with the URL once it's ready.

---

## Testing Locally (Optional)

To preview the site on your local machine before pushing:

### Option 1: Using Docsify CLI (Recommended)

```bash
# Install Docsify CLI globally
npm install -g docsify-cli

# Serve the site locally
docsify serve docs

# Open in browser: http://localhost:3000
```

### Option 2: Using Python HTTP Server

```bash
cd docs
python3 -m http.server 8000

# Open in browser: http://localhost:8000
```

### Option 3: Using Live Server (VS Code Extension)

1. Install "Live Server" extension in VS Code
2. Right-click `docs/index.html`
3. Select "Open with Live Server"

---

## What You Get

### Features
- **Homepage**: Clean landing page with download options
- **Navigation**: Sidebar with all Claude Code and Reddit API docs
- **Search**: Full-text search across all documentation
- **Responsive**: Works on mobile, tablet, and desktop
- **Code Highlighting**: Syntax highlighting for multiple languages
- **Copy Code**: One-click copy buttons on code blocks
- **Pagination**: Previous/Next buttons for easy navigation

### File Structure
```
docs/
├── index.html          # Docsify configuration
├── README.md           # Homepage content
├── _sidebar.md         # Left sidebar navigation
├── _navbar.md          # Top navigation bar
├── custom.css          # Custom styling
├── .nojekyll          # Tells GitHub Pages to skip Jekyll
├── claude/            # Symlink to ../claude/
└── reddit/            # Symlink to ../reddit/
```

---

## Customization Tips

### Update Repository URL
If your GitHub username or repo name is different, update these files:
- `docs/index.html` (line 14: `repo:` setting)
- `docs/README.md` (all GitHub URLs)
- `docs/_navbar.md` (GitHub link)

### Change Theme
Edit `docs/index.html` line 11 to use a different Docsify theme:
```html
<!-- Current: Vue theme -->
<link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/vue.css">

<!-- Other options: -->
<!-- <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/buble.css"> -->
<!-- <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/dark.css"> -->
<!-- <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/pure.css"> -->
```

### Modify Colors
Edit `docs/custom.css` to change the purple gradient colors:
```css
/* Find and replace #667eea and #764ba2 with your colors */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Add More Docs
To add a new documentation set:
1. Add the files to the repository
2. Create a symlink: `cd docs && ln -s ../newdocs newdocs`
3. Update `docs/_sidebar.md` to include links
4. Update `docs/_navbar.md` if needed

---

## Troubleshooting

### Site Not Loading After Enable
- Wait 2-3 minutes for GitHub to build the site
- Check the Actions tab for any build errors
- Verify `/docs` folder is selected as source

### Broken Links
- Ensure all markdown files use relative paths
- Check that symlinks are committed: `git ls-files -s docs/claude docs/reddit`
- Symlinks should show as mode `120000`

### Search Not Working
- Search only works after the site is fully loaded
- Try clearing browser cache
- Check browser console for JavaScript errors

### 404 Errors on Navigation
- Ensure `.nojekyll` file exists in `docs/`
- Verify file paths in `_sidebar.md` are correct
- Check that symlinks point to the right directories

---

## Advanced: Custom Domain (Optional)

To use a custom domain like `docs.yoursite.com`:

1. Add a `CNAME` file to `docs/`:
   ```bash
   echo "docs.yoursite.com" > docs/CNAME
   ```

2. Configure DNS with your domain provider:
   ```
   Type: CNAME
   Name: docs
   Value: jamesprial.github.io
   ```

3. Enable HTTPS in GitHub Settings → Pages

---

## Resources

- [Docsify Documentation](https://docsify.js.org/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Markdown Guide](https://www.markdownguide.org/)

---

## Support

If you encounter issues:
1. Check the [GitHub Pages status](https://www.githubstatus.com/)
2. Review the [Actions tab](https://github.com/jamesprial/doc-repo/actions) for errors
3. Open an issue in the repository

---

**Ready to go live?** Run the commands in Step 1 to push and enable GitHub Pages!
