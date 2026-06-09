// Load MathJax on pages where sphinx.ext.mathjax didn't inject it because all math
// is embedded inside raw HTML blocks (not RST math directives). Sphinx only adds
// MathJax to pages where it detects RST-level math; this covers the gap.
(function () {
    if (typeof window.MathJax !== 'undefined') { return; }
    window.MathJax = {
        tex: {
            inlineMath: [['\\(', '\\)']],
            displayMath: [['\\[', '\\]']]
        }
    };
    var s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js';
    s.async = true;
    document.head.appendChild(s);
}());
