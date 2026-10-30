(function () {
    var content = document.querySelector('.item-page .content');
    var tocContainer = document.getElementById('article-toc');
    var tocNav = document.getElementById('article-toc-nav');
    var tocToggle = document.getElementById('toc-toggle');

    if (!content || !tocNav) {
        return;
    }

    var headings = content.querySelectorAll('h2, h3');
    var tocItems = [];

    headings.forEach(function (heading, index) {
        var text = heading.textContent.trim();
        if (!text || text.toLowerCase() === 'table of contents') {
            return;
        }

        if (!heading.id) {
            heading.id = 'section-' + index;
        }

        tocItems.push({
            id: heading.id,
            text: text,
            level: heading.tagName.toLowerCase()
        });
    });

    if (tocItems.length < 3) {
        if (tocContainer) {
            tocContainer.style.display = 'none';
        }
        if (tocToggle) {
            tocToggle.style.display = 'none';
        }
        return;
    }

    if (window.matchMedia('(max-width: 899px)').matches && tocNav) {
        tocNav.hidden = true;
    }

    var list = document.createElement('ul');

    tocItems.forEach(function (item) {
        var li = document.createElement('li');
        li.className = 'toc-' + item.level;

        var link = document.createElement('a');
        link.href = '#' + item.id;
        link.textContent = item.text;
        link.addEventListener('click', function (event) {
            event.preventDefault();
            var target = document.getElementById(item.id);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                history.replaceState(null, '', '#' + item.id);
            }
            if (tocToggle && window.matchMedia('(max-width: 899px)').matches) {
                tocNav.hidden = true;
                tocToggle.setAttribute('aria-expanded', 'false');
            }
        });

        li.appendChild(link);
        list.appendChild(li);
    });

    tocNav.appendChild(list);

    if (tocToggle) {
        tocToggle.addEventListener('click', function () {
            var expanded = tocToggle.getAttribute('aria-expanded') === 'true';
            tocNav.hidden = expanded;
            tocToggle.setAttribute('aria-expanded', expanded ? 'false' : 'true');
        });
    }

    var observer = new IntersectionObserver(
        function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var activeLink = tocNav.querySelector('a[href="#' + entry.target.id + '"]');
                    tocNav.querySelectorAll('a').forEach(function (link) {
                        link.classList.remove('active');
                    });
                    if (activeLink) {
                        activeLink.classList.add('active');
                    }
                }
            });
        },
        { rootMargin: '-20% 0px -70% 0px', threshold: 0 }
    );

    headings.forEach(function (heading) {
        if (heading.id) {
            observer.observe(heading);
        }
    });
})();
