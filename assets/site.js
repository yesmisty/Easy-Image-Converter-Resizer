
(function(){
  function updateThemeButton(btn){
    btn.textContent = document.body.classList.contains('dark') ? "☀️ Light Mode" : "🌙 Dark Mode";
  }
  document.addEventListener('DOMContentLoaded', function(){
    var btn = document.getElementById('theme-toggle');
    if(btn){
      btn.addEventListener('click', function(){
        document.body.classList.toggle('dark');
        updateThemeButton(btn);
      });
      updateThemeButton(btn);
    }
    var current = location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.header-nav a').forEach(function(a){
      var href = a.getAttribute('href');
      if(href === current || (href==='index.html' && (current===''||current==='index.html'))){
        a.style.fontWeight='700';
        a.style.textDecoration='underline';
      }
    });
  });
})();
