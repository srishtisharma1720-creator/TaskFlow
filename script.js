
/* ==========================================
   TASKFLOW - THEME MANAGEMENT
   Dark Mode + Light Mode + Saved Preference
========================================== */

(function () {

    const THEME_KEY = "taskflow-theme";

    function applyTheme(theme) {

        const isDark = theme === "dark";

        // Update body theme
        document.body.classList.toggle("dark", isDark);

        // Update HTML theme marker
        document.documentElement.classList.toggle(
            "dark-theme",
            isDark
        );

        // Update theme button text
        const themeButton = document.querySelector(".theme-button");

        if (themeButton) {
            themeButton.textContent = isDark
                ? "☀️ Switch to Light Mode"
                : "🌙 Switch to Dark Mode";
        }

        // Save selected theme
        try {
            localStorage.setItem(THEME_KEY, theme);
        } catch (error) {
            console.warn("Unable to save theme preference.");
        }
    }

    // Restore saved theme. Dark is the default.
    let savedTheme = "dark";

    try {
        savedTheme = localStorage.getItem(THEME_KEY) || "dark";
    } catch (error) {
        console.warn("Unable to read theme preference.");
    }

    applyTheme(savedTheme);

    // Make function available to HTML onclick
    window.toggleTheme = function () {

        const currentlyDark =
            document.body.classList.contains("dark");

        applyTheme(currentlyDark ? "light" : "dark");

    };

})();
