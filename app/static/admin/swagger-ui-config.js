const SWAGGER_THEME_KEY = 'swagger-ui-theme';

function applyTheme(theme) {
    const root = document.querySelector('.swagger-ui');
    if (!root) return;

    if (theme === 'dark') {
        root.classList.add('dark');
        document.body.style.backgroundColor = '#1b1b1b';
    } else {
        root.classList.remove('dark');
        document.body.style.backgroundColor = '#fff';
    }
}

function initThemeSwitcher() {
    const checkExist = setInterval(() => {
        const topbar = document.querySelector('.topbar-wrapper');
        if (topbar) {
            clearInterval(checkExist);

            const container = document.createElement('div');
            container.style.marginLeft = '20px';
            container.style.display = 'flex';
            container.style.alignItems = 'center';

            const button = document.createElement('button');
            const currentTheme = localStorage.getItem(SWAGGER_THEME_KEY) || 'light';

            button.innerText = currentTheme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
            button.className = 'btn';
            button.style.padding = '5px 15px';
            button.style.borderRadius = '20px';
            button.style.border = '1px solid #fff';
            button.style.background = 'transparent';
            button.style.color = '#fff';
            button.style.cursor = 'pointer';
            button.style.fontWeight = 'bold';

            button.onclick = () => {
                const theme = localStorage.getItem(SWAGGER_THEME_KEY) === 'dark' ? 'light' : 'dark';
                localStorage.setItem(SWAGGER_THEME_KEY, theme);
                button.innerText = theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
                applyTheme(theme);
            };

            container.appendChild(button);
            topbar.appendChild(container);

            // Initial apply
            applyTheme(currentTheme);

            // Re-apply on any DOM change inside swagger-ui
            const swaggerDiv = document.querySelector('#swagger-ui');
            if (swaggerDiv) {
                const observer = new MutationObserver(() => applyTheme(localStorage.getItem(SWAGGER_THEME_KEY) || 'light'));
                observer.observe(swaggerDiv, { childList: true });
            }
        }
    }, 100);
}

document.addEventListener('DOMContentLoaded', initThemeSwitcher);
