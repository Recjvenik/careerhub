/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./templates/**/*.html", "./**/templates/**/*.html", "./**/*.py"],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Outfit', 'Inter', 'sans-serif'],
                display: ['Outfit', 'sans-serif'],
                body: ['Inter', 'sans-serif'],
            },
            colors: {
                brand: {
                    50: '#f0fdfa',
                    100: '#ccfbf1',
                    200: '#99f6e4',
                    300: '#5eead4',
                    400: '#2dd4bf',
                    500: '#14b8a6', // Primary Brand Color (Teal/Indigo dependent) -> Let's go with a Modern Indigo/Violet mix as plan said "Indigo"
                    600: '#0d9488',
                    700: '#0f766e',
                    800: '#115e59',
                    900: '#134e4a',
                    950: '#042f2e',
                    // Re-defining specifically for "Refined Editorial"
                    primary: '#4F46E5', // Indigo 600
                    secondary: '#64748B', // Slate 500
                    accent: '#8B5CF6', // Violet 500
                    surface: '#F8FAFC', // Slate 50
                },
                dark: {
                    bg: '#0F172A', // Slate 900
                    surface: '#1E293B', // Slate 800
                }
            },
            animation: {
                'fade-in-up': 'fadeInUp 0.5s ease-out',
                'fade-in': 'fadeIn 0.3s ease-out',
                'scale-in': 'scaleIn 0.2s ease-out',
            },
            keyframes: {
                fadeInUp: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                scaleIn: {
                    '0%': { opacity: '0', transform: 'scale(0.95)' },
                    '100%': { opacity: '1', transform: 'scale(1)' },
                },
            }
        },
    },
    plugins: [],
}
