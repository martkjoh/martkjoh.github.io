// Fills every element that has a data-include="path/to/file.html" attribute
// with the contents of that file.
document.querySelectorAll('[data-include]').forEach(async (el) => {
    const url = new URL(el.dataset.include, document.baseURI);
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(res.status);
        el.innerHTML = await res.text();
        // Render LaTeX in the new content. If MathJax hasn't loaded yet,
        // its first pass over the page will pick this up anyway.
        if (window.MathJax && MathJax.typesetPromise) {
            MathJax.startup.promise.then(() => MathJax.typesetPromise([el]));
        }
    } catch (err) {
        el.textContent = 'Could not load ' + el.dataset.include;
    }
});
