// 文章数据
let postsData = [];

// 加载文章列表
async function loadPostsList() {
    try {
        const response = await fetch('posts/index.json');
        postsData = await response.json();
        renderPosts(postsData);
        setupSearch();
    } catch (error) {
        console.error('加载文章列表失败:', error);
        document.getElementById('posts-list').innerHTML = '<p class="no-results">暂无文章</p>';
    }
}

// 渲染文章列表
function renderPosts(posts) {
    const container = document.getElementById('posts-list');

    if (posts.length === 0) {
        container.innerHTML = '<p class="no-results">没有找到匹配的文章</p>';
        return;
    }

    container.innerHTML = posts.map(post => `
        <div class="post-item">
            <h2><a href="post.html?slug=${post.slug}">${post.title}</a></h2>
            <div class="post-meta">${post.date}</div>
            <p class="post-excerpt">${post.excerpt}</p>
        </div>
    `).join('');
}

// 设置搜索功能
function setupSearch() {
    const searchInput = document.getElementById('search');
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();

        if (!query) {
            renderPosts(postsData);
            return;
        }

        const filtered = postsData.filter(post =>
            post.title.toLowerCase().includes(query) ||
            post.excerpt.toLowerCase().includes(query) ||
            (post.tags && post.tags.some(tag => tag.toLowerCase().includes(query)))
        );

        renderPosts(filtered);
    });
}

// 加载单篇文章
async function loadPost() {
    const params = new URLSearchParams(window.location.search);
    const slug = params.get('slug');

    if (!slug) {
        window.location.href = 'index.html';
        return; 
    }

    try {
        const response = await fetch(`posts/${slug}.md`);
        if (!response.ok) throw new Error('文章不存在');

        const markdown = await response.text();
        const { meta, content } = parseMarkdown(markdown);

        document.title = `${meta.title} - AI 产品思考`;

        const html = marked.parse(content);
        document.getElementById('post-content').innerHTML = `
            <h1>${meta.title}</h1>
            <div class="meta">${meta.date}</div>
            <div class="content">${html}</div>
        `;
    } catch (error) {
        console.error('加载文章失败:', error);
        document.getElementById('post-content').innerHTML = '<p>文章加载失败</p>';
    }
}

// 解析 Markdown 前置元数据
function parseMarkdown(text) {
    const lines = text.split('\n');
    let meta = { title: '无标题', date: '' };
    let contentStart = 0;

    if (lines[0] && lines[0].trim() === '---') {
        for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim() === '---') {
                contentStart = i + 1;
                break;
            }
            const match = lines[i].match(/^(\w+):\s*(.+)$/);
            if (match) {
                meta[match[1]] = match[2].replace(/^["']|["']$/g, '');
            }
        }
    }

    return {
        meta,
        content: lines.slice(contentStart).join('\n')
    };
}
