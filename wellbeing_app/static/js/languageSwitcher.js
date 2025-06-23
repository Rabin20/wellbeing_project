class LanguageSwitcher {
    constructor() {
        this.initElements();
        this.bindEvents();
        this.checkSavedLanguage();
    }

    initElements() {
        this.languageButtons = document.querySelectorAll('.btn-lang');
        this.translatableElements = document.querySelectorAll('[data-translate]');
    }

    bindEvents() {
        this.languageButtons.forEach(btn => {
            btn.addEventListener('click', () => this.handleLanguageChange(btn.dataset.lang));
        });
    }

    async handleLanguageChange(lang) {
        this.updateActiveButton(lang);
        
        if (lang === 'mi') {
            await this.translatePage();
        }
        
        this.saveLanguagePreference(lang);
    }

    updateActiveButton(lang) {
        this.languageButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });
    }

    async translatePage() {
        const texts = Array.from(this.translatableElements).map(el => el.dataset.translate);
        
        try {
            const response = await this.fetchTranslations(texts, 'mi');
            this.applyTranslations(response.translations);
        } catch (error) {
            console.error("Translation error:", error);
        }
    }

    async fetchTranslations(texts, targetLang) {
        const csrfToken = this.getCSRFToken();
        const response = await fetch('/translate_bulk/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                texts: texts,
                target_lang: targetLang
            })
        });
        return await response.json();
    }

    applyTranslations(translations) {
        this.translatableElements.forEach((el, index) => {
            if (translations[index]) {
                el.textContent = translations[index];
            }
        });
    }

    async saveLanguagePreference(lang) {
        const csrfToken = this.getCSRFToken();
        await fetch('/set_language_ajax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({language: lang})
        });
    }

    checkSavedLanguage() {
        const langCookie = document.cookie.split('; ')
            .find(row => row.startsWith('django_language'));
        if (langCookie) {
            const lang = langCookie.split('=')[1];
            const activeBtn = document.querySelector(`.btn-lang[data-lang="${lang}"]`);
            if (activeBtn) activeBtn.classList.add('active');
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LanguageSwitcher();
});