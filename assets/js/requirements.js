      // Date
      const d = new Date();
      const ds = `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
      const todayDate = document.getElementById("todayDate");
      if (todayDate) todayDate.textContent = ds;
      const logDate = document.getElementById("logDate");
      if (logDate) logDate.textContent = ds;
      const logDate2 = document.getElementById("logDate2");
      if (logDate2) logDate2.textContent = ds;

      // Active TOC
      const links = document.querySelectorAll(".toc-link, .toc-section-link");
      const tocIds = [...links]
        .map((link) => link.getAttribute("href"))
        .filter((href) => href && href.startsWith("#"))
        .map((href) => href.slice(1));
      const sections = tocIds
        .map((id) => document.getElementById(id))
        .filter(Boolean);

      function updateTOC() {
        const scrollY = window.scrollY + 80;
        let current = "cover";
        sections.forEach((s) => {
          if (s.offsetTop <= scrollY) current = s.id;
        });
        links.forEach((l) => {
          const href = l.getAttribute("href").slice(1);
          l.classList.toggle("active", href === current);
        });
      }
      window.addEventListener("scroll", updateTOC, { passive: true });
      updateTOC();
