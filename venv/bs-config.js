module.exports = {
    proxy: "http://localhost:3000",  // Proxy the Flask app running on port 5000
    files: ["static/css/*.css", "templates/*.html"],  // Watch these directories for changes
    open: false,
    notify: false
};
