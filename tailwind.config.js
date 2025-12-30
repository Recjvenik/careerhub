/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./templates/**/*.html", "./**/templates/**/*.html"],
    theme: {
        extend: {
            colors: {
                'notebook-bg': '#fcfcfc',
                'notebook-text': '#333333',
            }
        },
    },
    plugins: [],
}
