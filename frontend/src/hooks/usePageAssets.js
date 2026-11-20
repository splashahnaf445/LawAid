import { useEffect } from "react";


export default function usePageAssets({ css = [], bodyClass = "" }) {
  const key = css.join("|");
  useEffect(() => {
    const links = css.map((href) => {
      const l = document.createElement("link");
      l.rel = "stylesheet";
      l.href = href;
      document.head.appendChild(l);
      return l;
    });
    const classes = bodyClass.split(" ").filter(Boolean);
    document.body.classList.add(...classes);
    return () => {
      links.forEach((l) => l.remove());
      document.body.classList.remove(...classes);
    };
    
  }, [key, bodyClass]);
}
