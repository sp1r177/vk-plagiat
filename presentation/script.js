// Инициализация ScrollReveal
ScrollReveal().reveal('.problem-card', {
    delay: 200,
    distance: '50px',
    origin: 'bottom',
    interval: 200
});

ScrollReveal().reveal('.competitor-card', {
    delay: 200,
    distance: '50px',
    origin: 'left',
    interval: 200
});

ScrollReveal().reveal('.audience-card', {
    delay: 200,
    distance: '50px',
    origin: 'bottom',
    interval: 200
});

ScrollReveal().reveal('.journey-step', {
    delay: 200,
    distance: '50px',
    origin: 'bottom',
    interval: 200
});

ScrollReveal().reveal('.feature-card', {
    delay: 200,
    distance: '50px',
    origin: 'bottom',
    interval: 200
});

ScrollReveal().reveal('.retention-card', {
    delay: 200,
    distance: '50px',
    origin: 'left',
    interval: 200
});

ScrollReveal().reveal('.pricing-card', {
    delay: 200,
    distance: '50px',
    origin: 'bottom',
    interval: 200
});

ScrollReveal().reveal('.roadmap-item', {
    delay: 200,
    distance: '50px',
    origin: 'left',
    interval: 200
});

// Плавная навигация
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Анимация статистики
function animateNumbers() {
    const stats = document.querySelectorAll('.stat-number');
    stats.forEach(stat => {
        const finalValue = stat.textContent;
        const isPercentage = finalValue.includes('%');
        const isNumber = finalValue.includes('x') || finalValue.includes('/');
        
        if (isPercentage) {
            const number = parseInt(finalValue);
            animateValue(stat, 0, number, 2000, '%');
        } else if (isNumber) {
            stat.style.opacity = '1';
        }
    });
}

function animateValue(element, start, end, duration, suffix = '') {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current) + suffix;
    }, 16);
}

// Запуск анимации при загрузке страницы
window.addEventListener('load', () => {
    setTimeout(animateNumbers, 1000);
});

// Интерактивные карточки
document.querySelectorAll('.problem-card, .audience-card, .feature-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-10px)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});

// Анимация цен
document.querySelectorAll('.pricing-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        if (!this.classList.contains('highlight')) {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        }
    });
    
    card.addEventListener('mouseleave', function() {
        if (!this.classList.contains('highlight')) {
            this.style.transform = 'translateY(0) scale(1)';
        }
    });
});

// Демо видео placeholder
document.querySelector('.video-placeholder').addEventListener('click', function() {
    // Здесь можно добавить открытие модального окна с видео
    alert('Демо-видео будет добавлено позже');
});

// Счетчик прокрутки для навигации
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-links a');
    
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (scrollY >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// Анимация появления элементов при скролле
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in-up');
        }
    });
}, observerOptions);

// Наблюдение за элементами
document.querySelectorAll('.problem-card, .audience-card, .feature-card, .pricing-card, .roadmap-item').forEach(el => {
    observer.observe(el);
});

// Параллакс эффект для hero секции
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    const rate = scrolled * -0.5;
    hero.style.transform = `translateY(${rate}px)`;
});

// Анимация мокапа приложения
function animateMockup() {
    const mockup = document.querySelector('.mockup-screen');
    mockup.style.opacity = '0';
    mockup.style.transform = 'translateY(50px)';
    
    setTimeout(() => {
        mockup.style.transition = 'all 1s ease';
        mockup.style.opacity = '1';
        mockup.style.transform = 'translateY(0)';
    }, 500);
}

// Запуск анимации мокапа
window.addEventListener('load', () => {
    setTimeout(animateMockup, 1000);
});

// Интерактивные кнопки
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
    });
    
    btn.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});

// Анимация иконок
document.querySelectorAll('.card-icon, .feature-icon, .audience-icon').forEach(icon => {
    icon.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.2) rotate(5deg)';
        this.style.transition = 'transform 0.3s ease';
    });
    
    icon.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1) rotate(0deg)';
    });
});

// Добавление активного класса для навигации
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', function() {
        document.querySelectorAll('.nav-links a').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
    });
});

// Анимация загрузки страницы
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});

// Добавление CSS для активного состояния навигации
const style = document.createElement('style');
style.textContent = `
    .nav-links a.active {
        color: #2563eb !important;
        font-weight: 600;
    }
    
    .loaded .hero-content {
        animation: fadeInUp 1s ease-out;
    }
    
    .loaded .hero-image {
        animation: fadeInUp 1s ease-out 0.3s both;
    }
`;
document.head.appendChild(style); 