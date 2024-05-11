export const home_page = async (req, res) => {
    try {
        res.render("home-page", {
            layout: "layouts/main",
            title: "Usaha Mikro Kecil",
            script: "home-script.js",
            style: "home-style.css",
            message: "berhasil"
        });
    } catch (error) {
        console.error(error);
        res.status(error.status || 500).json({ error: error.message });
    }
};